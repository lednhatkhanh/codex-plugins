#!/bin/sh
set -eu

usage() {
  cat <<'USAGE'
Usage: install-agents.sh [project|user] [target-path] [--force]

project  Install bundled agents into target-path's Git repository at .codex/agents.
         If target-path is omitted, use the current working directory.
user     Install bundled agents into ~/.codex/agents for personal use. Ignores target-path.

By default, existing files are not overwritten. Pass --force to replace matching files.
USAGE
}

target="${1:-project}"
force="false"
target_path=""

if [ "$target" = "--help" ] || [ "$target" = "-h" ]; then
  usage
  exit 0
fi

shift 2>/dev/null || true
for arg in "$@"; do
  case "$arg" in
    --force)
      force="true"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [ -n "$target_path" ]; then
        usage >&2
        exit 2
      fi
      target_path="$arg"
      ;;
  esac
done

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
src="$plugin_root/assets/agents"

case "$target" in
  project)
    search_dir="${target_path:-$(pwd)}"
    if git_root=$(git -C "$search_dir" rev-parse --show-toplevel 2>/dev/null); then
      dest="$git_root/.codex/agents"
    else
      dest="$search_dir/.codex/agents"
    fi
    ;;
  user)
    dest="$HOME/.codex/agents"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

mkdir -p "$dest"

for file in "$src"/*.toml; do
  name=$(basename "$file")
  if [ -e "$dest/$name" ] && [ "$force" != "true" ]; then
    echo "Refusing to overwrite $dest/$name; rerun with --force" >&2
    exit 1
  fi
done

for file in "$src"/*.toml; do
  cp "$file" "$dest/"
  echo "Installed $dest/$(basename "$file")"
done

echo "Installed Codex agent templates to $dest"
