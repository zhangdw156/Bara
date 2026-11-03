# Implementation and source notes

## HarnessMM

[Paper](https://arxiv.org/abs/2610.32813), especially Appendix D.5 and I.1;
[official repository](https://github.com/YuhuaJiang2002/HarnessMM), commit
`e77dfb5b768831be80c7a97855450a65404d01cb`.

This variant ports the deterministic continuation controller from that revision.
`are/simulation/agents/default_agent/vendor/harnessmm_continuation.py` extracts `PLAN_INSTRUCTION`, `action_object`,
`fingerprint`, and `PublicContinuation` from `harnessmm/harness/gaia2_jev.py`.
Original bodies are retained. The source hash, published hash, and extraction are
recorded in `are/simulation/agents/default_agent/vendor/source.json`. Apache-2.0 attribution and license are retained.

The native model step uses the public non-stall configuration (`require_stall=False`) and
three-follow-up limit. Conditions are literal substrings of actual public tool
observations. New tasks, user messages, notifications, errors, or unmatched receipts
return control to the model. The same native executor runs the resulting action.

The native model step stores controller state in `BaseAgent.custom_state` and keeps a
pending model request replayable. It uses the original provider object and native
action executor.

## Native source layout

The `are/` package exposes the native factory
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research changes live in `are/simulation/agents/default_agent/`;
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
