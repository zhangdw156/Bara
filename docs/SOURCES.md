# Sources and reconstruction coverage

Audited on 2026-11-03. These agents are evaluation candidates, not claims that a
paper's complete evolved artifact has been recovered. All environments retain the
same caller-supplied native tool set. Reconstructed policy text is newly written
from published descriptions; it is not a verbatim copy of appendix prompt tables.

## Native baseline

ARE 1.2.0, [upstream source](https://github.com/facebookresearch/meta-agents-research-environments).
The baseline calls `are_simulation_react_json_agent` with an unchanged copy of the
provided config. No policy, wrapper, additional tools, or global patch is installed.

## AutoSaddler

[Paper](https://arxiv.org/abs/2608.23041), Appendix N, Table 16;
[official optimization repository](https://github.com/microsoft/AutoSaddler).

| Published component | This variant |
| --- | --- |
| Direct factual responses | Reconstructed policy |
| Ties, singular/multiple matches, per-group ambiguity | Reconstructed policy |
| Ordered-subtask dependency boundaries | Reconstructed policy |
| Constructive email reply reminder | Reconstructed policy, not the original hook |
| Crime-rate batch, folder addresses, conversation participants, ride-history search | Not added; use existing scenario tools |
| Expanded contact-field matching | Not implemented in environment apps |
| Automatic inter-turn wait of up to 300 seconds | Not implemented; native waits remain actor-selected |
| Automatic mkdir/move parent resolution | Policy guidance only; no automatic argument rewrite |

The published table is explicitly a representative patch catalogue. Neither that
table nor the optimizer repository establishes an exact complete final snapshot.
This fixed-tool agent-side variant does not inherit the paper's 53% to 62% result.

## ActiveSaddler

[Paper](https://arxiv.org/abs/2610.00906), Appendix G, Figures 6 and 7;
[official optimization code](https://github.com/microsoft/AutoSaddler/tree/feat/activesaddler).

The appendix describes two iterative repairs, not the entire final harness.
`guards.py` independently implements their narrow public-evidence counterparts:

- A reply ending explicitly quoted by the user is appended to a single- or
  multiline draft if absent. Names and closing text are never inferred. The paper's
  general name-resolution/canonicalization trigger is unavailable.
- Before a proposed `Calendar__add_calendar_event`, an explicit one-event-per-date
  replacement request is checked against observed native calendar records and
  successful deletion receipts. Multiple cancelled originals on that date route to
  the native clarification tool before any creation occurs. Unsupported formats or
  missing evidence leave reasoning to the actor. A later user message invalidates
  the old cancellation grouping.

The reconstructed guards operate at the model-output boundary before ARE parses
and executes the action, rather than modifying the original app registration code.
Other final-harness patches, optimizer curricula, and case-specific literals are
not included. Semantic generalization beyond the documented recognizers is untested.

## ParetoSaddler

[Paper](https://arxiv.org/abs/2611.02079), Appendix J, Tables 15–17;
[official optimization code](https://github.com/microsoft/AutoSaddler/tree/feat/paretosaddler).

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

## HarnessMM

[Paper](https://arxiv.org/abs/2610.32813), especially Appendix D.5 and I.1;
[official repository](https://github.com/YuhuaJiang2002/HarnessMM), commit
`e77dfb5b768831be80c7a97855450a65404d01cb`.

`vendor/harnessmm_continuation.py` extracts `PLAN_INSTRUCTION`, `action_object`,
`fingerprint`, and `PublicContinuation` from `harnessmm/harness/gaia2_jev.py`.
Original bodies are retained. The source hash, published hash, and extraction are
recorded in `vendor/source.json`. Apache-2.0 attribution and license are retained.

The adapter uses the public non-stall configuration (`require_stall=False`) and
three-follow-up limit. Conditions are literal substrings of actual public tool
observations. New tasks, user messages, notifications, errors, or unmatched receipts
return control to the model. The same native executor runs the resulting action.
The controller does not claim semantic proof that a task is complete.

New adapter code stores controller state in `BaseAgent.custom_state` and keeps a
pending model request replayable. It does not import the upstream research runner,
patch global classes, change provider transport, or read benchmark answers.

This is an earlier public deterministic component. It does **not** contain the
later typed bank, one-token selector, fused context-v16, or the complete frozen
configuration behind the 43.96% / 639.64k-token GAIA2 result. Those results are not
assigned to this port.

## Deliberate exclusions

ERL publishes the retrieval procedure and example heuristics, but the verified
materials do not provide the full final heuristic pool. "Top 20" describes how
many heuristics to retrieve; it is not a released list of 20 final rules. An ERL
agent with a fabricated pool would not be a faithful collection item, so it is not
included. No unseen author artifacts or undisclosed behavior are reconstructed
under the guise of original source.
