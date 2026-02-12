# CLAUDE.md

## Project
READ `.claude/project.yml` for identity, domain, invariants.
READ `.claude/stack.yml` for ALL runtime commands and exec_prefix.
READ `.claude/models.yml` for model routing.

## Authority
1. This file → 2. `.claude/memory/architecture.md` → 3. Code & Tests.

## Memory (sources of truth — never rely on chat history)
- Architecture: `.claude/memory/architecture.md`
- State: `.claude/memory/project-state.md`
- Research: `.claude/memory/research.md`
- Decisions: `.claude/memory/decisions/DEC-*.md`

## Invariants
READ `.claude/project.yml` → `invariants` section. STOP if any is violated.

## Output
- Do NOT explain before doing. Just do.
- Do NOT summarize code after writing.
- Output: `✅ Done: [task]` or `❌ Error: [details]`.
- Verbose only if explicitly requested.

## Git
Atomic commits. Conventional Commits: feat:, fix:, chore:, docs:.
Tests MUST pass before commit.
