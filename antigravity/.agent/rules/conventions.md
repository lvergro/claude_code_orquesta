# Coding and Git Conventions

## Output Rules
- Do NOT explain before doing. Just do.
- Do NOT summarize code after writing.
- Output: `Done: [task]` or `Error: [details]`.
- Verbose only if explicitly requested.

## Git
- Atomic commits with Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`.
- Tests MUST pass before commit.
- Never `git add -A` — add specific files.
- Never force push to main.

## Code Quality
- Do NOT add features, refactors, or improvements beyond what the task describes.
- Do NOT add comments, docstrings, or type annotations to code you didn't change.
- Do NOT create documentation files unless explicitly requested.
- Only create files that are strictly necessary to complete the task.
- No hardcoded secrets — auth tokens are the source of truth.

## Memory System
This project uses `.agent/memory/` as a persistent state directory:
- `architecture.md` — system design (source of truth, read before any code)
- `project-state.md` — runtime state (updated during development)
- `research.md` — investigation log
- `decisions/DEC-*.md` — architecture decision records
- `locks.md` — multi-session coordination
- `archive/` — completed state snapshots

Always read `architecture.md` and `project-state.md` before starting work.
Always update `project-state.md` after completing a task.
