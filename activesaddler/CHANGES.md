# Implementation and source notes

## ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906), Appendix G, Figures 6 and 7;
[official optimization code](https://github.com/microsoft/AutoSaddler/tree/feat/activesaddler).

The appendix describes two iterative repairs, reconstructed in
`are/simulation/agents/default_agent/action_guards.py`:

- **Email closing:** append the exact ending quoted by the user when a single- or
  multiline draft lacks it. The recognizer uses literal user quotes; name resolution
  stays with the model.
- **Calendar replacement:** before `Calendar__add_calendar_event`, check an explicit
  one-event-per-date replacement request against observed calendar records and
  successful deletion receipts. Multiple cancelled originals on that date trigger
  the native clarification tool before creation. A later user message resets the
  cancellation grouping.

These guards run inside the native model step before action execution. Requests
outside the two recognizers continue through the model's normal action selection.

## Native source layout

The `are/` package exposes the native factory
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research changes live in `are/simulation/agents/default_agent/`;
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
