import json
from copy import deepcopy
from importlib.metadata import entry_points

import pytest
from are.simulation.agents.agent_log import AgentUserInterfaceLog, BaseAgentLog
from are.simulation.agents.are_simulation_agent_config import ARESimulationReactBaseAgentConfig
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent
from are.simulation.agents.default_agent.base_agent import BaseAgent

from better_are_react_agent import create_agent, list_agents
from better_are_react_agent.catalog import identity
from better_are_react_agent.runtime import STATE_KEY
from better_are_react_agent.smoke import ScriptedEngine, action, make_agent, run

NAMES = [row["id"] for row in list_agents()]


@pytest.mark.parametrize("name", NAMES)
def test_native_tool_execution(name):
    assert run(name)["status"] == "passed"


@pytest.mark.parametrize("entry", entry_points(group="are.react_agents"), ids=lambda e: e.name)
def test_entry_point_matches_native_factory(entry):
    config = ARESimulationReactBaseAgentConfig(system_prompt="native prompt", use_custom_logger=False)
    original = config.model_dump()
    agent = entry.load()(ScriptedEngine([]), config)
    assert type(agent) is BaseAgent
    assert config.model_dump() == original
    assert agent.step.__func__ is BaseAgent.step
    assert agent.tools == {}


def test_baseline_preserves_prompt_executor_and_engine():
    engine = ScriptedEngine([])
    config = ARESimulationReactBaseAgentConfig(system_prompt="exact native bytes", use_custom_logger=False)
    expected = are_simulation_react_json_agent(engine, config)
    actual = create_agent(engine, config)
    assert actual.init_system_prompts == expected.init_system_prompts
    assert type(actual.action_executor) is type(expected.action_executor)
    assert actual.llm_engine is engine
    assert actual.custom_state == expected.custom_state


def planned():
    return action("Fixture__read", {"name": "a"}, followups=[{
        "action": "Fixture__read", "action_input": {"name": "b"},
        "observation_contains": ["contents:a"]}])


def test_public_continuation_skips_one_model_callback_and_preserves_receipts():
    engine = ScriptedEngine([planned()])
    agent, read, _ = make_agent("harnessmm-public-continuation", engine)
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
    agent, read, _ = make_agent("harnessmm-public-continuation", engine)
    agent.step()
    agent.append_agent_log(AgentUserInterfaceLog(content="Read c instead.",
        timestamp=agent.make_timestamp(), agent_id=agent.agent_id))
    agent.step()
    assert read.calls == ["a", "c"] and len(engine.requests) == 2


def test_pending_provider_call_restores_without_reprocessing_feedback():
    class Interrupted(BaseException):
        pass

    captured = {}
    def interrupt(messages, **kwargs):
        captured["messages"] = deepcopy(messages)
        captured["state"] = json.loads(json.dumps(agent.custom_state))
        captured["logs"] = [row.to_dict() for row in agent.logs]
        raise Interrupted()

    agent, _, _ = make_agent("harnessmm-public-continuation", interrupt)
    with pytest.raises(Interrupted):
        agent.step()
    resumed_engine = ScriptedEngine([planned()])
    resumed, read, _ = make_agent("harnessmm-public-continuation", resumed_engine)
    resumed.custom_state = captured["state"]
    resumed.logs = [BaseAgentLog.from_dict(deepcopy(row)) for row in captured["logs"]]
    # Native pending-step runtimes pass the original saved prompt here.
    response, _ = resumed.llm_engine(captured["messages"])
    assert resumed_engine.requests == [captured["messages"]]
    assert "followups" not in response
    assert resumed.custom_state[STATE_KEY]["controller"]["pending"][0]["action_input"] == {"name": "b"}
    assert read.calls == []


def test_snapshot_of_queued_action_resumes_same_native_action():
    engine = ScriptedEngine([planned()])
    agent, _, _ = make_agent("harnessmm-public-continuation", engine)
    agent.step()
    state = json.loads(json.dumps(agent.custom_state))
    logs = [row.to_dict() for row in agent.logs]
    restored, read, _ = make_agent("harnessmm-public-continuation", ScriptedEngine([]))
    restored.custom_state = state
    restored.logs = [BaseAgentLog.from_dict(deepcopy(row)) for row in logs]
    restored.step()
    assert read.calls == ["b"]


def test_mismatched_checkpoint_fails_before_model_call():
    agent, _, _ = make_agent("harnessmm-public-continuation", ScriptedEngine([]))
    agent.custom_state[STATE_KEY] = {"identity": {**identity("harnessmm-public-continuation"), "source_sha256": "wrong"}}
    with pytest.raises(ValueError, match="identity"):
        agent.step()


def test_terminal_text_uses_native_user_interface():
    engine = ScriptedEngine([action("Fixture__read", {"name": "a"}), "Final answer: contents:a"])
    agent, _, reply = make_agent("paretosaddler-i22-appendix", engine)
    agent.step()
    agent.step()
    assert reply.calls == ["contents:a"]


def test_policy_instances_are_isolated():
    a, _, _ = make_agent("autosaddler-appendix", ScriptedEngine([]))
    b, _, _ = make_agent("baseline", ScriptedEngine([]))
    assert "Research policy" in a.init_system_prompts["system_prompt"]
    assert "Research policy" not in b.init_system_prompts["system_prompt"]
    assert STATE_KEY not in b.custom_state


def test_active_signature_repair_executes_through_native_tool():
    from are.simulation.tools import Tool

    class EmailReply(Tool):
        name = "Emails__reply_to_email"
        description = "Reply to an email."
        inputs = {"body": {"type": "string", "description": "Reply body"}}
        output_type = "string"

        def __init__(self):
            super().__init__()
            self.delivered = []

        def forward(self, body):
            self.delivered.append(body)
            return "sent"

    engine = ScriptedEngine([action("Emails__reply_to_email", {"body": "Thanks.\nThe event starts at 10."})])
    agent, _, _ = make_agent("activesaddler-appendix", engine,
                             task='Reply and sign off with "Best,\\nAlice Chen".')
    email = EmailReply()
    agent.tools[email.name] = email
    agent.init_tools()
    agent.step()
    assert email.delivered == ["Thanks.\nThe event starts at 10.\n\nBest,\nAlice Chen"]
    assert len(engine.requests) == 1
    assert agent.custom_state[STATE_KEY]["last_intervention"]["reason"] == "explicit_multiline_signature"


def test_external_entry_points_expose_independent_content_identity():
    entries = list(entry_points(group="are.react_agents"))
    assert {e.name for e in entries} == set(NAMES)
    for entry in entries:
        factory = entry.load()
        first = factory.agent_identity()
        assert first["agent"] == entry.name
        assert len(first["source_sha256"]) == 64
        first["source_sha256"] = "tampered"
        assert factory.agent_identity()["source_sha256"] != "tampered"
