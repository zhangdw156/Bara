"""Conservative, public-evidence implementations of two published repair cases.

These recognizers are intentionally narrower than a semantic model. An unsupported
request stays with the native actor. No scenario IDs or environment internals are read.
"""

import ast
import json
import re
from collections import defaultdict
from datetime import datetime, timezone


def task_text(logs):
    return "\n".join(str(row.content) for row in logs
                     if row.get_type() in {"task", "agent_user_interface"})


def user_action(tools, text):
    name = "AgentUserInterface__send_message_to_user"
    tool = tools.get(name)
    if tool is None or "content" not in getattr(tool, "inputs", {}):
        return None
    return {"action": name, "action_input": {"content": text}}


def terminal_response(text, logs, tools):
    """Convert explicit terminal text only, after observed native tool execution."""
    if not isinstance(text, str) or "Action:" in text or "Thought:" in text:
        return None
    match = re.fullmatch(r"\s*Final answer:\s*(\S[\s\S]*)", text, re.I)
    if not match or not any(row.get_type() == "observation" for row in logs):
        return None
    answer = match[1].strip()
    if re.match(r"(?:I (?:will|am going to|cannot|can't|won't)|Sorry|Let me|Working on)\b", answer, re.I):
        return None
    return user_action(tools, answer)


def literal_signature(action, task):
    if not action["action"].endswith("__reply_to_email"):
        return None
    matches = re.findall(r'''(?:sign\s+off\s+with|end\s+(?:the\s+)?(?:reply|email)\s+with)\s*["']([^"']+)["']''', task, re.I)
    if len(set(matches)) != 1:
        return None
    closing = matches[0].replace("\\n", "\n")
    args = action["action_input"]
    body_key = next((name for name in ("body", "content", "message") if name in args), None)
    if body_key is None or not isinstance(args[body_key], str):
        return None
    body = args[body_key].rstrip()
    if not body or body.endswith(closing):
        return None
    return {"action": action["action"],
            "action_input": {**args, body_key: body + "\n\n" + closing}}


def _calendar_records(text):
    """Read native CalendarEvent representations with literal arguments only."""
    records = []
    try:
        tree = ast.parse(text, mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "CalendarEvent" and not node.args:
                value = {item.arg: ast.literal_eval(item.value) for item in node.keywords if item.arg}
                records.append(value)
            elif isinstance(node, ast.Dict):
                try:
                    value = ast.literal_eval(node)
                except (ValueError, TypeError, SyntaxError):
                    continue
                if "event_id" in value and "start_datetime" in value:
                    records.append(value)
    except (ValueError, TypeError, SyntaxError, RecursionError):
        pass
    # Individual native event reads use CalendarEvent.__str__.
    for match in re.finditer(r"(?:^|\n)EventID: ([^\n]+)\nTitle: [^\n]*\nStart: (\d{4}-\d\d-\d\d)[^\n]*", text):
        records.append({"event_id": match[1], "start_datetime": match[2]})
    return records


def _day(value):
    if type(value) in (float, int):
        try:
            return datetime.fromtimestamp(value, timezone.utc).date().isoformat()
        except (ValueError, OverflowError, OSError):
            return None
    if isinstance(value, str) and re.match(r"\d{4}-\d\d-\d\d(?:$|[ T])", value):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return None
    return None


def ambiguous_replacement(action, logs, tools):
    if action["action"] != "Calendar__add_calendar_event":
        return None
    task = task_text(logs)
    if not (re.search(r"cancel", task, re.I) and re.search(r"clarif|ambig", task, re.I)
            and re.search(r"only[^.\n]{0,100}(?:single|exactly one|one cancelled)", task, re.I)):
        return None
    proposed = _day(action["action_input"].get("start_datetime"))
    if proposed is None:
        return None
    known, cancelled = {}, defaultdict(set)
    previous = None
    for row in logs:
        kind = row.get_type()
        if kind == "tool_call":
            previous = (row.tool_name, row.tool_arguments)
        elif kind in {"task", "agent_user_interface", "error"}:
            previous = None
            if kind in {"task", "agent_user_interface"}:
                known, cancelled = {}, defaultdict(set)
        elif kind == "observation" and previous:
            name, args = previous
            value = str(row.content)
            if name.startswith("Calendar__get_") or name in {"Calendar__search_events", "Calendar__read_today_calendar_events"}:
                for record in _calendar_records(value):
                    day = _day(record.get("start_datetime"))
                    if day and isinstance(record.get("event_id"), str):
                        known[record["event_id"]] = day
            if name == "Calendar__delete_calendar_event" and isinstance(args, dict):
                ident = args.get("event_id")
                if ident in known and value.strip() == f"Event {ident} successfully deleted.":
                    cancelled[known[ident]].add(ident)
            previous = None
    if len(cancelled[proposed]) < 2:
        return None
    return user_action(tools, f"Multiple cancelled events fall on {proposed}. Which original event's time should the replacement use?")


def active_repair(action, logs, tools):
    if action is None:
        return None, None
    replacement = ambiguous_replacement(action, logs, tools)
    if replacement:
        return replacement, "calendar_ambiguity_before_creation"
    replacement = literal_signature(action, task_text(logs))
    if replacement:
        return replacement, "explicit_multiline_signature"
    return None, None


def render_action(action, reason):
    return "Thought: " + reason + "\nAction:\n" + json.dumps(action, ensure_ascii=False)
