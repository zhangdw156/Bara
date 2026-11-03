"""Agent-side adapters of algorithms visible in AutoSaddler's published patches.

All data comes from native tool calls. Pagination and per-call event/time accounting
are adapter differences, documented in tool_sources.json, not paper equivalence claims.
"""

from datetime import datetime, timezone

from .public_data import PublicDataError, paged_records, public_data, require_record
from .tool_hooks import DerivedTool, ToolChanges, ToolHook

SOURCE = ("https://github.com/autosaddler-projectpage/autosaddler-projectpage.github.io/blob/"
          "afd493fa47cdbced1c1a829285836b88d8cdbf70/src/components/EvolutionDemo/evo-data.ts")
CONTACT_FIELDS = ("first_name", "last_name", "phone", "email", "city_living", "country",
                  "nationality", "job", "address")


def _strings(items, label):
    if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
        raise PublicDataError(f"{label} must be a list of strings")
    return items


def crime_batch(call, native_name, zip_codes):
    _strings(zip_codes, "zip_codes")
    result = {}
    # The published implementation processes duplicates and charges each supplied
    # ZIP. It skips unknown ZIPs but propagates rate-limit failures.
    for code in zip_codes:
        try:
            result[code] = public_data(call(native_name, {"zip_code": code}))
        except ValueError as exc:
            if str(exc).strip() != "Zip code does not exist in our database":
                raise
    return result


def email_addresses(call, native_name, folder_name="INBOX"):
    if not isinstance(folder_name, str):
        raise TypeError("folder_name must be a string")
    senders, recipients = set(), set()
    for _, email in paged_records(call, native_name, kind="emails",
                                  arguments={"folder_name": folder_name.upper()}):
        require_record(email, {"sender", "recipients", "cc"})
        if not isinstance(email["sender"], str):
            raise PublicDataError("Email sender is not a string")
        senders.add(email["sender"])
        recipients.update(_strings(email["recipients"], "Email recipients"))
        recipients.update(_strings(email["cc"] or [], "Email cc"))
    return {"senders": sorted(senders), "recipients": sorted(recipients)}


def search_contacts(call, native_name, query):
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    query = query.lower()
    result = []
    for _, contact in paged_records(call, native_name, kind="contacts"):
        require_record(contact, set(CONTACT_FIELDS))
        values = [contact[key] for key in CONTACT_FIELDS]
        if any(value is not None and not isinstance(value, str) for value in values):
            raise PublicDataError("Contact search fields must be strings or null")
        first, last = contact["first_name"], contact["last_name"]
        if first is None or last is None:
            raise PublicDataError("Contact names must be present")
        if any(value is not None and query in value.lower() for value in values) or any(
                query in name.lower() for name in (first + " " + last, last + " " + first)):
            result.append(contact)
    return result


def ride_search(call, native_name, date=None, start_location_keyword=None, end_location_keyword=None):
    for value in (date, start_location_keyword, end_location_keyword):
        if value is not None and not isinstance(value, str):
            raise TypeError("Ride filters must be strings or null")
    matching, count = [], 0
    for index, ride in paged_records(call, native_name, kind="rides"):
        count += 1
        require_record(ride, {"time_stamp", "start_location", "end_location"})
        timestamp = ride["time_stamp"]
        if date is not None:
            if timestamp is None:
                continue
            if type(timestamp) not in (int, float):
                raise PublicDataError("Ride timestamp is not numeric")
            if datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d") != date:
                continue
        selected = True
        for field, query in (("start_location", start_location_keyword),
                             ("end_location", end_location_keyword)):
            value = ride[field]
            if value is not None and not isinstance(value, str):
                raise PublicDataError("Ride location is not a string")
            if query is not None and (value is None or query.lower() not in value.lower()):
                selected = False
        if selected:
            matching.append({"index": index, "ride": ride})
    return {"matching_rides": matching, "total_matches": len(matching), "total_rides": count}


def _current_user(call, contacts_name, lookup_name):
    raw = call(contacts_name, {})
    try:
        profile = public_data(raw)
    except PublicDataError:
        if not isinstance(raw, str):
            raise
        # Native Contact.__str__ is also a public format. Match field labels exactly.
        rows = [line.strip().split(": ", 1) for line in raw.splitlines() if ": " in line]
        values = {key: value for key, value in rows}
        if "Contact ID" not in values:
            raise PublicDataError("Current-user receipt is not a native Contact") from None
        profile = {"first_name": values.get("First Name"), "last_name": values.get("Last Name")}
    require_record(profile, {"first_name", "last_name"})
    if any(not isinstance(profile[key], str) for key in ("first_name", "last_name")):
        raise PublicDataError("Current-user full name is unavailable")
    ident = call(lookup_name, {"user_name": profile["first_name"] + " " + profile["last_name"]})
    # Native IDs are strings, including phone numbers. Do not parse a literal
    # numeric/plus-prefixed ID as a JSON number or Python unary expression.
    if isinstance(ident, str) and ident.startswith(("'", '"')):
        ident = public_data(ident)
    if not isinstance(ident, str) or not ident or ident in {"None", "null"}:
        raise PublicDataError("Current-user messaging ID cannot be resolved from public tools")
    return ident


def participants(call, native_name, *, v2=False, contacts_name=None, lookup_name=None):
    excluded = _current_user(call, contacts_name, lookup_name) if v2 else "Me"
    field, result_key = ("participant_ids", "participant_ids") if v2 else ("participants", "participants")
    names, seen, offset = set(), set(), 0
    while True:
        # A page of one respects every positive native view limit. An empty page
        # at offset == population size is valid in both native implementations.
        rows = public_data(call(native_name, {"offset": offset, "limit": 1,
                            "offset_recent_messages_per_conversation": 0,
                            "limit_recent_messages_per_conversation": 0}))
        if not isinstance(rows, list) or len(rows) > 1:
            raise PublicDataError("Conversation enumeration did not return the requested page")
        if not rows:
            return {result_key: sorted(names)}
        conversation = require_record(rows[0], {field, "conversation_id"})
        ident = conversation["conversation_id"]
        if not isinstance(ident, str) or ident in seen:
            raise PublicDataError("Conversation pagination repeated an identifier")
        seen.add(ident)
        names.update(item for item in _strings(conversation[field], field) if item != excluded)
        offset += 1


def _input(kind, description, **options):
    return {"type": kind, "description": description, **options}


def select_tools(context, native, call):
    """Select tool adaptations by native tool availability and input schemas."""
    changes = ToolChanges()

    def install(name, inputs, description, execute, source_patch, required, replace=False):
        for dependency, keys in required.items():
            if dependency not in native or not set(keys) <= native[dependency].inputs.keys():
                changes.decisions.append({"tool": name, "status": "unavailable",
                                          "reason": "native_prerequisite", "dependency": dependency})
                return
        if name in native and not replace:
            changes.decisions.append({"tool": name, "status": "native_tool_retained"})
            return
        tool = DerivedTool(name=name, inputs=inputs, description=description,
                           execute=execute, source={"url": SOURCE, "patch": source_patch,
                                                    "fidelity": "public-algorithm-adaptation"})
        (changes.replace if replace else changes.add)[name] = tool
        changes.decisions.append({"tool": name, "status": "active", "patch": source_patch,
                                  "fidelity": "public-algorithm-adaptation"})

    for name in sorted(native):
        prefix, separator, method = name.rpartition("__")
        if not separator:
            continue
        if method == "get_crime_rate":
            install(prefix + "__get_crime_rates_batch",
                    {"zip_codes": _input("any", "List of ZIP code strings; duplicates each consume a call.")},
                    "Query multiple ZIP codes through native reads. Unknown ZIPs are skipped; native rate limits apply.",
                    lambda zip_codes, n=name: crime_batch(call, n, zip_codes), "I-08 -> I-11",
                    {name: {"zip_code"}})
        elif method == "list_emails":
            install(prefix + "__get_email_addresses_in_folder",
                    {"folder_name": _input("string", "INBOX, SENT, DRAFT, or TRASH.", default="INBOX")},
                    "Return sorted unique senders and recipients, including cc, across the complete email folder.",
                    lambda folder_name="INBOX", n=name: email_addresses(call, n, folder_name),
                    "I-13 -> I-14", {name: {"folder_name", "offset", "limit"}})
        elif method == "get_contacts" and prefix + "__search_contacts" in native:
            search = prefix + "__search_contacts"
            install(search, {"query": _input("string", "Case-insensitive substring to search.")},
                    "Search names, phone, email, city, country, nationality, job, and address using complete native contact pages.",
                    lambda query, n=name: search_contacts(call, n, query), "I-06 -> I-08",
                    {name: {"offset"}, search: {"query"}}, replace=True)
        elif method == "get_ride_history":
            install(prefix + "__search_ride_history",
                    {"date": _input("string", "UTC date YYYY-MM-DD, or null.", default=None, nullable=True),
                     "start_location_keyword": _input("string", "Origin substring, or null.", default=None, nullable=True),
                     "end_location_keyword": _input("string", "Destination substring, or null.", default=None, nullable=True)},
                    "Search the complete native ride history by UTC date and case-insensitive origin/destination substrings. Preserve original indexes.",
                    lambda date=None, start_location_keyword=None, end_location_keyword=None, n=name:
                    ride_search(call, n, date, start_location_keyword, end_location_keyword),
                    "I-24 -> I-25", {name: {"offset", "limit"}})
        elif method == "list_recent_conversations":
            sender = native.get(prefix + "__send_message")
            if sender is None:
                continue
            required = {name: {"offset", "limit", "offset_recent_messages_per_conversation",
                               "limit_recent_messages_per_conversation"}}
            if "user_id" in sender.inputs:
                profiles = [key for key, tool in native.items()
                            if key.endswith("__get_current_user_details") and not tool.inputs]
                if len(profiles) != 1:
                    changes.decisions.append({"tool": prefix + "__get_all_participants", "status": "unavailable",
                                              "reason": "unique_public_current_user_source_required"})
                    continue
                profile, lookup = profiles[0], prefix + "__get_user_id"
                required[profile], required[lookup] = set(), {"user_name"}
                def execute(n=name, p=profile, lookup=lookup):
                    return participants(call, n, v2=True, contacts_name=p, lookup_name=lookup)
                detail = "Return sorted unique participant IDs, excluding the publicly resolved current user."
            elif "conversation_id" in sender.inputs:
                def execute(n=name):
                    return participants(call, n)
                detail = "Return sorted unique participant names across conversations, excluding Me."
            else:
                continue
            install(prefix + "__get_all_participants", {}, detail, execute, "I-13 -> I-14", required)
    return changes


def autosaddler_hook():
    return ToolHook("autosaddler-published-tools", SOURCE, select_tools)
