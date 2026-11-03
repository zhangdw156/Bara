# Native evaluator integration

The public boundary is a callable with the signature:

```python
factory(llm_engine, base_agent_config) -> are.simulation.agents.default_agent.base_agent.BaseAgent
```

The caller provides the native `ARESimulationReactBaseAgentConfig`, the engine,
scenario tool instances, notification system, clock, and lifecycle. The agent
returns native `Thought:` / JSON `Action:` text to ARE's unmodified executor.
No external runner protocol or extra service is required.

## Select an installed factory

```python
from importlib.metadata import entry_points

name = "autosaddler-appendix"
matches = list(entry_points(group="are.react_agents", name=name))
if len(matches) != 1:
    raise ValueError(f"Expected exactly one installed factory for {name}")
factory = matches[0].load()
implementation = factory.agent_identity()
agent = factory(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

The group name is this package's integration convention, not a feature claimed to
exist in stock ARE's CLI. An evaluator that hard-codes the native factory needs
one factory-selection branch. All listed variants then use that same branch.
`agent_identity()` returns a package/content identity for provenance and recovery.
Treat entry points as trusted installed Python code, not user-supplied executable
strings. No `eval`, module-path injection, or per-run package installation is needed.

## Requests and tools

All model requests pass through the caller's engine, including retry requests.
The caller therefore retains concurrency, native-time accounting, usage, and
journaling. Provider metadata is passed through unchanged. Deterministic HarnessMM
continuations explicitly report zero model tokens because no model request occurs.
There are no unmetered helper models, subprocesses, or background tasks.

Assign the tools before initialization as for the native agent. Variants add no
environment tools and do not bypass the native executor. Guards use only task text,
public logs, and the assigned tool catalogue. Observe native post-step termination
and notification delivery; a user reply or wait still has its native meaning.

## Checkpoints

Persist the usual native logs, pending step, system prompts, task, iterations,
attachments, and `custom_state`. This package's mutable controller state is stored
under `custom_state["better_are_react_agent"]`; it contains JSON-compatible values.
No state lives in process-global patches. After creating the same factory again,
restore `custom_state` and logs before resuming the pending native step.

Pin and compare `factory.agent_identity()` before restoring **every** variant,
including prompt-only variants. Also compare the native ARE revision and tool/model
identity as required by the evaluator. Do not silently resume with another policy.
The package checks wrapped-engine identities as an additional local safeguard.

A native runtime must itself support exact interrupted-step recovery. This package
does not retrofit that capability into the PyPI ARE runtime, nor does it guarantee
recovery across committed external tool actions without the evaluator's transaction
boundary. Local tests cover controller-state replay; an end-to-end checkpoint claim
requires the host evaluator's own integration test.

## Independent trials

Create a fresh factory instance per trial. Use a fixed model, tools, scenarios,
seeds, and time/step limits for paired comparisons. Record agent ID, content digest,
ARE revision, reconstruction fidelity, and actual model usage. Report reconstruction
results under the IDs in this repository rather than as the original paper scores.
