# Using a source directory

Choose `autosaddler`, `activesaddler`, `paretosaddler-i23`, `paretosaddler-i22`, or
`harnessmm`. Each is a separate ARE project with its own `are/` package,
`pyproject.toml`, `uv.lock`, README, license and tests. A directory can be copied
out of this collection and installed independently with `uv sync`.

For an evaluator that already loads native ARE ReAct, select that directory as
its ARE source and use the directory's `.venv/bin/python`. Keep the usual import:

```python
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

agent = are_simulation_react_json_agent(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

The returned object is the local native `BaseAgent`. Model transport, scenario
notifications, time management, judging, and trial ownership remain the caller's
responsibility. The implementation uses native logs, `custom_state`, and
`pending_step`; restore them together at the caller's request boundary.

Use a separate process/environment for each source tree: all five intentionally
use the same native `are` module namespace and distribution name. Select the
source before importing ARE. The source trees import no `bara` code.

Bara provides that process separation for its own evaluation commands. It records
actual source contents in results rather than requiring a hard-coded commit.
Bara is only the collection CLI and evaluator; it does not select factories inside
an already imported ARE process.
