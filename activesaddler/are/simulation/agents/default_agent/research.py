"""Research repair inside this native ARE source tree's model step."""

from .action_guards import active_repair, render_action


def query_model(agent, messages, **kwargs):
    response = agent.llm_engine(messages, **kwargs)
    text, metadata = response if isinstance(response, tuple) else (response, None)
    if agent.custom_state.get("research", {}).get("method") != 'activesaddler':
        return response
    try:
        parsed = agent.action_executor.parse_action(
            agent.action_executor.extract_action(text, split_token=agent.action_token))
        action = {"action": parsed.tool_name, "action_input": parsed.arguments}
        if not isinstance(parsed.arguments, dict):
            action = None
    except Exception:
        action = None
    replacement, reason = active_repair(action, agent.logs, agent.action_executor.tools)
    if replacement is not None:
        agent.custom_state["research"]["last_intervention"] = {
            "reason": reason, "original": text, "replacement": replacement,
        }
        text = render_action(replacement, "Apply the publicly supported " + reason + " repair.")
    return (text, metadata) if isinstance(response, tuple) else text
