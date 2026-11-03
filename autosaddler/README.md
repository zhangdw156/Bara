# AutoSaddler

[Paper](https://arxiv.org/abs/2608.23041) · [Source manifest](SOURCE.json)

This directory contains an installable ARE project, with its ReAct implementation in
`are/simulation/agents/default_agent/`.

Use the native factory:

```python
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

agent = are_simulation_react_json_agent(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

From this directory, `uv sync` creates its own `.venv`. From the collection root, `uv run bara smoke autosaddler` checks the same source with scripted model responses. `uv run bara benchmark autosaddler --help` opens the evaluation options.

This research reimplementation draws on the linked paper and public sources.
[CHANGES.md](CHANGES.md) documents the implemented components and differences from the paper.
