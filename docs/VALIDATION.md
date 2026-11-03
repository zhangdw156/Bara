# Validation scope

Run local checks with `uv run bara test`, `uv run bara smoke` and `uv run bara build`.

The suites exercise the native factory, real ARE steps and tools with scripted
responses, native builders, format retries, and pending-request restoration.
Method-specific checks cover AutoSaddler tool adaptations, ActiveSaddler repairs,
ParetoSaddler terminal conversion and HarnessMM continuation reuse.

Synthetic JSON and JSONL scenarios exercise the evaluation CLI through a loopback
model fixture, including native execution and trace/report export. A dispatch
check covers the full protocol's phase configuration.

## Checked on 2026-11-03

| Check | Coverage | Result |
| --- | --- | --- |
| `uv run bara test`, Python 3.12 | CLI and all five source/evaluation suites | 88 passed |
| Native smoke and package builds | All five sources | Passed; wheels contain native factories and research files, and archives include manifests and lockfiles |
| `uv sync`, smoke and local tests, Python 3.13 | HarnessMM copied outside the collection | Passed, including nine source tests |
| Official GAIA2 `mini` / `validation` import | Native HarnessMM loader, one scenario over the network | Passed |

The packaged HarnessMM controller matches its recorded public source hash.
Live model inference and complete GAIA2 evaluations have not been run.
