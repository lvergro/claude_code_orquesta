---
name: prepare-commit
description: >
  Validates commit readiness and generates a conventional commit message.
  Checks that tests pass and all planned tasks are complete before proceeding.
user-invocable: true
---

# /prepare-commit — Commit Readiness

Read `.claude/models.yml` for model routing. This skill uses model: haiku.

## Preconditions (ALL must pass)
1. Run tests: `{stack.runtime.exec_prefix} {stack.commands.test}` → PASS
2. Check project-state.md → all tasks [x]
3. Run /validate-invariants → PASS

## Generate Message
1. Analyze `git diff --staged` (or unstaged changes)
2. Determine type: feat | fix | chore | docs
3. Write concise message: `type: description`

## Output
- If ready: "✅ Commit ready: `type: message`"
- If not ready: "❌ Not ready: [reason]"
