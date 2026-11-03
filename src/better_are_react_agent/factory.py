"""Create a native BaseAgent; the caller owns tools, model transport, and evaluation."""

from .catalog import describe, identity, policy


def create_agent(llm_engine, base_agent_config, *, variant="baseline"):
    from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent

    from .runtime import STATE_KEY, VariantEngine

    describe(variant)
    extra = policy(variant)
    config = base_agent_config.model_copy(deep=True)
    if extra:
        config.system_prompt = str(config.system_prompt) + "\n\n" + extra
    agent = are_simulation_react_json_agent(llm_engine, config)
    if variant != "baseline":
        agent.custom_state[STATE_KEY] = {"identity": identity(variant)}
        if variant in {"harnessmm-public-continuation", "activesaddler-appendix",
                       "paretosaddler-i22-appendix"}:
            agent.llm_engine = VariantEngine(agent, llm_engine, variant)
    return agent
