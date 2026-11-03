import json
import os
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.data_handler.exporter import JsonScenarioExporter
from are.simulation.environment import Environment, EnvironmentConfig
from are.simulation.scenarios.scenario import Scenario
from are.simulation.types import EventRegisterer, EventType
from click.testing import CliRunner

from bara.benchmark import cli, gaia2_submission

SOURCE = Path(os.environ["BARA_AGENT_ROOT"])
METHOD = json.loads((SOURCE / "SOURCE.json").read_text())["method"]


def action(name, args):
    return "Thought: Execute the fixture step.\nAction:\n" + json.dumps(
        {"action": name, "action_input": args}
    )


def make_dataset(directory, count=1):
    folder = directory / "mini"
    folder.mkdir(parents=True)
    for number in range(count):
        aui = AgentUserInterface()
        with EventRegisterer.capture_mode():
            request = aui.send_message_to_agent(content="Reply with the word ready.")
        request.with_type(EventType.USER).depends_on(delay_seconds=0)
        scenario = Scenario(
            scenario_id=f"cli_fixture_{number}",
            apps=[aui],
            events=[request],
            start_time=0,
            duration=20,
            nb_turns=1,
        )
        scenario.initialize()
        exported = JsonScenarioExporter().export_to_json(
            env=Environment(EnvironmentConfig(start_time=0)),
            scenario=scenario,
            scenario_id=scenario.scenario_id,
            runner_config=None,
        )
        (folder / f"{number}.json").write_text(exported)


@pytest.fixture
def model_server(monkeypatch):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            requests.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            response = {
                "id": "offline-fixture",
                "object": "chat.completion",
                "created": 0,
                "model": "offline-fixture",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": action(
                                "AgentUserInterface__send_message_to_user", {"content": "ready"}
                            ),
                        },
                    }
                ],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }
            payload = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    monkeypatch.setenv("OPENAI_API_KEY", "offline-fixture")
    monkeypatch.setenv("no_proxy", "*")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("source_kind", ["directory", "jsonl"])
def test_cli_local_dataset_to_export(tmp_path, model_server, source_kind):
    executor, count = "thread", 1
    endpoint, requests = model_server
    dataset, output = tmp_path / "dataset", tmp_path / "results"
    make_dataset(dataset, count)
    if source_kind == "jsonl":
        listing = tmp_path / "scenarios.jsonl"
        listing.write_text(json.dumps({"trace_id": str(dataset / "mini/0.json")}) + "\n")
        source_args = ["--dataset", str(listing)]
        result_folder = "local"
    else:
        source_args = ["--dataset", str(dataset), "--hf-config", "mini"]
        result_folder = "mini"
    previous_signal = signal.getsignal(signal.SIGINT)
    try:
        result = CliRunner().invoke(
            cli.main,
            [
                *source_args,
                "--model",
                "openai/offline-fixture",
                "--provider",
                "local",
                "--endpoint",
                endpoint,
                "--judge_provider",
                "mock",
                "--num_runs",
                "1",
                "--executor_type",
                executor,
                "--max_concurrent_scenarios",
                str(count),
                "--scenario_timeout",
                "30",
                "--output_dir",
                str(output),
                "--log-level",
                "ERROR",
            ],
        )
    finally:
        signal.signal(signal.SIGINT, previous_signal)
    assert result.exit_code == 0, result.output + repr(result.exception)
    assert len(requests) == count
    manifest = json.loads((output / "agent_source.json").read_text())
    assert manifest["method"] == METHOD
    rows = [
        json.loads(row)
        for row in (output / result_folder / "output.jsonl").read_text().splitlines()
    ]
    assert len(rows) == count
    assert all(not row["metadata"]["has_exception"] for row in rows), rows
    assert (output / "benchmark_stats.json").exists()
    for row in rows:
        trace = json.loads(open(row["trace_id"]).read())
        assert "ready" in json.dumps(trace)
    policy_file = SOURCE / "are/simulation/agents/default_agent/research_policy.md"
    if policy_file.is_file():
        assert policy_file.read_text() in requests[0]["messages"][0]["content"]


def test_full_suite_dispatches_selected_agent_everywhere(tmp_path, monkeypatch):
    from are.simulation.scenarios.config import MultiScenarioRunnerConfig
    from are.simulation.scenarios.validation_result import MultiScenarioValidationResult

    calls = []

    def capture(**kwargs):
        calls.append(kwargs)
        return MultiScenarioValidationResult(run_config=MultiScenarioRunnerConfig())

    monkeypatch.setattr(gaia2_submission, "run_dataset", capture)
    monkeypatch.setattr(gaia2_submission, "generate_submission_summary", lambda *args: None)
    monkeypatch.setattr(cli, "generate_and_save_reports", lambda *args: None)
    result = CliRunner().invoke(
        cli.main,
        [
            "--dataset",
            str(tmp_path),
            "--output_dir",
            str(tmp_path / "output"),
            "--log-level",
            "ERROR",
        ],
        obj={"mode": "gaia2-run"},
    )

    assert result.exit_code == 0, result.output + repr(result.exception)
    assert len(calls) == 7
    assert all(row["agent"] == "default" for row in calls)
    assert [row["phase_name"] for row in calls] == ["standard"] * 5 + ["agent2agent", "noise"]
    assert all(row["num_runs"] == 3 for row in calls)


def test_missing_dataset_is_failure(tmp_path):
    result = CliRunner().invoke(
        cli.main,
        [
            "--dataset",
            str(tmp_path / "missing"),
            "--hf-config",
            "mini",
            "--output_dir",
            str(tmp_path / "results"),
            "--log-level",
            "ERROR",
        ],
    )
    assert result.exit_code != 0
    assert "Failed configurations" in result.output


def test_scenario_exception_is_not_a_successful_cli_exit(tmp_path, monkeypatch):
    from are.simulation.scenarios.config import MultiScenarioRunnerConfig
    from are.simulation.scenarios.validation_result import (
        MultiScenarioValidationResult,
        ScenarioValidationResult,
    )

    report = MultiScenarioValidationResult(run_config=MultiScenarioRunnerConfig())
    report.add_result(
        ScenarioValidationResult(success=False, exception=RuntimeError("worker died")), "fixture", 1
    )
    monkeypatch.setattr(cli, "run_dataset", lambda **kwargs: report)
    monkeypatch.setattr(cli, "generate_and_save_reports", lambda *args: None)
    result = CliRunner().invoke(
        cli.main,
        [
            "--dataset",
            str(tmp_path),
            "--hf-config",
            "mini",
            "--output_dir",
            str(tmp_path / "results"),
            "--log-level",
            "ERROR",
        ],
    )
    assert result.exit_code == 1
    assert "Failed configurations: mini" in result.output


def test_bara_command_uses_the_selected_source_and_caller_paths(tmp_path, model_server):
    import subprocess

    from bara.cli import ROOT

    endpoint, requests = model_server
    make_dataset(tmp_path / "dataset")
    result = subprocess.run([
        "uv", "run", "--project", str(ROOT), "bara", "benchmark", SOURCE.name,
        "--dataset", "dataset", "--hf-config", "mini", "--output_dir", "results",
        "--model", "openai/offline-fixture", "--provider", "local", "--endpoint", endpoint,
        "--judge_provider", "mock", "--num_runs", "1", "--max_concurrent_scenarios", "1",
        "--scenario_timeout", "30", "--log-level", "ERROR",
    ], cwd=tmp_path, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((tmp_path / "results/agent_source.json").read_text())
    assert manifest["method"] == METHOD
    assert len(requests) == 1
    assert (tmp_path / "results/benchmark_stats.json").is_file()
