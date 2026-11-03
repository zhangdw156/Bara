# Implementation and source notes

## ParetoSaddler

[Paper](https://arxiv.org/abs/2611.02079), Appendix J, Tables 15–17;
[shared optimizer repository](https://github.com/microsoft/AutoSaddler).
These reconstructions use Appendix J's change tables. The linked Pareto-specific
feature branch was unavailable at the audit date, and the tables describe file
changes and behavior rather than complete final files.

I-23 and I-22 come from **different searches**:

| Component | I-23 reconstruction | I-22 reconstruction |
| --- | --- | --- |
| Final/clarification channel, relative dates, task order | Policy | Policy where described |
| Contact, destination, calendar, email and product checks | Policy reminders | Recipient/conversation/discount/reuse reminders as policy |
| Cab-monitoring and shopping termination changes | Policy; native termination code retained | Native termination code retained |
| Terminal plain-text response conversion | None | Explicit `Final answer:` only, after observed tool activity; refusal/progress prefixes excluded |
| Application search/filter/batch/representation changes | Not implemented | Not implemented |
| Recurring-action timing | Native actor | Policy requiring the final interval |

The I-22 appendix references a monitoring tool that remains unimplemented in this
source. Application extensions beyond the policy changes are listed as omitted
in the table above.

## Native source layout

The full `are/` Python package is included locally. The standard factory remains
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research behavior lives in `are/simulation/agents/default_agent/`.
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
