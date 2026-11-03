# better-are-react-agent

[中文说明](README.zh-CN.md)

Runnable, source-traceable research variants of **ARE's native ReAct agent**.
Every factory returns ARE's `BaseAgent` and retains its native reasoning/tool loop,
JSON executor, scenario tools, and caller-supplied model engine.

This repository collects a public HarnessMM component and **partial agent-side
reconstructions** from AutoSaddler, ActiveSaddler, and ParetoSaddler appendices.
The reconstructions are independent implementations, **not the authors' complete
final agents or reproductions of their published scores**. Several papers modify
environment application tools; those changes are outside these fixed-tool variants.

| Agent ID | Material | Implemented behavior |
| --- | --- | --- |
| `baseline` | Native ARE 1.2.0 | Unmodified factory; comparison control |
| `autosaddler-appendix` | Appendix N, Table 16 | Reconstructed communication, ambiguity, ordering, email, path, and monitoring policy |
| `activesaddler-appendix` | Appendix G, Figures 6–7 | Case-study policy, literal multiline signature repair, and a public-receipt calendar ambiguity guard |
| `paretosaddler-i23-appendix` | Appendix J, Table 16 | Agent-side policy reconstruction for the I-23 quality/cost selection |
| `paretosaddler-i22-appendix` | Appendix J, Table 17 | Agent-side efficiency/reminder policy and conservative terminal-text conversion |
| `harnessmm-public-continuation` | Pinned Apache-2.0 code | Published deterministic continuation controller, maximum three actions, with instance-local durable state |

See [source and coverage notes](docs/SOURCES.md) for what each variant does and
what remains unavailable. Published method names identify the source of the ideas,
not an endorsement or a benchmark result for this implementation.

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
