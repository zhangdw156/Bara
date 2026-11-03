"""Two-argument factories matching ARE's are_simulation_react_json_agent signature."""

from .catalog import identity
from .factory import create_agent


def _registered(name):
    def decorate(factory):
        factory.agent_identity = lambda: identity(name)
        return factory
    return decorate


@_registered("baseline")
def baseline(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="baseline")


@_registered("autosaddler-appendix")
def autosaddler_appendix(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="autosaddler-appendix")


@_registered("activesaddler-appendix")
def activesaddler_appendix(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="activesaddler-appendix")


@_registered("paretosaddler-i23-appendix")
def paretosaddler_i23_appendix(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="paretosaddler-i23-appendix")


@_registered("paretosaddler-i22-appendix")
def paretosaddler_i22_appendix(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="paretosaddler-i22-appendix")


@_registered("harnessmm-public-continuation")
def harnessmm_public_continuation(llm_engine, base_agent_config):
    return create_agent(llm_engine, base_agent_config, variant="harnessmm-public-continuation")
