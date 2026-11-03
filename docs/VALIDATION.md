# Validation scope

Checks are run locally; this repository has no automatic GitHub Actions workflow.

The local suites exercise the standard native factory from each independent source
directory, real ARE steps and tools with scripted responses, native builder use,
format retries, and restoration of a pending request without repeating a committed
tool. Method-specific checks cover AutoSaddler tool adaptations, ActiveSaddler
repairs, ParetoSaddler terminal conversion and HarnessMM continuation reuse.

The collection CLI is checked separately from agent implementations. Synthetic
JSON and JSONL scenarios exercise the custom evaluation CLI through a loopback
model fixture, native scenario execution and trace/report export. A dispatch check
covers the full protocol's phase configuration; it is not a full GAIA2 campaign.

No live model inference, full downloaded GAIA2 campaign, benchmark score, or SOTA
result is claimed. Native factory compatibility does not assert that every external
evaluator accepts every source deployment policy or implements exact recovery.

## Checked on 2026-11-03

The complete `uv run bara test` command passed 88 checks on Python 3.12: the CLI
suite plus the five independent source and evaluation suites. Every source also
passed native smoke and package builds. Each built wheel was checked for its local
native factory and research files; the source archives include project manifests
and lockfiles. The public HarnessMM controller's recorded content hash is preserved.

A separate copy of the HarnessMM directory, outside the collection and without
its package on the import path, passed `uv sync`, native smoke and all nine local
source tests on Python 3.13. This checks independent use of that source directory;
it is not a Python 3.13 result for every full evaluation suite.

The native HarnessMM loader also imported one scenario from the official GAIA2
`mini` / `validation` subset over the network. This checks real dataset access and
scenario import only; it is not a model inference or a complete mini evaluation.
