# better-are-react-agent

[中文说明](README.zh-CN.md)

A collection of **research reimplementations of RSI-improved ARE ReAct agents**
for researchers studying recursive self-improvement (RSI) on GAIA2.

We turn ideas and available artifacts from recent papers into runnable native
ARE ReAct variants. Use them as starting points for comparison, ablation studies,
and further harness evolution. **These are non-faithful reimplementations, not
exact reproductions of the authors' final agents or published benchmark scores.**

Every factory returns ARE's `BaseAgent` and retains its native reasoning/tool loop,
JSON executor, scenario tools, and caller-supplied model engine. This gives the
collection one consistent interface for evaluation and experimentation.

## Papers

| Paper | URL | Implementations in this repository |
| --- | --- | --- |
| AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces | https://arxiv.org/abs/2608.23041 | `autosaddler-appendix` |
| ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization | https://arxiv.org/abs/2610.00906 | `activesaddler-appendix` |
| ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost | https://arxiv.org/abs/2611.02079 | `paretosaddler-i23-appendix`, `paretosaddler-i22-appendix` |
| HarnessMM: Recursive Self-Improvement for Harness Token Efficiency | https://arxiv.org/abs/2610.32813 | `harnessmm-public-continuation` |

## Available agents

| Agent ID | Material | Implemented behavior |
| --- | --- | --- |
| `baseline` | Native ARE 1.2.0 | Unmodified factory; comparison control |
| `autosaddler-appendix` | Appendix N, Table 16 | Reconstructed communication, ambiguity, ordering, email, path, and monitoring policy |
| `activesaddler-appendix` | Appendix G, Figures 6–7 | Case-study policy, literal multiline signature repair, and a public-receipt calendar ambiguity guard |
| `paretosaddler-i23-appendix` | Appendix J, Table 16 | Agent-side policy reconstruction for the I-23 quality/cost selection |
| `paretosaddler-i22-appendix` | Appendix J, Table 17 | Agent-side efficiency/reminder policy and conservative terminal-text conversion |
| `harnessmm-public-continuation` | Pinned Apache-2.0 code | Published deterministic continuation controller, maximum three actions, with instance-local durable state |

The collection currently contains five enhanced variants and one native baseline.
Some are prompt-centered, some add guards or execution control. Environment tool
extensions from the papers are not bundled. See [source and implementation notes](docs/SOURCES.md)
for the implemented components, differences, and original code links. Each variant
is a starting point for RSI research; its performance must be measured independently.

## Install and inspect

Use a new environment from the repository root:

```sh
uv venv .uv-venv/better-are-react-agent --python 3.12
uv pip install --python .uv-venv/better-are-react-agent/bin/python -e '.[dev]'
.uv-venv/better-are-react-agent/bin/better-are-react-agent list
.uv-venv/better-are-react-agent/bin/better-are-react-agent smoke
```

The smoke command uses scripted responses and real native ARE steps and tools.
It makes no model requests, downloads no benchmark dataset, and does not measure
GAIA2 success. No provider credentials are needed.

## Use the same native factory interface

Each published factory accepts the same two arguments as
`are_simulation_react_json_agent`:

```python
from better_are_react_agent.factories import autosaddler_appendix

agent = autosaddler_appendix(llm_engine, base_agent_config)
agent.tools = scenario_tools
# Continue through the existing native ARE lifecycle.
```

Or select a variant by ID:

```python
from better_are_react_agent import create_agent

agent = create_agent(llm_engine, base_agent_config,
                     variant="harnessmm-public-continuation")
```

Factories are also exposed through the standard Python entry-point group
`are.react_agents`. An evaluator only needs to select the factory at native agent
construction. Model transport, request accounting, scenario tools, native scoring,
and records remain owned by the evaluator. Installing this package does not
monkey-patch ARE or automatically change the agent selected by another program.

[Integration contract](docs/INTEGRATION.md) · [Validation scope](docs/VALIDATION.md)
· [Third-party notices](THIRD_PARTY_NOTICES.md)

## Development

```sh
.uv-venv/better-are-react-agent/bin/python -m pytest
.uv-venv/better-are-react-agent/bin/ruff check src tests
.uv-venv/better-are-react-agent/bin/python -m build
```

Keep newly reconstructed behavior separate from exact public component ports.
Record source revisions, missing components, and deviations in the catalogue.
Use Angular-style commit messages. Do not commit credentials, private execution
records, benchmark solutions, or machine-specific paths.
