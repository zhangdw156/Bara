# Implementation and source notes

## ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906), Appendix G, Figures 6 and 7;
[official optimization code](https://github.com/microsoft/AutoSaddler/tree/feat/activesaddler).

The appendix describes two iterative repairs, not the entire final harness.
`are/simulation/agents/default_agent/action_guards.py` independently implements their narrow public-evidence counterparts:

- A reply ending explicitly quoted by the user is appended to a single- or
  multiline draft if absent. Names and closing text are never inferred. The paper's
  general name-resolution/canonicalization trigger is unavailable.
- Before a proposed `Calendar__add_calendar_event`, an explicit one-event-per-date
  replacement request is checked against observed native calendar records and
  successful deletion receipts. Multiple cancelled originals on that date route to
  the native clarification tool before any creation occurs. Unsupported formats or
  missing evidence leave reasoning to the actor. A later user message invalidates
  the old cancellation grouping.

The reconstructed guards run inside this source tree's native model step before the action is executed.
Other final-harness patches, optimizer curricula, and case-specific literals are
not included. Semantic generalization beyond the documented recognizers is untested.

## Native source layout

The full `are/` Python package is included locally. The standard factory remains
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research behavior is implemented in this directory, without importing the
collection CLI or a sibling agent. `SOURCE.json` records upstream provenance.

All directories include native pending-step persistence and success-aware terminal
tool handling. These common runtime fixes are separate from the paper-inspired
changes. They retain the native JSON executor, log memory and model-call contract.
