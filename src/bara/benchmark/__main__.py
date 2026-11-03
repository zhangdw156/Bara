import os
import sys

from .cli import main

mode = sys.argv[1]
if mode not in {"run", "judge", "gaia2-run"}:
    raise SystemExit("Unknown evaluation mode")
main(
    args=sys.argv[2:],
    prog_name=os.environ.get("BARA_COMMAND", "bara benchmark AGENT"),
    obj={"mode": mode},
)
