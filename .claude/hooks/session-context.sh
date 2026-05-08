#!/usr/bin/env bash
# SessionStart hook — injects active state from project-state.md as additionalContext.
# Keeps Claude aware of in-progress work without forcing a Read.

set -euo pipefail

STATE="${CLAUDE_PROJECT_DIR:-.}/.claude/memory/project-state.md"
[[ ! -f "$STATE" ]] && exit 0

# Extract Current Focus + Active Tasks blocks
SUMMARY=$(awk '
  /^## (Current Focus|Active Tasks|Blockers)/ { p=1; print; next }
  /^## / && p { p=0 }
  p { print }
' "$STATE")

# Skip injection if everything is idle/empty
if echo "$SUMMARY" | grep -qE '^(task|file|test):[[:space:]]*\(none\)' && \
   echo "$SUMMARY" | grep -q '^## Active Tasks' && \
   ! echo "$SUMMARY" | grep -qE '^- '; then
  exit 0
fi

python3 -c "
import json, sys
ctx = '''Active project state (.claude/memory/project-state.md):

$SUMMARY'''
print(json.dumps({
  'hookSpecificOutput': {
    'hookEventName': 'SessionStart',
    'additionalContext': ctx
  }
}))
"
