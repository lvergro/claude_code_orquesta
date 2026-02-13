# GEMINI.md

## Project
READ `.agent/rules/project.md` for identity, domain, invariants.
READ `.agent/rules/stack.md` for ALL runtime commands.
READ `.agent/rules/conventions.md` for coding and git standards.

## Authority
1. This file → 2. `.agent/memory/architecture.md` → 3. Code & Tests.

## Memory (sources of truth — never rely on chat history)
- Architecture: `.agent/memory/architecture.md`
- State: `.agent/memory/project-state.md`
- Research: `.agent/memory/research.md`
- Schema: `.agent/memory/schema.md` (auto-synced, on-demand read)
- Decisions: `.agent/memory/decisions/DEC-*.md`

## Invariants
READ `.agent/rules/project.md` → invariants section. STOP if any is violated.

## Output
- Do NOT explain before doing. Just do.
- Do NOT summarize code after writing.
- Output: `Done: [task]` or `Error: [details]`.
- Verbose only if explicitly requested.

## Git
Atomic commits. Conventional Commits: feat:, fix:, chore:, docs:.
Tests MUST pass before commit.

## Workflow & Skills
- **Fidelity**: ALWAYS follow the full `/feature` workflow (Phase 0 to 6). Never skip phases.
- **State sync**: Update GitHub issue progress immediately as `project-state.md` changes.
- **Proactive skills**: Use skills WITHOUT being asked:
  - `validate-invariants` → before every commit
  - `write-tests` → for every feature or logic change
  - `analyze-architecture` → after major structural changes
  - `summarize-context` → every 3 completed tasks
  - `archive-state` → after Phase 6 cleanup
