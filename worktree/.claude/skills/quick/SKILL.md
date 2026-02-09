---
name: quick
description: >
  Fast-path for trivial changes that do NOT alter architecture or touch
  critical flows. Bypasses planning. Just implement and commit.
user-invocable: true
---

# /quick — Fast Path

## Gate (MUST validate)
Read `.claude/project.yml` → `gate_protected_areas`.
If the change touches ANY protected area → ABORT, suggest /develop instead.

## Preflight Checks (before building)
1. Run `git diff --stat` — if changes touch **>5 files** or **>200 lines**, ABORT: "Change is too large for /quick. Use /develop."
2. Run **/validate-invariants** — if FAIL → ABORT with violation details.

## Flow
1. Use **builder agent**: implement + test
2. If PASS → Use **git agent**: commit
