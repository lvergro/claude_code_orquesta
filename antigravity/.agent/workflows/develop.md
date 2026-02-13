---
description: Master E2E pipeline for features — plans, executes in loop, and commits
---

# /develop — Master Pipeline

## Phase 0: Triage

1. **Schema verification** — Run `/sync-schema` auto-verification:
   - Read `.agent/rules/stack.md` → Schema section. Not configured → skip silently.
   - If configured, check if `schema.md` is stale (files in schema paths newer than `Last synced` date).
   - Stale or missing → run full `/sync-schema` before continuing.
2. Read `.agent/memory/project-state.md`
   - Has pending `[ ]` tasks with `skill: /develop`? → RESUME from first pending task (skip to Phase 2)
   - Clean state or `phase: IDLE`? → Continue to Phase 1
3. Analyze request:
   - Needs architecture changes? → Include Phase 1
   - No arch changes? → Skip to Phase 2
   - Arch-only request? → Phase 1 only, then finalize

## Phase 1: Architecture + Planning

1. Read `.agent/memory/decisions/DEC-*.md` to avoid re-litigating past decisions
2. If architecture changes needed:
   - Update `.agent/memory/architecture.md`
   - Record new decisions as `DEC-####.md` in `memory/decisions/`
3. **MANDATORY — Write plan to project-state.md:**

```
# Project State
updated: [YYYY-MM-DD]
skill: /develop
phase: execution

## Active Tasks

### Wave 1: [Name]
- [ ] Task description
- [ ] Task description

### Wave 2: [Name]
- [ ] Task description

## Current Focus
task: (starting)
file: (none)
test: (none)

## Blockers
(none)

## Recent Decisions (last 5)
(none)
```

4. Output the plan summary. Wait for user approval before Phase 2.

### Planning Rules
- Each wave groups related tasks (DB, Backend, UI, etc.)
- Tasks must be specific and actionable
- Keep total tasks under 15. Decompose further if needed.
- project-state.md MUST NOT exceed 80 lines

## Phase 2: Execution Loop

**BEFORE each task:** Update `Current Focus` in project-state.md.

**For each pending task `[ ]`:**
1. Implement + test using commands from `.agent/rules/stack.md`
2. PASS → edit project-state.md: `- [ ]` to `- [x]`, update focus. Print: `Done: [N/total] Task`
3. FAIL → retry max 2. 3rd fail → STOP, ask user.

**After each completed wave:** Update `phase` field.

**Every 3 completed tasks:** Compress context (summarize-context skill activates). Print: `Context compressed. Continuing task N.`

## Phase 3: Finalization

1. Verify ALL tasks `[x]` in project-state.md
2. Run final validation:
   - If validate command defined in stack.md → run it
   - Otherwise → run test, then build
   - FAIL → create fix tasks, return to Phase 2
3. Update project-state.md: set `phase: completed`
4. Commit with conventional format
5. Archive state to `.agent/memory/archive/`

## Critical Rules

- **NEVER skip writing to project-state.md.** Every task state change MUST be persisted.
- **project-state.md is the source of truth.** If the session crashes, the next `/develop` reads it and resumes.
- **Mark tasks [x] one at a time**, not in batch.
- **80-line cap**: If project-state.md exceeds 80 lines, archive completed waves.
- **NEVER create documentation files** unless explicitly requested. Only write to `.agent/memory/`.
- **Do ONLY what the task says.** No extra features, no refactors, no "while I'm here" improvements.
