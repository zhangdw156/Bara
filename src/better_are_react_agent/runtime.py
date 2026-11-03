"""Instance-local model-boundary adapters, retaining ARE's step and tool executor."""

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict

from .catalog import identity
from .guards import active_repair, render_action, task_text, terminal_response
from .vendor.harnessmm_continuation import PLAN_INSTRUCTION, PublicContinuation, action_object

STATE_KEY = "better_are_react_agent"
INTERRUPTS = {"task", "agent_user_interface", "environment_notifications", "hint", "task_reminder"}


class VariantEngine:
    def __init__(self, agent, provider, variant):
        self.agent, self.provider, self.variant = agent, provider, variant

    def __getattr__(self, name):
        return getattr(self.provider, name)

    def _state(self):
        state = self.agent.custom_state.get(STATE_KEY)
        if not isinstance(state, dict) or state.get("identity") != identity(self.variant):
            raise ValueError("Agent checkpoint identity differs from the selected implementation")
        return state

    def __call__(self, messages, **kwargs):
        state = self._state()
        if self.variant == "harnessmm-public-continuation":
            return self._continuation(messages, kwargs, state)
        response = self.provider(messages, **kwargs)
        text, metadata = response if isinstance(response, tuple) else (response, None)
        replacement, reason = None, None
        if self.variant == "activesaddler-appendix":
            replacement, reason = active_repair(action_object(text), self.agent.logs,
                                               self.agent.action_executor.tools)
        elif self.variant == "paretosaddler-i22-appendix":
            replacement = terminal_response(text, self.agent.logs, self.agent.action_executor.tools)
            reason = "explicit_terminal_text"
        if replacement is not None:
            state["last_intervention"] = {"reason": reason, "original": text, "replacement": replacement}
            text = render_action(replacement, "Apply the publicly supported " + reason + " repair.")
        return (text, metadata) if isinstance(response, tuple) else text

    def _continuation(self, messages, kwargs, state):
        logs = self.agent.logs
        signature = hashlib.sha256(task_text(logs).encode()).hexdigest()
        if state.get("task_sha256") != signature or state.get("cursor", 0) > len(logs):
            state.clear()
            state.update(identity=identity(self.variant), task_sha256=signature, cursor=0,
                         controller=asdict(PublicContinuation(require_stall=False)))
        controller = PublicContinuation(**state["controller"])
        legal = set(self.agent.action_executor.tools)
        # A caller may snapshot from inside provider(). Keep this branch replayable
        # without consuming the same tool feedback a second time on recovery.
        if state.get("phase") == "awaiting_model":
            prompt = deepcopy(state["model_messages"])
        else:
            fresh = logs[state["cursor"]:]
            kinds = {row.get_type() for row in fresh}
            observations = [row.content for row in fresh if row.get_type() == "observation"
                            and isinstance(getattr(row, "content", None), str)]
            text, decision = controller.decide(
                observation="\n".join(observations) or None, error="error" in kinds,
                intervened=bool(kinds & INTERRUPTS), legal_tools=legal)
            state["cursor"] = len(logs)
            state["last_decision"] = decision
            controller.traces = []
            state["controller"] = asdict(controller)
            if text is not None:
                return text, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                              "completion_duration": 0.0}
            prompt = deepcopy(messages)
            if not prompt or prompt[0].get("role") != "system" or not isinstance(prompt[0].get("content"), str):
                raise ValueError("The native text system prompt is required")
            prompt[0]["content"] += PLAN_INSTRUCTION
            state["phase"] = "awaiting_model"
            state["model_messages"] = deepcopy(prompt)
        response = self.provider(prompt, **kwargs)
        text, metadata = response if isinstance(response, tuple) else (response, None)
        executed = controller.remember(text, legal)
        state["last_plan"] = controller.traces[-1] if controller.traces else None
        controller.traces = []
        state["controller"] = asdict(controller)
        state["phase"] = "ready"
        state.pop("model_messages", None)
        state["last_model_output"] = text
        # Assert serializability at the state boundary; never persist clients or closures.
        json.dumps(state, allow_nan=False)
        return (executed, metadata) if isinstance(response, tuple) else executed
