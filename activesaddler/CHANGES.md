# Implementation and source notes

## ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906), Appendix G, Figures 6 and 7;
[official optimization code](https://github.com/microsoft/AutoSaddler/tree/feat/activesaddler).

The appendix describes two iterative repairs, reconstructed in
`are/simulation/agents/default_agent/action_guards.py`:

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
Research behavior lives in `are/simulation/agents/default_agent/`.
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
