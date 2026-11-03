from types import SimpleNamespace

from better_are_react_agent.guards import (
    active_repair,
    ambiguous_replacement,
    literal_signature,
    terminal_response,
)
from better_are_react_agent.smoke import ReplyTool


def row(kind, content="", **kwargs):
    return SimpleNamespace(get_type=lambda: kind, content=content, **kwargs)


def test_multiline_signature_is_added_once_and_never_guessed():
    action = {"action": "Emails__reply_to_email", "action_input": {"body": "Thanks!\nSee you tonight."}}
    task = 'Please sign off with "Best,\\nAlice Chen".'
    fixed = literal_signature(action, task)
    assert fixed["action_input"]["body"] == "Thanks!\nSee you tonight.\n\nBest,\nAlice Chen"
    assert literal_signature(fixed, task) is None
    assert literal_signature(action, "Reply using my name.") is None
    assert action["action_input"]["body"] == "Thanks!\nSee you tonight."


def calendar_logs(count=2, success=True):
    logs = [row("task", "Cancel the events, then replace only dates with a single cancelled event; ask for clarification otherwise.")]
    for i in range(count):
        logs += [row("tool_call", tool_name="Calendar__get_calendar_event", tool_arguments={"event_id": str(i)}),
                 row("observation", f"EventID: {i}\nTitle: Meeting\nStart: 2026-10-10 12:00:00+00:00\nEnd: 2026-10-10 13:00:00+00:00"),
                 row("tool_call", tool_name="Calendar__delete_calendar_event", tool_arguments={"event_id": str(i)}),
                 row("observation" if success else "error", f"Event {i} successfully deleted." if success else "failed")]
    return logs


def test_ambiguity_guard_runs_before_registration():
    action = {"action": "Calendar__add_calendar_event", "action_input": {"start_datetime": "2026-10-10 14:00:00"}}
    tool = ReplyTool()
    corrected, reason = active_repair(action, calendar_logs(), {tool.name: tool})
    assert corrected["action"] == tool.name
    assert "2026-10-10" in corrected["action_input"]["content"]
    assert reason == "calendar_ambiguity_before_creation"
    assert ambiguous_replacement(action, calendar_logs(count=1), {tool.name: tool}) is None
    assert ambiguous_replacement(action, calendar_logs(success=False), {tool.name: tool}) is None
    assert ambiguous_replacement(action, calendar_logs(), {}) is None


def test_new_user_decision_invalidates_ambiguity_guard():
    action = {"action": "Calendar__add_calendar_event", "action_input": {"start_datetime": "2026-10-10 14:00:00"}}
    tool = ReplyTool()
    logs = calendar_logs() + [row("agent_user_interface", "Use 2 PM for the replacement.")]
    assert ambiguous_replacement(action, logs, {tool.name: tool}) is None


def test_progress_and_refusal_are_not_terminal_answers():
    tool = ReplyTool()
    logs = [row("observation", "result")]
    for text in ("Working on it", "Final answer: I will read it", "Final answer: I cannot do that"):
        assert terminal_response(text, logs, {tool.name: tool}) is None
    assert terminal_response("Final answer: 42", [], {tool.name: tool}) is None
