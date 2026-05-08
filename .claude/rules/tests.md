---
paths:
  - "tests/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/__tests__/**"
---

# Testing Rules

## Source of truth
Test commands live in `.claude/stack.yml` → `commands.test` and `commands.test_single`.
File naming follows `conventions.test_file_pattern`.

## What to test
- Cover the path the spec calls out, not every branch by reflex.
- New invariants from `project.yml` get an explicit test that fails if violated.
- Bug fix → regression test that fails on the unfixed code.

## What NOT to test
- Framework behavior (don't test that React renders).
- Trivial getters/setters or pass-through code.
- Implementation details that change with refactors — test behavior, not internals.

## Mocks
- Mock at boundaries (network, FS, time). Don't mock internal modules.
- Integration tests should hit a real DB in a transaction that rolls back.

## Before commit
Tests MUST pass (CLAUDE.md). The `git` agent aborts the commit if they don't.
