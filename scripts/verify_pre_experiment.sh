#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repository_root"

.venv-negotiation/bin/python main.py status
.venv-presentation/bin/python presentation/main.py
.venv-negotiation/bin/python -m unittest discover -s tests -p 'test_*.py'

if .venv-negotiation/bin/python main.py serve-mcp; then
    printf '%s\n' "ERROR: MCP service unexpectedly passed the experiment gate" >&2
    exit 1
else
    exit_code=$?
fi

if [ "$exit_code" -ne 3 ]; then
    printf '%s\n' "ERROR: expected closed-gate exit code 3, got $exit_code" >&2
    exit 1
fi

printf '%s\n' "Pre-experiment verification passed; instrument I/O remains blocked."
