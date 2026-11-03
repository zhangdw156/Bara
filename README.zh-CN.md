# better-are-react-agent

收集可运行、可追溯来源的 **ARE 原生 ReAct 增强版本**。所有入口都返回
ARE 的 `BaseAgent`，保留原生推理循环、工具执行器和调用方提供的模型接口。

[English](README.md) · [来源与重建范围](docs/SOURCES.md) · [接入约定](docs/INTEGRATION.md)

| 版本 ID | 内容 |
| --- | --- |
| `baseline` | 原生 ARE ReAct 对照组 |
| `autosaddler-appendix` | 根据附录重建通信、消歧、顺序依赖等 agent 侧提示规则 |
| `activesaddler-appendix` | 根据两个案例重建提示及有限的邮件签名、日历歧义检查 |
| `paretosaddler-i23-appendix` | 根据 I-23 变更说明重建 agent 侧策略 |
| `paretosaddler-i22-appendix` | 根据 I-22 重建效率提示和保守的最终回复转换 |
| `harnessmm-public-continuation` | 移植公开的确定性延续执行组件，最多连续复用三个动作 |

**附录重建版不是作者完整的最终 agent，也没有复现论文成绩。**论文对环境应用
工具的修改未包含在这些固定工具版本中。每个版本的已实现内容、缺失内容和来源
都记录在 `agents.json` 与来源文档中。

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
