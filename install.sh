#!/usr/bin/env bash

HEREDIR="$(dirname "$(readlink -f "$0")")"

mkdir -p "$HOME/.local/bin"
ln -s "$HOME/.local/bin/pysh" "$HEREDIR/pysh"

echo "Installed to $HOME/.local/bin/pysh . Ensure $HOME/.local/bin is on your \$PATH . If not, add it in your .bashrc"

