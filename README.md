<div align="center">

<img src="assets/readme/hero.svg" width="100%" alt="Bara · RSI research on GAIA2">

<h3>One directory. One evolved ARE ReAct source tree.</h3>

<p>Read the code. Run the agent. Build your next iteration.</p>

<p>
<a href="https://github.com/facebookresearch/meta-agents-research-environments"><img src="https://img.shields.io/badge/Native-ARE_1.2.0-2d6b59?style=for-the-badge&amp;labelColor=193b32" alt="Native ARE 1.2.0"></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.12_%7C_3.13-344b5b?style=for-the-badge&amp;logo=python&amp;logoColor=white&amp;labelColor=253642" alt="Python 3.12 and 3.13"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-b37d29?style=for-the-badge&amp;labelColor=684c23" alt="MIT license; upstream component notices below"></a>
</p>

<p><a href="#collection"><b>Agent sources</b></a> &nbsp; · &nbsp; <a href="#quick-start"><b>Quick start</b></a> &nbsp; · &nbsp; <a href="#data"><b>Data & evaluation</b></a> &nbsp; · &nbsp; <a href="#papers"><b>Papers</b></a> &nbsp; · &nbsp; <a href="README.zh-CN.md"><b>中文说明</b></a></p>

</div>

**Bara** (Better ARE ReAct Agent) collects five ARE ReAct research reimplementations
based on public code and appendices from four recursive self-improvement papers.
**Each agent directory is an installable ARE project** for studying, evaluating
and developing agent variants.

<a id="collection"></a>

## 🧩 Agent source collection

<table>
<tr>
<td width="50%" valign="top">
<h3>🛠️ AutoSaddler</h3>
<p><sub><b>TASK POLICY & TOOL ALGORITHMS</b></sub></p>
<p>Communication, ambiguity, ordering and public search/batch adaptations.</p>
<p><a href="autosaddler/"><b>Open source →</b></a> &nbsp; · &nbsp; <a href="https://arxiv.org/abs/2608.23041">Paper ↗</a></p>
</td>
<td width="50%" valign="top">
<h3>🧭 ActiveSaddler</h3>
<p><sub><b>ACTION REPAIRS</b></sub></p>
<p>Email signature and calendar ambiguity repairs inside the native model step.</p>
<p><a href="activesaddler/"><b>Open source →</b></a> &nbsp; · &nbsp; <a href="https://arxiv.org/abs/2610.00906">Paper ↗</a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>⚖️ ParetoSaddler</h3>
<p><sub><b>QUALITY & COST</b></sub></p>
<p>Two independent source trees from different searches, with task policies and terminal handling.</p>
<p><a href="paretosaddler-i23/"><b>I-23 source →</b></a> &nbsp; · &nbsp; <a href="paretosaddler-i22/"><b>I-22 source →</b></a> &nbsp; · &nbsp; <a href="https://arxiv.org/abs/2611.02079">Paper ↗</a></p>
</td>
<td width="50%" valign="top">
<h3>🔁 HarnessMM</h3>
<p><sub><b>DECISION REUSE</b></sub></p>
<p>Public deterministic continuation when native tool feedback matches planned conditions.</p>
<p><a href="harnessmm/"><b>Open source →</b></a> &nbsp; · &nbsp; <a href="https://arxiv.org/abs/2610.32813">Paper ↗</a></p>
</td>
</tr>
</table>

```text
Bara/
├── autosaddler/
├── activesaddler/
├── paretosaddler-i23/
├── paretosaddler-i22/
├── harnessmm/
└── src/bara/                 # CLI and evaluation tools
```

Every agent directory contains `are/`, `pyproject.toml`, `uv.lock`, `README.md`,
`CHANGES.md`, and tests. It can be copied and installed independently. Research
code lives in its own `are/simulation/agents/default_agent/`; `src/bara/` provides
the collection CLI and evaluation tools. [Use a source with an existing evaluator →](docs/USAGE.md)

<a id="quick-start"></a>

## 🚀 Quick start

From the collection root:

```sh
uv sync
uv run bara list
uv run bara smoke autosaddler
```

The smoke check runs offline using scripted model responses and native ARE tools.
Bara automatically prepares the selected directory's `.venv`.

| Command | Purpose |
| --- | --- |
| `uv run bara benchmark autosaddler --help` | Dataset evaluation options |
| `uv run bara gaia2 harnessmm --help` | Full GAIA2 protocol options |
| `uv run bara judge autosaddler --help` | Offline judging options |
| `uv run bara smoke` | Offline smoke for every source |
| `uv run bara test` | Local source and evaluation tests |
| `uv run bara build` | Build each independent ARE package |

<a id="data"></a>

## 🗂️ Data & mini evaluation

Use `--hf-dataset` to read the
[official GAIA2 dataset](https://huggingface.co/datasets/meta-agents-research-environments/gaia2)
during evaluation. Scenarios stream from Hugging Face, so keep network access
available throughout the run.

To run the entire `mini` subset once per scenario, use the example below with your
model names, endpoints and service credentials. The example uses OpenAI-compatible
agent and judge endpoints; the judge inherits `--provider local`.

```sh
uv run bara benchmark harnessmm \
  --hf-dataset meta-agents-research-environments/gaia2 \
  --hf-config mini \
  --model openai/YOUR_MODEL \
  --provider local \
  --endpoint http://localhost:8000/v1 \
  --judge_model openai/YOUR_JUDGE_MODEL \
  --judge_endpoint http://localhost:8001/v1 \
  --num_runs 1
```

The split defaults to `validation`. Omitting `--limit` runs the entire selected
subset; `--num_runs 1` runs each scenario once, while the default is three times.
Replace `harnessmm` with any other source directory to evaluate that implementation.
Results go to `runs/<source>/<timestamp>/` automatically.

For local dataset input, `--dataset` accepts native ARE scenario JSON files in a
directory or a JSONL list of paths. To use local Parquet data, export each row's
`data` field as a scenario JSON file. Use `uv run bara gaia2 <source>` for the full
protocol, including Agent2Agent and noise phases.

[Local data layout, model settings and full protocol →](docs/EVALUATION.md)

## 🔌 Native ARE interface

Each source exposes the native factory:

```python
from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

agent = are_simulation_react_json_agent(llm_engine, base_agent_config)
agent.tools = scenario_tools
```

Select the source directory and its environment before importing ARE. The factory
returns a native `BaseAgent`. Bara's evaluator uses the selected source's builders,
tools, user simulator and judge. See the [integration guide](docs/USAGE.md) for use
with an existing evaluator.

<a id="papers"></a>

## 📚 Papers & sources

- **[AutoSaddler](https://arxiv.org/abs/2608.23041)** — Automatic Harness Optimization with Durable Updates from Agent Execution Traces.
- **[ActiveSaddler](https://arxiv.org/abs/2610.00906)** — Automated Curriculum Learning for Agent Harness Optimization.
- **[ParetoSaddler](https://arxiv.org/abs/2611.02079)** — Pareto-Guided Optimization of Agent Harnesses for Quality and Cost.
- **[HarnessMM](https://arxiv.org/abs/2610.32813)** — Recursive Self-Improvement for Harness Token Efficiency.

Per-directory source manifests and implementation notes distinguish public code
ports from appendix reconstructions. [Source coverage →](docs/SOURCES.md)

<details>
<summary><b>Local validation and contribution</b></summary>

Tests exercise native execution, pending-request recovery, method-specific behavior,
and synthetic dataset evaluation. [Validation scope →](docs/VALIDATION.md)

Add a new implementation as an independent ARE source directory with a paper URL,
source manifest and documented differences. Keep the native factory interface.
Use Angular-style commit messages.

</details>

---

<p align="center"><sub>Built for open RSI research · <a href="LICENSE">MIT</a> · HarnessMM controller: Apache-2.0 · <a href="THIRD_PARTY_NOTICES.md">Attribution & licenses</a></sub></p>
