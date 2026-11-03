"""Public method identities and honest reconstruction boundaries."""

import hashlib
import json
from functools import lru_cache
from importlib.metadata import version
from importlib.resources import files


@lru_cache(maxsize=1)
def _catalog():
    return json.loads(files(__package__).joinpath("agents.json").read_text())


def list_agents():
    """Return independent descriptions, without importing ARE or a model client."""
    return [describe(name) for name in _catalog()]


def describe(name):
    try:
        return json.loads(json.dumps(_catalog()[name]))
    except KeyError:
        raise ValueError(f"Unknown agent {name!r}; choose from {', '.join(_catalog())}") from None


def policy(name):
    spec = describe(name)
    return files(__package__).joinpath("policies", spec["policy"]).read_text() if spec["policy"] else ""


@lru_cache(maxsize=None)
def _identity(name):
    """Content identity for checkpoints and evaluation provenance, excluding local paths."""
    spec = describe(name)
    root = files(__package__)
    sources = {}

    def collect(folder, prefix=""):
        for item in sorted(folder.iterdir(), key=lambda p: p.name):
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            path = prefix + item.name
            if item.is_dir():
                collect(item, path + "/")
            elif item.name.endswith((".py", ".md", ".json", ".txt")):
                sources[path] = hashlib.sha256(item.read_bytes()).hexdigest()

    collect(root)
    digest = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    return {"agent": name, "package_version": version("better-are-react-agent"),
            "source_sha256": digest, "fidelity": spec["fidelity"],
            "factory": spec["factory"], "are_distribution": version("meta-agents-research-environments")}


def identity(name):
    return json.loads(json.dumps(_identity(name)))
