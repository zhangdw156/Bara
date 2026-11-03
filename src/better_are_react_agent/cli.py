"""Inspect factories and run a credential-free native execution check."""

import argparse
import json
import os

from .catalog import describe, identity, list_agents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    info = sub.add_parser("describe")
    info.add_argument("agent")
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--agent", default="all")
    args = parser.parse_args()
    if args.command == "list":
        value = list_agents()
    elif args.command == "describe":
        value = {**describe(args.agent), "identity": identity(args.agent)}
    else:
        os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
        from .smoke import run
        names = [row["id"] for row in list_agents()] if args.agent == "all" else [args.agent]
        value = [run(name) for name in names]
    print(json.dumps(value, indent=2, ensure_ascii=False))
