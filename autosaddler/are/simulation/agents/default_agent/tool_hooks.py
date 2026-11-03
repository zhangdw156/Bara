"""Instance-local disclosure hooks over caller-supplied native tool instances."""

import hashlib
import json
import random
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from are.simulation.tools import Tool

TOOL_STATE = "autosaddler_tools"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class ToolContext:
    """Task text and optional public labels supplied by the evaluator, not hidden state."""

    task: str = ""
    universe_id: str | None = None
    task_id: str | None = None


@dataclass
class ToolChanges:
    add: dict[str, Tool] = field(default_factory=dict)
    replace: dict[str, Tool] = field(default_factory=dict)
    hide: tuple[str, ...] = ()
    decisions: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class ToolHook:
    name: str
    source: str
    select: Callable[[ToolContext, Mapping[str, Tool], Callable], ToolChanges]


class DerivedTool(Tool):
    """An agent-owned operation whose implementation receives only public call access."""

    def __init__(self, *, name, description, inputs, execute, source):
        super().__init__()
        self.name, self.description = name, description
        self.inputs = deepcopy(inputs)
        self.output_type = "any"
        self.execute = execute
        self.source = source

    def forward(self, **arguments):
        unknown = set(arguments) - self.inputs.keys()
        if unknown:
            raise ValueError(f"Unknown derived-tool arguments: {sorted(unknown)}")
        return self.execute(**arguments)


def _catalog(tools):
    return {name: {"description": tool.description, "inputs": tool.inputs,
                   "output_type": tool.output_type} for name, tool in sorted(tools.items())}


class ToolHookRuntime:
    def __init__(self, agent, hooks):
        self.agent, self.hooks = agent, tuple(hooks)
        self.native = {}
        self.effective = None
        self.context = ToolContext()
        # The outer ARE agent adds scenario instructions, date and notification
        # text after factory construction. Capture them at first initialization.
        self.templates = None
        self.last_key = None
        self.last_state = None

    def public_context(self):
        tasks = [str(row.content) for row in self.agent.logs
                 if row.get_type() in {"task", "agent_user_interface"}]
        labels = self.agent.custom_state.get(TOOL_STATE, {}).get("context", {})
        return ToolContext(task="\n".join(tasks) or str(self.agent.task or ""),
                           universe_id=labels.get("universe_id"), task_id=labels.get("task_id"))

    def call_native(self, name, arguments):
        # This map holds the original objects, even when their model-facing names
        # are replaced or hidden. Never dispatch back through the augmented map.
        if name not in self.native:
            raise ValueError(f"Derived tool requested unavailable native tool: {name}")
        state = self.agent.custom_state[TOOL_STATE]
        call = {"tool": name, "arguments": deepcopy(arguments), "status": "started",
                "native_time_start": self.agent.make_timestamp()}
        state.setdefault("calls", []).append(call)
        try:
            result = self.native[name](**arguments)
        except BaseException as exc:
            call.update(status="error", error=str(exc), native_time_end=self.agent.make_timestamp())
            raise
        call.update(status="returned", native_time_end=self.agent.make_timestamp(),
                    receipt_sha256=hashlib.sha256(str(result).encode()).hexdigest())
        return result

    def refresh(self):
        agent = self.agent
        assigned = agent.tools is not self.effective
        native = dict(agent.tools) if assigned else self.native
        context = self.public_context()
        native_description = _catalog(native)
        key = digest({"context": context.__dict__, "tools": native_description})
        state = agent.custom_state.get(TOOL_STATE, {})
        if key == self.last_key and not assigned and state is self.last_state:
            if digest(_catalog(agent.tools)) != state["disclosed_tools_sha256"]:
                raise ValueError("Assign a fresh native tool dictionary; do not mutate disclosed tools in place")
            return
        if self.last_key is not None and key != self.last_key and getattr(agent, "pending_step", None):
            raise ValueError("Cannot switch tool disclosure during a pending native step")
        active = dict(native)
        decisions = []
        owned = set()
        for hook in self.hooks:
            delta = hook.select(context, MappingProxyType(native), self.call_native)
            if not isinstance(delta, ToolChanges):
                raise TypeError("Tool hook must return ToolChanges")
            if set(delta.add) & (set(active) | set(delta.replace)):
                raise ValueError("An added tool collides with an existing tool")
            if set(delta.hide) & (set(delta.add) | set(delta.replace)):
                raise ValueError("A hook cannot hide a tool it also adds or replaces")
            if not set(delta.replace) <= active.keys() or not set(delta.hide) <= active.keys():
                raise ValueError("Tool replacement or hiding targets an unavailable tool")
            touched = set(delta.add) | set(delta.replace) | set(delta.hide)
            if touched & owned:
                raise ValueError("Multiple hooks modify the same tool")
            for name, tool in {**delta.add, **delta.replace}.items():
                if name != tool.name:
                    raise ValueError("Tool map key and declared name differ")
            active.update(delta.add)
            active.update(delta.replace)
            for name in delta.hide:
                del active[name]
            owned |= touched
            decisions.append({"hook": hook.name, "source": hook.source,
                              "added": sorted(delta.add), "replaced": sorted(delta.replace),
                              "hidden": sorted(delta.hide), "decisions": delta.decisions})
        if getattr(agent, "pending_step", None) and state.get("disclosed_tools_sha256"):
            if (state["disclosed_tools_sha256"] != digest(_catalog(active))
                    or state.get("native_tools_sha256") != digest(native_description)
                    or state.get("context_sha256") != digest(context.__dict__)):
                raise ValueError("Restored native step has a different tool catalogue or context")
        if "prompt_templates" in state:
            self.templates = deepcopy(state["prompt_templates"])
        elif self.templates is None:
            self.templates = deepcopy(agent.init_system_prompts)
        tool_values = list(active.values())
        if agent.shuffle_tools:
            random.Random(agent.shuffle_seed).shuffle(tool_values)
        prompts = agent.update_system_prompt_tools(deepcopy(self.templates), tool_values)
        state = agent.custom_state.setdefault(TOOL_STATE, {})
        state.update(native_tools_sha256=digest(native_description),
                     disclosed_tools_sha256=digest(_catalog(active)),
                     context_sha256=digest(context.__dict__), decisions=decisions,
                     prompt_templates=deepcopy(self.templates))
        self.native = native
        self.effective = active
        self.context = context
        agent.tools = active
        agent.action_executor.update_tools(active)
        agent.system_prompts = prompts
        agent.system_prompt = "\n\n".join(str(text) for text in prompts.values())
        self.last_key = key
        self.last_state = state


def install_tool_hooks(agent, hooks):
    """Install before the caller assigns scenario tools. No global class is patched."""
    if hasattr(agent, "tool_hook_runtime"):
        raise ValueError("Tool hooks are already installed on this agent")
    runtime = ToolHookRuntime(agent, hooks)
    original_init = agent.init_tools
    original_history = agent.build_history_from_logs

    def init_tools():
        runtime.refresh()
        # Native initialization expands its prompt template in place. Start from
        # the original template each time so later tool changes remain visible.
        agent.init_system_prompts = deepcopy(runtime.templates)
        return original_init()

    def history(*args, **kwargs):
        runtime.refresh()
        result = original_history(*args, **kwargs)
        for message in result:
            if message["role"] == "system":
                message["content"] = agent.system_prompt + "\n"
                break
        return result

    agent.init_tools = init_tools
    agent.build_history_from_logs = history
    agent.tool_hook_runtime = runtime
    return agent


def set_tool_context(agent, *, universe_id=None, task_id=None):
    """Optional public routing labels. Published hooks do not hard-code benchmark IDs."""
    if not hasattr(agent, "tool_hook_runtime"):
        raise ValueError("This agent has no tool-disclosure hooks")
    if any(value is not None and not isinstance(value, str) for value in (universe_id, task_id)):
        raise TypeError("Public context labels must be strings or None")
    context = {"universe_id": universe_id, "task_id": task_id}
    previous = agent.custom_state.get(TOOL_STATE, {}).get("context", {})
    if getattr(agent, "pending_step", None) and any(
            previous.get(key) != value for key, value in context.items()):
        raise ValueError("Cannot switch tool context during a pending native step")
    agent.custom_state.setdefault(TOOL_STATE, {})["context"] = context
