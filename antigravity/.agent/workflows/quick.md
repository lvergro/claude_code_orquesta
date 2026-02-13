---
description: Fast path for trivial changes — bypasses planning, just implement and commit
---

# /quick — Fast Path

For trivial changes that do NOT alter architecture or touch critical flows.

## Gate (must validate)

Read `.agent/rules/project.md` → gate-protected areas.
If the change touches ANY protected area → ABORT, suggest `/develop` instead.

## Preflight Checks

1. `git diff --stat` — if changes touch **>5 files** or **>200 lines** → ABORT: "Change is too large for /quick. Use /develop."
2. Validate invariants (validate-invariants skill activates) — if FAIL → ABORT with violation details.

## Flow

1. Implement + test using commands from `.agent/rules/stack.md`
2. If PASS → commit with conventional format
3. Output: `Done: [description]`
