"""Select an independent ARE project, then run its native code in its own environment."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def projects():
    return {
        path.name: path
        for path in sorted(ROOT.iterdir())
        if path.is_dir()
        and (path / "SOURCE.json").is_file()
        and (path / "are/simulation/agents/default_agent/agent_factory.py").is_file()
    }


def select(name):
    available = projects()
    if name not in available:
        raise ValueError(f"Unknown source directory {name!r}. Choose: {', '.join(available)}")
    return available[name]


def launch(name, operation, arguments=()):
    source = select(name)
    env = os.environ.copy()
    # Each source tree owns .venv; an activated collection environment must not
    # redirect uv into another project's interpreter.
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_PROJECT_ENVIRONMENT", None)
    env["PYTHONPATH"] = os.pathsep.join((str(source), str(ROOT / "src")))
    env["BARA_AGENT_ROOT"] = str(source)
    env["BARA_COMMAND"] = f"bara {operation} {name}"
    env.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    prefix = ["uv", "run", "--project", str(source)]
    if operation in {"benchmark", "gaia2", "judge"}:
        mode = {"benchmark": "run", "gaia2": "gaia2-run", "judge": "judge"}[operation]
        command = [*prefix, "python", "-m", "bara.benchmark", mode, *arguments]
        # Dataset and output arguments remain relative to the caller's directory.
        cwd = None
    elif operation == "smoke":
        command = [*prefix, "python", str(source / "smoke.py")]
        cwd = source
    elif operation == "test":
        command = [
            *prefix,
            "python",
            "-m",
            "pytest",
            "-q",
            str(source / "tests"),
            str(ROOT / "tests/benchmark"),
            *arguments,
        ]
        cwd = source
    elif operation == "build":
        command = ["uv", "build", "--project", str(source)]
        cwd = source
    else:
        raise ValueError(f"Unknown operation: {operation}")
    return subprocess.run(command, cwd=cwd, env=env).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="bara", description="Independent ARE ReAct source collection."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List available source directories")
    listing.add_argument("--json", action="store_true", help="Print source manifests as JSON")
    for name, description in (
        ("benchmark", "Evaluate a dataset with one source directory"),
        ("gaia2", "Run the full GAIA2 evaluation protocol"),
        ("judge", "Judge previously exported traces"),
    ):
        command = commands.add_parser(name, help=description)
        command.add_argument("agent", help="Source directory, e.g. autosaddler")
        command.add_argument(
            "options",
            nargs=argparse.REMAINDER,
            help="Native evaluation options; use AGENT --help to see them",
        )
    for name in ("smoke", "test", "build"):
        command = commands.add_parser(name, help=f"{name.title()} one source directory or all")
        command.add_argument("agent", nargs="?", default="all")
        command.add_argument("options", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command == "list":
        values = [json.loads((path / "SOURCE.json").read_text()) for path in projects().values()]
        if args.json:
            print(json.dumps(values, indent=2))
        else:
            for row in values:
                print(f"{row['method']:<20} {row['title']}  {row['paper']}")
        return 0
    if args.command == "test" and args.agent == "all":
        code = subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests/cli")],
                              cwd=ROOT).returncode
        if code:
            return code
    try:
        names = (
            list(projects())
            if args.agent == "all" and args.command in {"smoke", "test", "build"}
            else [args.agent]
        )
        for name in names:
            code = launch(name, args.command, args.options)
            if code:
                return code
        return 0
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
