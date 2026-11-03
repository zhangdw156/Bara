import inspect
import json
from copy import deepcopy
from pathlib import Path

import pytest

from are.simulation.agents.agent_builder import AgentBuilder
from are.simulation.agents.agent_config_builder import AgentConfigBuilder
from are.simulation.agents.agent_log import BaseAgentLog, TaskLog
from are.simulation.agents.are_simulation_agent_config import ARESimulationReactBaseAgentConfig
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent
from are.simulation.agents.default_agent.base_agent import BaseAgent
from are.simulation.environment import Environment, EnvironmentConfig
from smoke import METHOD, ReadTool, ReplyTool, ScriptedEngine, action, make_agent, run


def test_native_imports_and_factory_are_owned_by_this_directory():
    root = Path(__file__).resolve().parents[1]
    for value in (BaseAgent, are_simulation_react_json_agent):
        assert Path(inspect.getfile(value)).resolve().is_relative_to(root)
    config = ARESimulationReactBaseAgentConfig(system_prompt="native prompt", use_custom_logger=False)
    original = config.model_dump()
    engine = ScriptedEngine([])
    agent = are_simulation_react_json_agent(engine, config)
    assert type(agent) is BaseAgent
    assert agent.llm_engine is engine
    assert agent.custom_state["research"]["method"] == METHOD
    assert config.model_dump() == original


def test_native_read_and_reply():
    assert run()["status"] == "passed"


def test_native_format_retry_keeps_the_same_provider():
    engine = ScriptedEngine(["malformed", action("Fixture__read", {"name": "a"})])
    agent, read, _ = make_agent(engine)
    agent.step()
    assert len(engine.requests) == 2
    assert read.calls == ["a"]
    assert agent.pending_step is None


def test_native_builder_uses_the_local_research_source():
    class EngineBuilder:
        def create_engine(self, **kwargs):
            return engine

    engine = ScriptedEngine([action("Fixture__read", {"name": "a"}, followups=[{
        "action": "Fixture__read", "action_input": {"name": "b"},
        "observation_contains": ["contents:a"]}]), action("Fixture__read", {"name": "b"})])
    env = Environment(EnvironmentConfig(start_time=0))
    config = AgentConfigBuilder().build("default")
    config.base_agent_config.use_custom_logger = False
    wrapped = AgentBuilder(EngineBuilder()).build(config, env)
    native = wrapped.react_agent
    assert native.custom_state["research"]["method"] == METHOD
    read, reply = ReadTool(), ReplyTool()
    native.tools = {read.name: read, reply.name: reply}
    native.initialize()
    native.append_agent_log(TaskLog(content="Read a and b.", timestamp=native.make_timestamp(),
                                    agent_id=native.agent_id))
    native.step()
    native.step()
    assert read.calls == ["a", "b"]
    assert len(engine.requests) == (1 if METHOD == "harnessmm" else 2)


def test_pending_request_restores_without_replaying_a_completed_tool():
    class Interrupted(BaseException):
        pass

    saved = {}
    count = 0

    def engine(messages, **kwargs):
        nonlocal count
        count += 1
        if count == 1:
            return action("Fixture__read", {"name": "a"}), {}
        saved.update(messages=deepcopy(messages), state=deepcopy(agent.custom_state),
                     pending=deepcopy(agent.pending_step),
                     logs=[row.to_dict() for row in agent.logs])
        raise Interrupted()

    agent, read, _ = make_agent(engine)
    agent.step()
    with pytest.raises(Interrupted):
        agent.step()
    assert read.calls == ["a"]
    resumed_engine = ScriptedEngine([action("AgentUserInterface__send_message_to_user", {"content": "done"})])
    resumed, resumed_read, reply = make_agent(resumed_engine)
    resumed.custom_state = json.loads(json.dumps(saved["state"]))
    resumed.pending_step = deepcopy(saved["pending"])
    resumed.logs = [BaseAgentLog.from_dict(deepcopy(row)) for row in saved["logs"]]
    resumed.step()
    assert resumed_engine.requests == [saved["messages"]]
    assert resumed_read.calls == []
    assert reply.calls == ["done"]
    assert resumed.pending_step is None


def test_checkpoint_from_another_source_is_rejected_before_model_call():
    engine = ScriptedEngine([])
    agent, _, _ = make_agent(engine)
    agent.custom_state["research"]["method"] = "another-source"
    with pytest.raises(ValueError, match="another research implementation"):
        agent.step()
    assert engine.requests == []
