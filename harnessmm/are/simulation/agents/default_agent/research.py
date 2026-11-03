"""Public HarnessMM continuation inside the native ARE model step."""

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict

from .vendor.harnessmm_continuation import PLAN_INSTRUCTION, PublicContinuation

INTERRUPTS = {"task", "agent_user_interface", "environment_notifications", "hint", "task_reminder"}


def task_text(logs):
    return "\n".join(str(row.content) for row in logs
                     if row.get_type() in {"task", "agent_user_interface"})


def query_model(agent, messages, **kwargs):
    state = agent.custom_state.get("research", {})
    if state.get("method") != "harnessmm":
        return agent.llm_engine(messages, **kwargs)
    return _continuation(agent, messages, kwargs, state)


def _continuation(agent, messages, kwargs, state):
        logs = agent.logs
        signature = hashlib.sha256(task_text(logs).encode()).hexdigest()
        if state.get("task_sha256") != signature or state.get("cursor", 0) > len(logs):
            state.clear()
            state.update(method="harnessmm", task_sha256=signature, cursor=0,
                         controller=asdict(PublicContinuation(require_stall=False)))
        controller = PublicContinuation(**state["controller"])
        legal = set(agent.action_executor.tools)
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
        response = agent.llm_engine(prompt, **kwargs)
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
