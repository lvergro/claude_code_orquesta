---
name: develop
description: >
  Master End-to-End pipeline for features. Plans, designs if needed,
  executes in loop, and commits. Use for any feature, complex bug fix,
  or change requiring planning. Absorbs implement, resume, and propose-architecture.
user-invocable: true
---

# /develop — Master Pipeline

Read `.claude/models.yml` for model routing.

## PHASE 0: Triage
1. Read `.claude/memory/project-state.md`
   - Has pending `[ ]` tasks with `skill: /develop`? → RESUME from first pending task (skip to Phase 2)
   - Clean state or `phase: IDLE`? → Continue to Phase 1
2. Use **planner agent** (model: opus) to analyze request
   - Needs architecture changes? → Include Phase 1
   - No arch changes? → Skip to Phase 2
   - Arch-only request? → Phase 1 only, then finalize

## PHASE 1: Architecture + Planning
1. Read `.claude/memory/decisions/DEC-*.md` to avoid re-litigating past decisions
2. If architecture changes needed:
   - Use **planner agent** (model: opus, design mode) → update architecture.md
   - Record new decisions as `DEC-####.md` in `memory/decisions/`
3. **MANDATORY — Write plan to project-state.md** using this exact format:

```markdown
# Project State
updated: [YYYY-MM-DD]
skill: /develop
phase: execution

## Active Tasks

### Wave 1: [Wave Name]
- [ ] Task description
- [ ] Task description

### Wave 2: [Wave Name]
- [ ] Task description
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

4. Output the plan summary. Wait for user approval before proceeding to Phase 2.

## PHASE 2: Execution Loop

**BEFORE each task:**
- Update `Current Focus` in project-state.md with the task being worked on

**For each pending task `[ ]` in project-state.md:**
1. Use **builder agent** (model: sonnet): implement + test
2. **PASS** → IMMEDIATELY edit project-state.md:
   - Change `- [ ] Task` to `- [x] Task`
   - Update `Current Focus` to next task
   - Print: `✅ [N/total] Task description`
3. **FAIL** → builder retries (max 2). 3rd fail → STOP, ask user.

**After each completed wave:**
- Update `phase` field if moving to next wave

**Every 3 completed tasks:**
- Use **/summarize-context** to compress state
- Print: `Context compressed. Continuing task N.`

## PHASE 3: Finalization
1. Verify ALL tasks `[x]` in project-state.md
2. Run final validation: `{stack.runtime.exec_prefix} {stack.commands.validate}`
   - If `validate` is defined in stack.yml, run it (typically: tests + build)
   - If not defined, run `{stack.commands.test}` then `{stack.commands.build}`
   - Build step catches SSR/runtime errors (missing providers, import errors, type mismatches)
   - **FAIL** → create fix tasks, return to Phase 2
3. Update project-state.md: set `phase: completed`
4. Use **git agent** (model: haiku): commit + push
5. Use **/archive-state**: move state to archive/

## Critical Rules
- **NEVER skip writing to project-state.md.** Every task state change MUST be persisted.
- **project-state.md is the source of truth.** If the session crashes, the next `/develop` reads it and resumes.
- **Mark tasks [x] one at a time**, not in batch. Each mark = one Edit to the file.
- **80-line cap**: If project-state.md exceeds 80 lines, archive completed waves immediately.
- **NEVER create documentation files** (docs/*.md, README, CHANGELOG) unless explicitly requested by the user. Only write to `.claude/memory/` files.
- **Do ONLY what the task says.** No extra features, no refactors, no "while I'm here" improvements.
