#!/usr/bin/env bash

set -euo pipefail

HEREDIR="$(dirname "$(readlink -f "$0")")"

mkdir -p "$HOME/.local/bin"
ln -s "$HEREDIR/pysh" "$HOME/.local/bin/pysh"

echo "Installed to $HOME/.local/bin/pysh . Ensure $HOME/.local/bin is on your \$PATH . If not, add it in your .bashrc"

