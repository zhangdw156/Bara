# Validation scope

Local validation on 2026-11-03 uses an isolated Python 3.12 environment and the
published ARE 1.2.0 distribution. It does not change other environments.

The checks exercise:

- Every installed factory returning the actual native `BaseAgent`, retaining
  `BaseAgent.step`, and executing native read/reply tools with scripted responses.
- An unchanged baseline prompt/config/engine and independent variant instances.
- A HarnessMM continuation executing a second native action without another model
  callback, then invalidation when the user changes the task.
- JSON round trips of a queued continuation and a pending provider-call state,
  including exact reuse of the prepared request and source-identity rejection.
- Signature repair reaching the real native tool executor, calendar ambiguity
  prevention from successful public deletion receipts, and non-intervention on
  failed deletions, missing tools, or a later user clarification.
- Conservative terminal-text conversion and preservation of progress/refusal text.
- Entry-point discovery and content identities, CLI smoke execution, source lint,
  and building an installable wheel/source distribution.

These are offline behavior/integration checks, not real-model experiments. No
GAIA2 task dataset, hidden state, judge, or paid model endpoint is used. There is
no success-rate, token-saving, or SOTA claim. Native simulated-time waits, live
user simulation, full host recovery, Linux/container execution, and complete
benchmark campaigns require separate validation. The GitHub workflow defines
Python 3.12/3.13 checks; its existence alone is not evidence that they have run.
