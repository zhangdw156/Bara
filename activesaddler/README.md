# ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906) · [Source manifest](SOURCE.json)

This directory is an independent, installable ARE source tree. Its native ReAct implementation is in `are/simulation/agents/default_agent/`. It imports no sibling implementation or collection package.

Use the unchanged native factory:

```python
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

agent = are_simulation_react_json_agent(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

From this directory, `uv sync` creates its own `.venv`. From the collection root, `uv run bara smoke activesaddler` checks the same source with scripted model responses. `uv run bara benchmark activesaddler --help` opens the evaluation options.

This is a non-faithful research implementation, not the authors' verified final agent. No published score is claimed. See [CHANGES.md](CHANGES.md) for implemented behavior and limitations.
