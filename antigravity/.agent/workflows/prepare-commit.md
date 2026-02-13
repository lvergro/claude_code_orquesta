---
description: Validates commit readiness and generates a conventional commit message
---

# /prepare-commit — Commit Readiness

## Preconditions (all must pass)

1. Run tests (from `.agent/rules/stack.md`) → PASS
2. Check `.agent/memory/project-state.md` → all tasks `[x]`
3. Validate invariants (validate-invariants skill activates) → PASS

## Generate Message

1. Analyze `git diff --staged` (or unstaged changes)
2. Determine type: `feat` | `fix` | `chore` | `docs`
3. Write concise message: `type: description`

## Output

- If ready: `Done: Commit ready — \`type: message\``
- If not ready: `Error: Not ready — [reason]`
