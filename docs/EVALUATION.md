# Evaluation with bara

From the collection root:

```sh
uv sync
uv run bara list
uv run bara smoke autosaddler
uv run bara benchmark autosaddler --help
```

`bara` selects the named source directory and runs its native ARE code in that
directory's `.venv`. The environment is synchronized automatically. Dataset and
output paths remain relative to the directory where you invoke the command.

## Read the official dataset online

Use `--hf-dataset` to stream scenarios from the public dataset at
[meta-agents-research-environments/gaia2](https://huggingface.co/datasets/meta-agents-research-environments/gaia2).
Keep network access available throughout the run. For local input, use the
[scenario JSON layout below](#use-prepared-local-data).

This example evaluates the entire `mini` subset once per scenario:

```sh
uv run bara benchmark harnessmm \
  --hf-dataset meta-agents-research-environments/gaia2 \
  --hf-config mini \
  --model openai/YOUR_MODEL \
  --provider local \
  --endpoint http://localhost:8000/v1 \
  --judge_model openai/YOUR_JUDGE_MODEL \
  --judge_endpoint http://localhost:8001/v1 \
  --num_runs 1
```

Replace the model names and endpoints with your own and configure the credentials
required by your model service. This example uses OpenAI-compatible endpoints;
the `openai/` prefix lets `--provider local` select the matching model protocol.
The judge inherits the agent's provider, but its model and endpoint are configured
separately. If both roles use the same endpoint, set both endpoint options to that
URL. For another provider, use its model naming and `--provider`; set
`--judge_provider` only if the judge uses a different provider.

| Setting | Behavior |
| --- | --- |
| `--hf-config mini` | Select the mini subset |
| `--hf-split` | Defaults to `validation` for Hub data |
| `--limit N` | Load up to N scenarios per selected configuration; defaults to the entire subset |
| `--num_runs 1` | Run each scenario once; the default is three times |
| `--max_concurrent_scenarios N` | Run up to N scenarios concurrently; otherwise ARE chooses from the CPU count |

To evaluate one capability, replace `mini` with `execution`, `search`,
`adaptability`, `time`, or `ambiguity`. These are native ARE scenarios; arbitrary
question-answer datasets need an ARE scenario implementation before evaluation.

## Use prepared local data

To evaluate local native ARE JSON scenarios, replace
`--hf-dataset ... --hf-config mini` in the example above with:

```sh
--dataset data/gaia2 --hf-config mini
```

The matching layout, relative to the directory where you invoke Bara, is:

```text
data/gaia2/
└── mini/
    ├── scenario_001.json
    └── scenario_002.json
```

The official download contains **Parquet** files. To create this layout, parse
each row's `data` field as JSON and save the resulting scenario object in a
separate `.json` file under `mini/`.

If you preserve a split directory such as `data/gaia2/mini/validation/`, also pass
`--hf-split validation`; local paths append the configuration and split only when
you explicitly supply them. Model API access is still required when using remote
models with local scenario data.

To select individual scenarios, `--dataset selection.jsonl` accepts one JSON
object per line, with a `trace_id` pointing to an existing scenario `.json` file.
Use absolute paths or paths relative to the directory where you invoke Bara:

```jsonl
{"trace_id": "data/gaia2/mini/scenario_001.json"}
{"trace_id": "data/gaia2/mini/scenario_002.json"}
```

For JSONL input, omit `--hf-config`. Use `--dataset` for local files or
`--hf-dataset` for Hub data.

## Execution behavior

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
  --hf-dataset meta-agents-research-environments/gaia2 \
  --model openai/YOUR_MODEL \
  --provider local \
  --endpoint http://localhost:8000/v1 \
  --judge_model openai/YOUR_JUDGE_MODEL \
  --judge_endpoint http://localhost:8001/v1
```

This runs ARE's full protocol: the five capability configurations plus its
Agent2Agent and noise phases on `mini`, with three repetitions per scenario.
Use `benchmark` for a mini-only evaluation or a JSONL selection. For local input,
the dataset must include all five capability directories and `mini`; replace
`--hf-dataset ...` with `--dataset data/gaia2`. The Agent2Agent phase also makes
model calls for the app agents.

## Results and judging

Results default to `runs/<source>/<timestamp>/`; set `--output_dir` to choose a path.
Results include native traces, `benchmark_stats.json`, and `agent_source.json`
recording the selected method, paper, upstream provenance and actual source digest.
Each output directory belongs to one source; its digest identifies the code used
for that evaluation, including local edits.

For offline judging of native exported traces:

```sh
uv run bara judge autosaddler --dataset path/to/exported-traces --help
```

## Local checks

```sh
uv run bara smoke
uv run bara test
uv run bara build
```

These operate on all five source directories. Add a directory name to check just
one. Smoke and tests run offline using scripted responses and synthetic local
scenarios.
