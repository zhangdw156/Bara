# Evaluation CLI sources

`cli.py`, `scenario_executor.py`, and `gaia2_submission.py` adapt the MIT-licensed
ARE 1.2.0 benchmark modules listed in `source.json`. The original license is in
this directory. ARE's default builders, scenario tools, judge, user simulator,
trace export, and full-protocol phase definitions are retained.

Bara selects a separate ARE source directory and interpreter before import.
There is no variant factory or entry-point registry. The evaluator adds source
content provenance, automatic output directories, JSONL input handling, a thread
default, and failure exit statuses. Agent logic remains inside each source tree.
