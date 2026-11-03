# ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906) · [Source manifest](SOURCE.json)

This directory contains an installable ARE project, with its ReAct implementation in
`are/simulation/agents/default_agent/`.

Use the native factory:

```python
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

agent = are_simulation_react_json_agent(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

From this directory, `uv sync` creates its own `.venv`. From the collection root, `uv run bara smoke activesaddler` checks the same source with scripted model responses. `uv run bara benchmark activesaddler --help` opens the evaluation options.

Reconstructs the email-closing and calendar-replacement repairs in Appendix G.
See [CHANGES.md](CHANGES.md) for implementation details and source references.
