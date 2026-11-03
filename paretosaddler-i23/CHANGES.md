# Implementation and source notes

## ParetoSaddler

[Paper](https://arxiv.org/abs/2611.02079), Appendix J, Tables 15–17;
[shared optimizer repository](https://github.com/microsoft/AutoSaddler).
The Pareto-specific feature branch linked by the project page was not publicly
available at the audit date; no code from that branch is claimed here.

I-23 and I-22 come from **different searches**. They are separate selectable agents.
The tables describe changed files and behaviors; they do not supply the complete
final file contents.

| Component | I-23 reconstruction | I-22 reconstruction |
| --- | --- | --- |
| Final/clarification channel, relative dates, task order | Policy | Policy where described |
| Contact, destination, calendar, email and product checks | Policy; no identical pre-tool guard claim | Recipient/conversation/discount/reuse reminders as policy |
| Cab-monitoring and shopping termination changes | Policy; native termination code retained | Native termination code retained |
| Terminal plain-text response conversion | None | Explicit `Final answer:` only, after observed tool activity; refusal/progress prefixes excluded |
| Application search/filter/batch/representation changes | Not implemented | Not implemented |
| Recurring-action timing | Native actor | Policy requiring the final interval |

The I-22 appendix itself notes that a hook refers to an unimplemented monitoring
tool. This repository does not fabricate that tool. Missing application extensions
mean these are not exact I-23/I-22 replications.

## Native source layout

The full `are/` Python package is included locally. The standard factory remains
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research behavior is implemented in this directory, without importing the
collection CLI or a sibling agent. `SOURCE.json` records upstream provenance.

All directories include native pending-step persistence and success-aware terminal
tool handling. These common runtime fixes are separate from the paper-inspired
changes. They retain the native JSON executor, log memory and model-call contract.
