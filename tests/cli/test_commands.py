import json
import sys

import pytest

from bara import cli


def test_collection_discovery_does_not_import_an_agent(capsys):
    assert cli.main(["list", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert {row["method"] for row in rows} == {
        "autosaddler",
        "activesaddler",
        "paretosaddler-i23",
        "paretosaddler-i22",
        "harnessmm",
    }
    assert "are" not in sys.modules


def test_launch_uses_selected_source_and_preserves_relative_dataset_paths(monkeypatch):
    captured = {}

    def run(command, **kwargs):
        captured.update(command=command, **kwargs)
        return type("Result", (), {"returncode": 7})()

    monkeypatch.setattr(cli.subprocess, "run", run)
    monkeypatch.setenv("VIRTUAL_ENV", "/another/project/.venv")
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "/another/project/.venv")
    assert cli.main(["benchmark", "autosaddler", "--dataset", "data"]) == 7
    assert captured["command"][-3:] == ["run", "--dataset", "data"]
    assert str(cli.ROOT / "autosaddler") in captured["command"]
    assert captured["cwd"] is None
    assert "VIRTUAL_ENV" not in captured["env"]
    assert "UV_PROJECT_ENVIRONMENT" not in captured["env"]
    assert captured["env"]["PYTHONPATH"].split(":")[0] == str(cli.ROOT / "autosaddler")


def test_unknown_source_is_rejected_before_launch(monkeypatch):
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: pytest.fail("must not launch"))
    with pytest.raises(SystemExit) as exc:
        cli.main(["smoke", "missing"])
    assert exc.value.code == 2
