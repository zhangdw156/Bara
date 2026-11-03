# Implementation and source notes

## ParetoSaddler

[Paper](https://arxiv.org/abs/2611.02079), Appendix J, Tables 15–17;
[shared optimizer repository](https://github.com/microsoft/AutoSaddler).
These variants reconstruct policies and terminal handling from Appendix J's
change tables.

I-23 and I-22 come from **different searches**:

| Component | I-23 reconstruction | I-22 reconstruction |
| --- | --- | --- |
| Final/clarification channel, relative dates, task order | Policy | Policy where described |
| Contact, destination, calendar, email and product checks | Policy reminders | Recipient/conversation/discount/reuse reminders as policy |
| Cab-monitoring and shopping termination changes | Policy; native termination code retained | Native termination code retained |
| Terminal plain-text response conversion | Native JSON action format | Explicit `Final answer:` after observed tool activity, with refusal/progress prefix checks |
| Application search/filter/batch/representation | Native ARE application behavior | Native ARE application behavior |
| Recurring-action timing | Native actor | Policy requiring the final interval |

I-22 handles recurring actions through model-selected native calls and a policy
reminder to complete the final interval.

## Native source layout

The `are/` package exposes the native factory
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research changes live in `are/simulation/agents/default_agent/`;
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
