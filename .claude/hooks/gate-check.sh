#!/usr/bin/env bash
# PreToolUse hook for Edit|Write — enforces gate_protected_areas from project.yml.
# Reads JSON from stdin, emits permissionDecision JSON. Exit 0 always.
#
# Single source of truth for patterns: project.yml → gate_protected_areas.
# Naive YAML parse: extracts lines matching `- pattern: "..."` under that key.

set -euo pipefail

INPUT=$(cat)
PROJECT_YML="${CLAUDE_PROJECT_DIR:-.}/.claude/project.yml"

FILE_PATH=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); ti=d.get("tool_input",{}); print(ti.get("file_path") or ti.get("path") or "")' 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" || ! -f "$PROJECT_YML" ]]; then
  exit 0
fi

# Extract protected patterns (works for: `- pattern: "foo/"` or `- pattern: foo/`)
PATTERNS=$(awk '
  /^gate_protected_areas:/ { in_section=1; next }
  in_section && /^[a-zA-Z]/ { in_section=0 }
  in_section && /^[[:space:]]*-[[:space:]]*pattern:/ {
    sub(/^[[:space:]]*-[[:space:]]*pattern:[[:space:]]*/, "")
    gsub(/^"|"$|^'\''|'\''$/, "")
    print
  }
' "$PROJECT_YML")

[[ -z "$PATTERNS" ]] && exit 0

REL_PATH="${FILE_PATH#${CLAUDE_PROJECT_DIR:-.}/}"

while IFS= read -r PATTERN; do
  [[ -z "$PATTERN" ]] && continue
  # Convert simple glob to regex: ** → .*, * → [^/]*, /  literal
  REGEX=$(printf '%s' "$PATTERN" | sed 's|\.|\\.|g; s|\*\*|.*|g; s|\*|[^/]*|g')
  if [[ "$REL_PATH" =~ ^${REGEX} || "$FILE_PATH" =~ ${REGEX} ]]; then
    REASON=$(awk -v pat="$PATTERN" '
      /^gate_protected_areas:/ { in_section=1; next }
      in_section && /^[a-zA-Z]/ { in_section=0 }
      in_section && match($0, /pattern:[[:space:]]*"?'"'"'?([^"'"'"']*)/, m) { last=m[1] }
      in_section && /reason:/ && last==pat {
        sub(/^[[:space:]]*reason:[[:space:]]*/, "")
        print; exit
      }
    ' "$PROJECT_YML")
    [[ -z "$REASON" ]] && REASON="Protected area (gate_protected_areas in project.yml)"

    python3 -c "
import json
print(json.dumps({
  'hookSpecificOutput': {
    'hookEventName': 'PreToolUse',
    'permissionDecision': 'ask',
    'permissionDecisionReason': f'Gate-protected path \"$REL_PATH\" matches \"$PATTERN\". Reason: $REASON'
  }
}))
"
    exit 0
  fi
done <<< "$PATTERNS"

exit 0
