"""Decode data returned by public tools, without evaluating Python expressions."""

import ast
import io
import json
import re
import tokenize
from dataclasses import fields, is_dataclass
from enum import Enum


class PublicDataError(ValueError):
    """The available receipt does not support the requested transformation."""


RECORDS = {"Contact", "Ride", "Email", "ReturnedEmails", "Conversation", "ConversationV2",
           "Message", "MessageV2", "CrimeDataPoint"}


def _literal(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        if any(key is None for key in node.keys):
            raise PublicDataError("Expanded mappings are not public literals")
        return {_literal(key): _literal(value) for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _literal(node.operand)
        if type(value) not in (int, float):
            raise PublicDataError("Non-numeric unary expression")
        return -value if isinstance(node.op, ast.USub) else value
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in RECORDS and not node.args
            and all(item.arg is not None for item in node.keywords)):
        return {item.arg: _literal(item.value) for item in node.keywords}
    raise PublicDataError("Only literal values and known public record representations are supported")


def _normalize(value):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _normalize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_normalize(item) for item in value]
    return value


def public_data(value):
    """Normalize a returned value; never read the app that produced it."""
    if not isinstance(value, str):
        return _normalize(value)
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        pass
    # ARE's dataclass repr includes these enum literals. Replace only the declared
    # literal representation, then parse the remainder with the restricted walker.
    try:
        # Preserve text that happens to contain an enum repr inside a string field.
        offsets, current = [], 0
        for line in value.splitlines(keepends=True):
            offsets.append(current)
            current += len(line)
        strings = [(offsets[token.start[0] - 1] + token.start[1],
                    offsets[token.end[0] - 1] + token.end[1])
                   for token in tokenize.generate_tokens(io.StringIO(value).readline)
                   if token.type == tokenize.STRING]
        text = re.sub(r"<(?:Gender|Status)\.[A-Z_]+: ('[^'\n]*'|\"[^\"\n]*\")>",
                      lambda match: match[0] if any(start <= match.start() < end
                                                   for start, end in strings) else match[1], value)
        return _literal(ast.parse(text, mode="eval").body)
    except (SyntaxError, ValueError, TypeError, RecursionError, tokenize.TokenError):
        raise PublicDataError("Tool result is not a supported structured public receipt") from None


def require_record(value, fields_required):
    if not isinstance(value, dict) or not set(fields_required) <= value.keys():
        raise PublicDataError(f"Public record is missing required fields: {sorted(fields_required)}")
    return value


def paged_records(call, tool, *, kind, arguments=None):
    """Follow native range receipts. Reject partial, inconsistent, or stalled pages."""
    offset, expected_total = 0, None
    seen = set()
    while True:
        args = {**(arguments or {}), "offset": offset}
        if kind in {"emails", "rides"}:
            args["limit"] = 5
        data = public_data(call(tool, args))
        if kind == "emails":
            require_record(data, {"emails", "emails_range", "total_emails"})
            batch, bounds, total = data["emails"], data["emails_range"], data["total_emails"]
        else:
            require_record(data, {kind})
            meta = data.get("metadata", data)
            require_record(meta, {"range", "total"})
            batch, bounds, total = data[kind], meta["range"], meta["total"]
        if (type(total) is not int or total < 0 or not isinstance(bounds, list)
                or len(bounds) != 2 or any(type(n) is not int for n in bounds)
                or bounds[0] != offset or not offset <= bounds[1] <= total):
            raise PublicDataError("Invalid native pagination receipt")
        if expected_total is not None and total != expected_total:
            raise PublicDataError("Population changed during enumeration; no complete snapshot is claimed")
        expected_total = total
        if not isinstance(batch, (list, dict)) or len(batch) != bounds[1] - offset:
            raise PublicDataError("Page contents disagree with their native range")
        if isinstance(batch, dict):
            try:
                indexed = {int(key): row for key, row in batch.items()}
            except (ValueError, TypeError):
                raise PublicDataError("Ride page contains non-index keys") from None
            if set(indexed) != set(range(offset, bounds[1])):
                raise PublicDataError("Ride indexes disagree with their native range")
            yield from sorted(indexed.items())
        else:
            id_field = {"contacts": "contact_id", "emails": "email_id"}.get(kind)
            for record in batch:
                if isinstance(record, dict) and id_field in record:
                    identifier = record[id_field]
                    if not isinstance(identifier, str) or identifier in seen:
                        raise PublicDataError("Native pagination repeated or invalidated a record identifier")
                    seen.add(identifier)
            yield from enumerate(batch, start=offset)
        if bounds[1] == total:
            return
        if bounds[1] == offset:
            raise PublicDataError("Native pagination made no progress")
        offset = bounds[1]
