from copy import deepcopy

import pytest

from are.simulation.agents.default_agent.public_data import PublicDataError, public_data
from are.simulation.agents.default_agent.tool_hooks import (
    TOOL_STATE,
)
from are.simulation.tools import Tool
from smoke import ScriptedEngine, action, make_agent


class NativeTool(Tool):
    def __init__(self, name, inputs, function):
        super().__init__()
        self.name = name
        self.description = "Native fixture: " + name
        self.inputs = {key: {"type": "any", "description": key} for key in inputs}
        self.function = function
        self.calls = []
        self.output_type = "any"

    def forward(self, **args):
        self.calls.append(deepcopy(args))
        return self.function(**args)


def assign(agent, *tools):
    agent.tools = {tool.name: tool for tool in tools}
    agent.init_tools()
    return agent


def auto(*tools, engine=None):
    agent, _, _ = make_agent(engine or ScriptedEngine([]))
    return assign(agent, *tools)


def contact(first, last, **fields):
    return dict(first_name=first, last_name=last, phone=None, email=None, city_living=None,
                country=None, nationality=None, job=None, address=None) | fields


def test_contacts_replace_same_name_and_paginate_original_objects():
    records = [contact("Alice", "Chen", city_living="Beijing"),
               contact("Bob", "Li", job="Engineer"), contact("Grace", "Lee", address="Beijing Road")]
    def page(offset=0):
        return {"contacts": records[offset:offset+1],
                "metadata": {"range": (offset, min(offset+1, 3)), "total": 3}}
    get = NativeTool("Contacts__get_contacts", ["offset"], page)
    original = NativeTool("Contacts__search_contacts", ["query"], lambda query: [])
    engine = ScriptedEngine([action(original.name, {"query": "beijing"})])
    agent = auto(get, original, engine=engine)
    agent.step()
    assert original.calls == []
    assert [row["offset"] for row in get.calls] == [0, 1, 2]
    assert "city, country, nationality" in engine.requests[0][0]["content"]
    output = [row.content for row in agent.logs if row.get_type() == "observation"][-1]
    assert "Alice" in output and "Grace" in output and "Bob" not in output
    assert agent.tool_hook_runtime.native[original.name] is original
    assert len(agent.custom_state[TOOL_STATE]["calls"]) == 3


def test_contacts_search_preserves_full_name_orders_empty_queries_and_null_fields():
    records = [contact("Alice", "Chen"), contact("Bob", "Li", email="b@example.org")]
    get = NativeTool("Contacts__get_contacts", ["offset"],
                     lambda offset=0: {"contacts": records, "metadata": {"range": (0, 2), "total": 2}})
    old = NativeTool("Contacts__search_contacts", ["query"], lambda query: [])
    tool = auto(get, old).tools[old.name]
    assert tool(query="CHEN ALICE") == [records[0]]
    assert tool(query="") == records
    assert tool(query="example.org") == [records[1]]


def test_crime_batch_preserves_native_rate_limit_duplicates_and_unknown_zip_behavior():
    from are.simulation.apps.city import CityApp, CrimeDataPoint

    app = CityApp(name="City", api_call_limit=4,
                  crime_data={"100": CrimeDataPoint(2.0, 3.0), "200": CrimeDataPoint(4.0, 5.0)})
    source = NativeTool("City__get_crime_rate", ["zip_code"], app.get_crime_rate)
    agent = auto(source)
    tool = agent.tools["City__get_crime_rates_batch"]
    assert tool(zip_codes=["100", "missing", "100", "200"]) == {
        "100": {"violent_crime": 2.0, "property_crime": 3.0},
        "200": {"violent_crime": 4.0, "property_crime": 5.0}}
    assert app.api_call_count == 4
    with pytest.raises(ValueError, match="Free version only supports"):
        tool(zip_codes=["100"])
    assert app.api_call_count == 0 and app.rate_limit_exceeded is True
    assert len(source.calls) == 5
    assert agent.custom_state[TOOL_STATE]["calls"][-1]["status"] == "error"
    assert agent.tools[source.name] is source


def test_email_addresses_include_cc_sort_deduplicate_and_do_not_read_messages():
    from are.simulation.apps.email_client import Email, EmailClientApp, EmailFolderName

    app = EmailClientApp(name="Emails")
    for i in range(7):
        app.folders[EmailFolderName.INBOX].add_email(Email(
            sender="b@example.org" if i % 2 else "a@example.org",
            recipients=["d@example.org"], cc=["c@example.org", "d@example.org"], timestamp=i))
    source = NativeTool("Emails__list_emails", ["folder_name", "offset", "limit"], app.list_emails)
    agent = auto(source)
    result = agent.tools["Emails__get_email_addresses_in_folder"](folder_name="inbox")
    assert result == {"senders": ["a@example.org", "b@example.org"],
                      "recipients": ["c@example.org", "d@example.org"]}
    assert [row["offset"] for row in source.calls] == [0, 5]
    assert all(not email.is_read for email in app.folders[EmailFolderName.INBOX].emails)


def test_ride_search_keeps_global_indexes_and_uses_utc_date():
    from are.simulation.apps.cab import CabApp, Ride

    app = CabApp(name="Cab", ride_history=[
        Ride(time_stamp=0, start_location="North STATION", end_location="Home"),
        Ride(time_stamp=None, start_location="Station", end_location="Home"),
        Ride(time_stamp=86399, start_location="North Station", end_location="Home"),
        Ride(time_stamp=86400, start_location="North Station", end_location="Home")])
    source = NativeTool("Cab__get_ride_history", ["offset", "limit"], app.get_ride_history)
    agent = auto(source)
    result = agent.tools["Cab__search_ride_history"](date="1970-01-01",
        start_location_keyword="station", end_location_keyword="HOME")
    assert [row["index"] for row in result["matching_rides"]] == [0, 2]
    assert result["total_matches"] == 2 and result["total_rides"] == 4


def conversation_tools(prefix, rows, *, v2=False):
    def page(offset=0, limit=1, **kwargs):
        assert limit == 1 and kwargs["limit_recent_messages_per_conversation"] == 0
        return rows[offset:offset+limit]
    source = NativeTool(prefix + "__list_recent_conversations",
        ["offset", "limit", "offset_recent_messages_per_conversation", "limit_recent_messages_per_conversation"], page)
    send = NativeTool(prefix + "__send_message", ["user_id" if v2 else "conversation_id", "content"],
                      lambda **args: pytest.fail("Enumeration must never send a message"))
    return source, send


def test_v1_participants_exclude_me_sort_and_deduplicate():
    source, send = conversation_tools("Chats", [
        {"conversation_id": "a", "participants": ["Me", "Zoe", "Alice"]},
        {"conversation_id": "b", "participants": ["Alice", "Me"]}])
    agent = auto(source, send)
    assert agent.tools["Chats__get_all_participants"]() == {"participants": ["Alice", "Zoe"]}
    assert len(source.calls) == 3


@pytest.mark.parametrize("self_id", ["self", "+1234567890", "12345", "000123"])
def test_v2_participants_require_public_self_identity_and_exclude_it(self_id):
    source, send = conversation_tools("Messages", [
        {"conversation_id": "a", "participant_ids": [self_id, "friend"]}], v2=True)
    unsupported = auto(source, send)
    assert "Messages__get_all_participants" not in unsupported.tools
    profile = NativeTool("Contacts__get_current_user_details", [],
                         lambda: {"first_name": "Alice", "last_name": "Chen"})
    lookup = NativeTool("Messages__get_user_id", ["user_name"],
                        lambda user_name: self_id if user_name == "Alice Chen" else None)
    agent = auto(source, send, profile, lookup)
    assert agent.tools["Messages__get_all_participants"]() == {"participant_ids": ["friend"]}
    assert len(profile.calls) == len(lookup.calls) == 1


def test_stalled_pages_never_become_complete_results():
    def page(folder_name, offset, limit):
        return {"emails": [], "emails_range": [0, 0], "total_emails": 3}
    source = NativeTool("Emails__list_emails", ["folder_name", "offset", "limit"], page)
    agent = auto(source)
    with pytest.raises(PublicDataError, match="progress"):
        agent.tools["Emails__get_email_addresses_in_folder"]()
    assert len(source.calls) == 1


@pytest.mark.parametrize("change", ["population", "duplicate"])
def test_changing_pages_never_become_complete_results(change):
    def page(folder_name, offset, limit):
        return {"emails": [{"sender": "a@example.org", "recipients": [], "cc": [],
                             "email_id": "same" if change == "duplicate" else str(offset)}],
                "emails_range": [offset, offset + 1],
                "total_emails": 2 + (offset if change == "population" else 0)}
    source = NativeTool("Emails__list_emails", ["folder_name", "offset", "limit"], page)
    with pytest.raises(PublicDataError, match="Population changed|repeated"):
        auto(source).tools["Emails__get_email_addresses_in_folder"]()
    assert len(source.calls) == 2


def test_repeated_conversation_page_is_rejected():
    source, send = conversation_tools("Chats", [])
    source.function = lambda **kwargs: [{"conversation_id": "same", "participants": ["Me", "Alice"]}]
    with pytest.raises(PublicDataError, match="repeated"):
        auto(source, send).tools["Chats__get_all_participants"]()
    assert len(source.calls) == 2


def test_public_decoder_accepts_native_repr_without_executing_expressions(tmp_path):
    from are.simulation.apps.contacts import Contact
    record = Contact(first_name="Alice", last_name="Chen", city_living="Beijing",
                     description="Text containing <Status.UNKNOWN: 'Unknown'> is unchanged.")
    decoded = public_data(str({"contacts": [record]}))["contacts"][0]
    assert decoded["city_living"] == "Beijing"
    assert decoded["description"] == record.description
    assert decoded["status"] == "Unknown"
    target = tmp_path / "must-not-exist"
    with pytest.raises(PublicDataError):
        public_data(f"__import__('pathlib').Path({str(target)!r}).touch()")
    assert not target.exists()


def test_derived_tool_arguments_cannot_override_captured_native_dispatch():
    source = NativeTool("City__get_crime_rate", ["zip_code"], lambda zip_code: {})
    tool = auto(source).tools["City__get_crime_rates_batch"]
    with pytest.raises(ValueError, match="Unknown derived-tool arguments"):
        tool(zip_codes=["x"], n="Other__read")
    assert source.calls == []


def test_disclosure_requires_schemas_and_preserves_a_native_existing_extension():
    wrong = NativeTool("City__get_crime_rate", ["region"], lambda region: None)
    assert "City__get_crime_rates_batch" not in auto(wrong).tools
    source = NativeTool("City__get_crime_rate", ["zip_code"], lambda zip_code: {})
    existing = NativeTool("City__get_crime_rates_batch", ["zip_codes"], lambda zip_codes: {"original": True})
    agent = auto(source, existing)
    assert agent.tools[existing.name] is existing
