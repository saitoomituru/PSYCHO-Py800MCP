#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repository_root"

uv venv --python 3.11 .venv-negotiation
uv venv --python 3.11 .venv-presentation

. "$repository_root/.venv-negotiation/bin/activate"
uv sync --project runtimes/negotiation --active --frozen
deactivate

printf '%s\n' "Created isolated runtimes:"
printf '  %s\n' "$repository_root/.venv-negotiation"
printf '  %s\n' "$repository_root/.venv-presentation"
printf '%s\n' "Installed the lock-pinned docs-only FastMCP dependency into the negotiation runtime."
printf '%s\n' "No presentation dependency or instrument connection was attempted."
