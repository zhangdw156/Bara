"""Record actual source contents, without a plugin registry or fixed revision gate."""

import hashlib
import inspect
import json
import os
from pathlib import Path


def source_identity():
    from are.simulation.agents.default_agent.agent_factory import are_simulation_react_json_agent
    from are.simulation.agents.default_agent.base_agent import BaseAgent

    source = Path(os.environ["BARA_AGENT_ROOT"]).resolve()
    for obj in (BaseAgent, are_simulation_react_json_agent):
        if not Path(inspect.getfile(obj)).resolve().is_relative_to(source):
            raise RuntimeError("ARE was imported from a different source directory")
    manifest = json.loads((source / "SOURCE.json").read_text())
    hashes = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((source / "are").rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".txt"}
    }
    for name in ("pyproject.toml", "uv.lock"):
        hashes[name] = hashlib.sha256((source / name).read_bytes()).hexdigest()
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return {
        "method": manifest["method"],
        "paper": manifest["paper"],
        "source_sha256": digest,
        "upstream": manifest["upstream"],
        "factory": "are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent",
    }


def write_source_identity(output_dir):
    path = Path(output_dir) / "agent_source.json"
    selected = source_identity()
    if path.exists():
        if json.loads(path.read_text()) != selected:
            raise ValueError("Output directory belongs to another agent or source revision")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(selected, indent=2) + "\n")
