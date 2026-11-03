<div align="center">

<img src="assets/readme/hero.svg" width="100%" alt="Better ARE ReAct Agent · RSI research on GAIA2">

<h3>面向 GAIA2 的 RSI 研究，从原生 ARE ReAct 出发。</h3>

<p>读论文、跑实现、做对比，继续改进你的 agent。</p>

<p>
<a href="https://github.com/facebookresearch/meta-agents-research-environments"><img src="https://img.shields.io/badge/Native-ARE_1.2.0-2d6b59?style=for-the-badge&amp;labelColor=193b32" alt="Native ARE 1.2.0"></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.12_%7C_3.13-344b5b?style=for-the-badge&amp;logo=python&amp;logoColor=white&amp;labelColor=253642" alt="Python 3.12 and 3.13"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-b37d29?style=for-the-badge&amp;labelColor=684c23" alt="MIT license; upstream component notices below"></a>
</p>

<p>
<a href="#collection"><b>实现合集</b></a>
&nbsp; · &nbsp;
<a href="#quick-start"><b>快速开始</b></a>
&nbsp; · &nbsp;
<a href="#papers"><b>论文与来源</b></a>
&nbsp; · &nbsp;
<a href="README.md"><b>English</b></a>
</p>

</div>

**Better ARE ReAct Agent** 根据前沿论文，收集 RSI 后 ARE ReAct agent 的可运行实现，
希望帮助在 **GAIA2** 上研究递归自改进的朋友开展对比评测、消融实验和进一步的 harness 演化。

> [!NOTE]
> **非保真实现，作为研究起点。** 这些版本不代表作者完整的最终 agent，也不直接继承论文成绩。[查看实现范围与差异 →](docs/SOURCES.md)

<a id="collection"></a>

## 🧩 实现合集

四篇论文、五个增强版本，以及一个保持原样的原生基线。

<table>
<tr>
<td width="50%" valign="top">
<h3>🛠️ AutoSaddler</h3>
<p><sub><b>提示与任务策略</b></sub></p>
<p>通信、消歧与子任务顺序。从提示规则入手，研究 agent 如何遵循任务约束。</p>
<p><a href="https://arxiv.org/abs/2608.23041"><b>论文 ↗</b></a> &nbsp; · &nbsp; <a href="docs/SOURCES.md#autosaddler">实现说明 →</a></p>
</td>
<td width="50%" valign="top">
<h3>🧭 ActiveSaddler</h3>
<p><sub><b>执行前检查</b></sub></p>
<p>根据案例重建邮件签名与日历歧义检查，在原生工具执行前修正特定错误。</p>
<p><a href="https://arxiv.org/abs/2610.00906"><b>论文 ↗</b></a> &nbsp; · &nbsp; <a href="docs/SOURCES.md#activesaddler">实现说明 →</a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>⚖️ ParetoSaddler</h3>
<p><sub><b>质量与成本</b></sub></p>
<p>I-23、I-22 两个 agent 侧版本，便于比较任务策略与面向效率的行为调整。</p>
<p><a href="https://arxiv.org/abs/2611.02079"><b>论文 ↗</b></a> &nbsp; · &nbsp; <a href="docs/SOURCES.md#paretosaddler">实现说明 →</a></p>
</td>
<td width="50%" valign="top">
<h3>🔁 HarnessMM</h3>
<p><sub><b>决策复用</b></sub></p>
<p>移植公开的延续执行组件，在工具反馈满足条件时复用已经确定的后续动作。</p>
<p><a href="https://arxiv.org/abs/2610.32813"><b>论文 ↗</b></a> &nbsp; · &nbsp; <a href="docs/SOURCES.md#harnessmm">实现说明 →</a></p>
</td>
</tr>
</table>

<details>
<summary><b>查看全部六个 agent ID</b></summary>

| Agent ID | 实现内容 |
| --- | --- |
| `baseline` | 原生 ARE ReAct 对照组 |
| `autosaddler-appendix` | AutoSaddler 的 agent 侧提示策略 |
| `activesaddler-appendix` | ActiveSaddler 案例策略及执行前检查 |
| `paretosaddler-i23-appendix` | ParetoSaddler I-23 策略 |
| `paretosaddler-i22-appendix` | ParetoSaddler I-22 策略及最终回复转换 |
| `harnessmm-public-continuation` | HarnessMM 公开的确定性延续执行组件 |

使用 `baseline` 作为原生对照。各版本使用相同的场景工具集，不包含论文对环境应用工具的扩展。

</details>

<a id="quick-start"></a>

## 🚀 快速开始

在仓库目录下创建独立环境，安装并运行离线检查：

```sh
uv venv .uv-venv/better-are-react-agent --python 3.12
uv pip install --python .uv-venv/better-are-react-agent/bin/python -e .
.uv-venv/better-are-react-agent/bin/better-are-react-agent smoke
```
检查使用预设回复，实际执行 ARE 原生步骤和工具。无需 API 密钥或下载 benchmark，
也不代表真实模型的 GAIA2 成绩。

## 🔌 同一接口，切换不同版本

创建原生 agent 时选择实现：

```python
from better_are_react_agent import create_agent

agent = create_agent(
    llm_engine,
    base_agent_config,
    variant="harnessmm-public-continuation",
)
agent.tools = scenario_tools
```
所有版本都返回 ARE 的 **`BaseAgent`**，保留原生推理循环和 JSON 工具执行器。
模型接口、场景工具、通知、时钟和评分由评测程序提供。

<details>
<summary><b>原生 factory 接口与入口发现</b></summary>

具名 factory 与 `are_simulation_react_json_agent` 使用相同的两个参数：

```python
from better_are_react_agent.factories import autosaddler_appendix

agent = autosaddler_appendix(llm_engine, base_agent_config)
```

各版本注册在 Python 的 `are.react_agents` entry-point group 中。安装本包不会自动
修改其他程序的 agent 选择。入口发现、内容标识和恢复状态见[接入约定](docs/INTEGRATION.md)。

</details>

<a id="papers"></a>

## 📚 论文与来源

合集参考以下论文。在研究中使用对应思想或实现时，请引用原始工作。

- **[AutoSaddler](https://arxiv.org/abs/2608.23041)** — Automatic Harness Optimization with Durable Updates from Agent Execution Traces. [arXiv:2608.23041](https://arxiv.org/abs/2608.23041)
- **[ActiveSaddler](https://arxiv.org/abs/2610.00906)** — Automated Curriculum Learning for Agent Harness Optimization. [arXiv:2610.00906](https://arxiv.org/abs/2610.00906)
- **[ParetoSaddler](https://arxiv.org/abs/2611.02079)** — Pareto-Guided Optimization of Agent Harnesses for Quality and Cost. [arXiv:2611.02079](https://arxiv.org/abs/2611.02079)
- **[HarnessMM](https://arxiv.org/abs/2610.32813)** — Recursive Self-Improvement for Harness Token Efficiency. [arXiv:2610.32813](https://arxiv.org/abs/2610.32813)

原始仓库、附录位置、已实现内容与缺失部分，均列在[来源说明](docs/SOURCES.md)中。

## ✅ 验证与开发

<a href="https://github.com/zhangdw156/better-are-react-agent/actions/workflows/test.yml"><img src="https://github.com/zhangdw156/better-are-react-agent/actions/workflows/test.yml/badge.svg" alt="原生 agent 检查"></a>

已检查原生工具执行、不同版本的状态隔离、延续动作复用、新通知使旧计划失效，以及控制器
状态恢复。CI 覆盖 **Python 3.12、3.13**，目前未报告真实模型 benchmark 成绩。
[查看验证范围 →](docs/VALIDATION.md)

<details>
<summary><b>运行开发检查</b></summary>

```sh
uv pip install --python .uv-venv/better-are-react-agent/bin/python -e '.[dev]'
.uv-venv/better-are-react-agent/bin/python -m pytest
.uv-venv/better-are-react-agent/bin/ruff check src tests
.uv-venv/better-are-react-agent/bin/python -m build
```

添加新版本时，请记录论文来源、实现选择和差异，并区分公开组件移植与重建版本。
提交信息使用 Angular 风格。

</details>

---

<p align="center">
<sub>为开放 RSI 研究而构建 · <a href="LICENSE">MIT</a> · HarnessMM 组件：Apache-2.0 · <a href="THIRD_PARTY_NOTICES.md">来源与许可</a></sub>
</p>
