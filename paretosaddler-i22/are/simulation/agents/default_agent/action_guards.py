import json
import re


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


def render_action(action, reason):
    return "Thought: " + reason + "\nAction:\n" + json.dumps(action, ensure_ascii=False)
