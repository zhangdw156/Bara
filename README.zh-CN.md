# better-are-react-agent

这是一个根据学术前沿论文整理的 **RSI 后 ARE ReAct agent 实现合集**，希望帮助
想在 GAIA2 上基于 ARE 原生 ReAct 研究递归自改进（RSI）的朋友。

我们把论文思想、附录描述和公开代码整理成可运行、可继续改进的版本，方便进行
对比评测、消融实验和进一步的 harness 演化。**这些实现不追求保真复现，不代表
作者完整的最终 agent，也不直接继承论文成绩。**

所有入口都返回 ARE 的 `BaseAgent`，保留原生推理循环、工具执行器和调用方提供
的模型接口，便于用同一种评测流程研究不同增强方法。

[English](README.md) · [来源与实现差异](docs/SOURCES.md) · [接入约定](docs/INTEGRATION.md)

| 论文 | URL | 对应实现 |
| --- | --- | --- |
| AutoSaddler | https://arxiv.org/abs/2608.23041 | `autosaddler-appendix` |
| ActiveSaddler | https://arxiv.org/abs/2610.00906 | `activesaddler-appendix` |
| ParetoSaddler | https://arxiv.org/abs/2611.02079 | I-23、I-22 两个版本 |
| HarnessMM | https://arxiv.org/abs/2610.32813 | `harnessmm-public-continuation` |

| 版本 ID | 内容 |
| --- | --- |
| `baseline` | 原生 ARE ReAct 对照组 |
| `autosaddler-appendix` | 根据附录重建通信、消歧、顺序依赖等 agent 侧提示规则 |
| `activesaddler-appendix` | 根据两个案例重建提示及有限的邮件签名、日历歧义检查 |
| `paretosaddler-i23-appendix` | 根据 I-23 变更说明重建 agent 侧策略 |
| `paretosaddler-i22-appendix` | 根据 I-22 重建效率提示和保守的最终回复转换 |
| `harnessmm-public-continuation` | 移植公开的确定性延续执行组件，最多连续复用三个动作 |

目前包含五个增强版本和一个原生基线。论文对环境应用工具的修改未包含在这些
固定工具版本中；具体实现内容、差异和来源记录在 `agents.json` 与来源文档中。

在仓库目录下安装到独立环境：

```sh
uv venv .uv-venv/better-are-react-agent --python 3.12
uv pip install --python .uv-venv/better-are-react-agent/bin/python -e '.[dev]'
.uv-venv/better-are-react-agent/bin/better-are-react-agent list
.uv-venv/better-are-react-agent/bin/better-are-react-agent smoke
```

`smoke` 使用预设模型回复，实际执行 ARE 原生步骤和工具；无需密钥，也不运行
真实模型或完整 GAIA2。正常评测时，由评测程序提供模型、场景工具和评分器。

```python
from better_are_react_agent import create_agent

agent = create_agent(llm_engine, base_agent_config,
                     variant="autosaddler-appendix")
agent.tools = scenario_tools
```

评测程序只需在创建原生 agent 的位置选择对应 factory。模型请求、成本记录、
通知和工具调用仍沿用原有原生评测流程。安装本包不会自动修改其他程序的选择。
