#!/usr/bin/env bash
# PostToolUse hook for Edit|MultiEdit|Write — auto-formats the modified file.
# Reads JSON from stdin, detects extension, runs the appropriate formatter.
# Skips silently if formatter is not installed. Never blocks. Exit 0 always.

set -uo pipefail

INPUT=$(cat)

FILE_PATH=$(printf '%s' "$INPUT" | python3 -c '
import json, sys
d = json.load(sys.stdin)
ti = d.get("tool_input", {})
print(ti.get("file_path") or ti.get("path") or "")
' 2>/dev/null || echo "")

[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 0

EXT="${FILE_PATH##*.}"

case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs|json|css|scss|html|md|yaml|yml)
    command -v prettier &>/dev/null && prettier --write --log-level silent "$FILE_PATH"
    ;;
  go)
    command -v gofmt &>/dev/null && gofmt -w "$FILE_PATH"
    ;;
  py)
    if command -v ruff &>/dev/null; then
      ruff format --quiet "$FILE_PATH"
    elif command -v black &>/dev/null; then
      black --quiet "$FILE_PATH"
    fi
    ;;
  rs)
    command -v rustfmt &>/dev/null && rustfmt --edition 2021 "$FILE_PATH"
    ;;
  rb)
    command -v rubocop &>/dev/null && rubocop --autocorrect --no-color -q "$FILE_PATH"
    ;;
  sh|bash)
    command -v shfmt &>/dev/null && shfmt -w "$FILE_PATH"
    ;;
esac

exit 0
