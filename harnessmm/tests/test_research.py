import json
from copy import deepcopy

from are.simulation.agents.agent_log import AgentUserInterfaceLog, BaseAgentLog
from smoke import ScriptedEngine, action, make_agent

STATE_KEY = "research"

def planned():
    return action("Fixture__read", {"name": "a"}, followups=[{
        "action": "Fixture__read", "action_input": {"name": "b"},
        "observation_contains": ["contents:a"]}])

def test_public_continuation_skips_one_model_callback_and_preserves_receipts():
    engine = ScriptedEngine([planned()])
    agent, read, _ = make_agent(engine)
    agent.step()
    agent.step()
    assert read.calls == ["a", "b"]
    assert len(engine.requests) == 1
    observations = [row.content for row in agent.logs if row.get_type() == "observation"]
    assert observations == ["contents:a", "contents:b"]
    state = agent.custom_state[STATE_KEY]
    assert state["last_decision"]["execute"] is True
    json.dumps(state, allow_nan=False)

def test_new_user_message_invalidates_old_continuation():
    engine = ScriptedEngine([planned(), action("Fixture__read", {"name": "c"})])
    agent, read, _ = make_agent(engine)
    agent.step()
    agent.append_agent_log(AgentUserInterfaceLog(content="Read c instead.",
        timestamp=agent.make_timestamp(), agent_id=agent.agent_id))
    agent.step()
    assert read.calls == ["a", "c"] and len(engine.requests) == 2

def test_snapshot_of_queued_action_resumes_same_native_action():
    engine = ScriptedEngine([planned()])
    agent, _, _ = make_agent(engine)
    agent.step()
    state = json.loads(json.dumps(agent.custom_state))
    logs = [row.to_dict() for row in agent.logs]
    restored, read, _ = make_agent(ScriptedEngine([]))
    restored.custom_state = state
    restored.logs = [BaseAgentLog.from_dict(deepcopy(row)) for row in logs]
    restored.step()
    assert read.calls == ["b"]
