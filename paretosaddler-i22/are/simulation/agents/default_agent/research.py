"""Research repair inside this native ARE source tree's model step."""

from .action_guards import render_action, terminal_response


def query_model(agent, messages, **kwargs):
    response = agent.llm_engine(messages, **kwargs)
    text, metadata = response if isinstance(response, tuple) else (response, None)
    if agent.custom_state.get("research", {}).get("method") != 'paretosaddler-i22':
        return response
    replacement = terminal_response(text, agent.logs, agent.action_executor.tools)
    reason = "explicit_terminal_text"
    if replacement is not None:
        agent.custom_state["research"]["last_intervention"] = {
            "reason": reason, "original": text, "replacement": replacement,
        }
        text = render_action(replacement, "Apply the publicly supported " + reason + " repair.")
    return (text, metadata) if isinstance(response, tuple) else text
