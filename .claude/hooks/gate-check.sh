#!/usr/bin/env bash
# PreToolUse hook for Edit|Write — enforces gate_protected_areas from project.yml.
# Reads JSON from stdin, emits permissionDecision JSON. Exit 0 always.
#
# Single source of truth for patterns: project.yml → gate_protected_areas.
# All parsing and matching happens in python3: no gawk/mawk dependency, and
# values reach the script via environment variables — never interpolated
# into code (a quote in a pattern or reason must not break the gate).

set -uo pipefail

PROJECT_YML="${CLAUDE_PROJECT_DIR:-.}/.claude/project.yml"
[[ -f "$PROJECT_YML" ]] || exit 0

INPUT=$(cat)

HOOK_INPUT="$INPUT" PROJECT_YML="$PROJECT_YML" PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}" \
python3 - <<'PY'
import json, os, re, sys

try:
    data = json.loads(os.environ.get("HOOK_INPUT", "{}"))
except ValueError:
    sys.exit(0)

ti = data.get("tool_input", {})
file_path = ti.get("file_path") or ti.get("path") or ""
if not file_path:
    sys.exit(0)

# Naive YAML parse: `- pattern: "..."` / `reason: ...` pairs under the
# gate_protected_areas key. Works for quoted and unquoted values.
areas = []
current = None
in_section = False
try:
    with open(os.environ["PROJECT_YML"], encoding="utf-8") as f:
        for line in f:
            if re.match(r"^gate_protected_areas:", line):
                in_section = True
                continue
            if in_section and re.match(r"^[A-Za-z]", line):
                break
            if not in_section or re.match(r"^\s*#", line):
                continue
            m = re.match(r"""^\s*-\s*pattern:\s*["']?([^"'#]+?)["']?\s*$""", line)
            if m:
                current = {"pattern": m.group(1).strip(), "reason": ""}
                areas.append(current)
                continue
            m = re.match(r"""^\s*reason:\s*["']?(.+?)["']?\s*$""", line)
            if m and current is not None:
                current["reason"] = m.group(1).strip()
except OSError:
    sys.exit(0)

if not areas:
    sys.exit(0)

prefix = os.environ.get("PROJECT_DIR", ".").rstrip("/") + "/"
rel_path = file_path[len(prefix):] if file_path.startswith(prefix) else file_path

def glob_to_regex(pattern):
    # ** crosses directories, * stays within one segment. The placeholder
    # keeps the * substitution from mangling the .* produced by **.
    out = re.escape(pattern)
    out = out.replace(r"\*\*", "\x00").replace(r"\*", "[^/]*").replace("\x00", ".*")
    return out

for area in areas:
    regex = glob_to_regex(area["pattern"])
    if re.match(regex, rel_path) or re.search(regex, file_path):
        reason = area["reason"] or "Protected area (gate_protected_areas in project.yml)"
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason":
                    'Gate-protected path "%s" matches "%s". Reason: %s'
                    % (rel_path, area["pattern"], reason),
            }
        }))
        break
PY

exit 0
