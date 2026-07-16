#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repository_root"

uv venv --python 3.11 .venv-negotiation
uv venv --python 3.11 .venv-presentation

printf '%s\n' "Created isolated runtimes:"
printf '  %s\n' "$repository_root/.venv-negotiation"
printf '  %s\n' "$repository_root/.venv-presentation"
printf '%s\n' "No third-party package was installed and no instrument connection was attempted."
