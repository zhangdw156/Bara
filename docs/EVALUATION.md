# Evaluation with bara

From the collection root:

```sh
uv sync
uv run bara list
uv run bara smoke autosaddler
uv run bara benchmark autosaddler --help
```

`bara` selects the named source directory and runs its native ARE code in that
directory's `.venv`. The environment is synchronized automatically. You do not
need to activate it, install an agent plugin, or register a factory. Dataset and
output paths remain relative to the directory where you invoke the command.

## Run a dataset

```sh
uv run bara benchmark autosaddler \
  --dataset data/gaia2 \
  --hf-config mini \
  --model YOUR_MODEL \
  --provider local \
  --endpoint http://localhost:8000/v1 \
  --num_runs 1 \
  --limit 5
```

Use your provider's normal credentials and endpoint. `--dataset` accepts native
ARE JSON scenario directories or JSONL scenario listings. An extracted directory
must contain the selected configuration, such as `data/gaia2/mini/`. For a Hub
dataset, replace `--dataset` with `--hf-dataset` and choose `--hf-config` and
`--hf-split`. These commands do not invent a local dataset or silently download
one when a local path was requested.

The same command works with any of the five source directory names. The runner
uses that source's standard `AgentConfigBuilder`, `AgentBuilder`, scenario tools,
user simulator and judge. The native internal agent name remains `default`; the
selected research implementation comes from its source directory.

The default executor uses threads. `--executor_type process` requests the native
process executor; platform-specific process behavior follows ARE. The native
model, judge, concurrency, timeout, time-mode and export options are listed in
`--help`. Missing datasets and scenario execution exceptions produce a failing
exit status. An incorrect task answer is reported as an evaluation result.

## Full GAIA2 protocol

```sh
uv run bara gaia2 harnessmm \
  --dataset data/gaia2 \
  --model YOUR_MODEL \
  --provider local \
  --endpoint http://localhost:8000/v1
```

This retains ARE's full protocol: the five capability configurations plus its
Agent2Agent and noise phases, with three repetitions per scenario. The dataset
must contain the protocol's capability subsets; use `benchmark` for a mini set or
JSONL listing. This is a real evaluation command and can make model calls.

## Results and judging

Without `--output_dir`, each invocation creates `runs/<source>/<timestamp>/`.
Results include native traces, `benchmark_stats.json`, and `agent_source.json`
recording the selected method, paper, upstream provenance and actual source digest.
An output directory already owned by a different source is rejected. This records
edited research sources without restricting them to a particular commit.

For offline judging of native exported traces:

```sh
uv run bara judge autosaddler --dataset path/to/exported-traces --help
```

Hub upload occurs only when explicitly requested with the native upload option.
No benchmark score is claimed for any reconstruction in this collection.

## Local checks

```sh
uv run bara smoke
uv run bara test
uv run bara build
```

These operate on all five source directories. Add a directory name to check just
one. Smoke and tests use scripted responses and synthetic local scenarios, with
no paid model calls. No GitHub Actions workflow is configured.
