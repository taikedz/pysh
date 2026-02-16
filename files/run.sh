#!/usr/bin/env bash

HEREDIR="$(dirname "\$(readlink -f "$0")")"
. "$HEREDIR/.venv/bin/activate"

python3 "$HEREDIR/$(basename %TARGET%)" "$@"