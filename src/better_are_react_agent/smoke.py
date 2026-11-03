"""Credential-free check using the real ARE factory, step, parser, tools, and logs."""

import json
from copy import deepcopy

from are.simulation.agents.agent_log import TaskLog
from are.simulation.agents.are_simulation_agent_config import ARESimulationReactBaseAgentConfig
from are.simulation.agents.default_agent.base_agent import BaseAgent
from are.simulation.agents.default_agent.prompts import (
    DEFAULT_ARE_SIMULATION_REACT_JSON_SYSTEM_PROMPT,
)
from are.simulation.tools import Tool

from .catalog import identity
from .factory import create_agent


class ReadTool(Tool):
    name = "Fixture__read"
    description = "Read a fixture item."
    inputs = {"name": {"type": "string", "description": "Item name"}}
    output_type = "string"

    def __init__(self):
        super().__init__()
        self.calls = []

    def forward(self, name):
        self.calls.append(name)
        return "contents:" + name


class ReplyTool(Tool):
    name = "AgentUserInterface__send_message_to_user"
    description = "Send a response to the user."
    inputs = {"content": {"type": "string", "description": "Response text"}}
    output_type = "string"

    def __init__(self):
        super().__init__()
        self.calls = []

    def forward(self, content):
        self.calls.append(content)
        return "Message delivered"


class ScriptedEngine:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []
        self.model_name = "offline-scripted-fixture"

    def __call__(self, messages, **kwargs):
        self.requests.append(deepcopy(messages))
        # No model call occurs; do not manufacture observed token usage.
        return next(self.replies), {}


def action(name, args, **extra):
    return "Thought: Execute the fixture step.\nAction:\n" + json.dumps(
        {"action": name, "action_input": args, **extra})


def make_agent(variant, engine, task="Read the report and tell me its contents."):
    config = ARESimulationReactBaseAgentConfig(
        system_prompt=str(DEFAULT_ARE_SIMULATION_REACT_JSON_SYSTEM_PROMPT),
        max_iterations=8, use_custom_logger=False)
    agent = create_agent(engine, config, variant=variant)
    read, reply = ReadTool(), ReplyTool()
    agent.tools = {read.name: read, reply.name: reply}
    agent.initialize()
    agent.append_agent_log(TaskLog(content=task, timestamp=agent.make_timestamp(),
                                  agent_id=agent.agent_id))
    return agent, read, reply


def run(variant):
    engine = ScriptedEngine([action("Fixture__read", {"name": "report"}),
                             action("AgentUserInterface__send_message_to_user", {"content": "contents:report"})])
    agent, read, reply = make_agent(variant, engine)
    assert type(agent) is BaseAgent
    agent.step()
    agent.step()
    assert read.calls == ["report"] and reply.calls == ["contents:report"]
    assert len(engine.requests) == 2
    return {"agent": variant, "status": "passed", "scope": "native ARE steps with scripted responses",
            "model_requests": 0, "scripted_engine_calls": len(engine.requests),
            "native_tool_calls": len(read.calls) + len(reply.calls), "identity": identity(variant)}
