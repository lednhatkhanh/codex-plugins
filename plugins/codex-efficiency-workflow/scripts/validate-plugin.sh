#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
repo_root=$(git -C "$plugin_root" rev-parse --show-toplevel 2>/dev/null || true)

if [ -n "$repo_root" ] && [ -x "$repo_root/scripts/validate-marketplace.py" ]; then
  python3 "$repo_root/scripts/validate-marketplace.py" --plugin "$plugin_root"
else
  echo "Cannot find repo validator at scripts/validate-marketplace.py" >&2
  exit 1
fi
