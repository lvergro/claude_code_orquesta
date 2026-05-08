# CLAUDE.md

## Project
@.claude/project.yml
@.claude/stack.yml

## Authority
1. This file → 2. `.claude/memory/architecture.md` → 3. Code & Tests.

## Memory (sources of truth — never rely on chat history)
- Architecture summary: `.claude/memory/architecture.md` (compact — full C4 in `docs/architecture/`)
- State: `.claude/memory/project-state.md`
- Research: `.claude/memory/research.md`
- Schema: `.claude/memory/schema.md` (auto-synced, on-demand read)
- Decisions (ADRs): `docs/decisions/ADR-*.md`
- Requirements index: `.claude/memory/requirements.md` (FR↔UC map)
- Full design (FRs, UCs, NFRs, C4): `docs/`

## Invariants
Read invariants from `project.yml` (loaded above). STOP if any is violated.

## Output
- Do NOT explain before doing. Just do.
- Do NOT summarize code after writing.
- Output: `✅ Done: [task]` or `❌ Error: [details]`.
- Verbose only if explicitly requested.

## Git
Atomic commits. Conventional Commits: feat:, fix:, chore:, docs:.
Tests MUST pass before commit.
