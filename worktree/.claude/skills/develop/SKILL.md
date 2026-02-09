---
name: develop
description: >
  Master End-to-End pipeline for features. Plans, designs if needed,
  executes in loop, and commits. Use for any feature, complex bug fix,
  or change requiring planning. Absorbs implement, resume, and propose-architecture.
user-invocable: true
---

# /develop — Master Pipeline

## PHASE 0: Triage
1. Read `.claude/memory/project-state.md`
   - Has pending [ ] tasks? → RESUME from first pending task
   - Clean state? → Continue to Phase 1
2. Use **planner agent** to analyze request
   - Needs architecture changes? → Include Phase 1
   - No arch changes? → Skip to Phase 2
   - Arch-only request? → Phase 1 only, then finalize

## PHASE 1: Architecture (conditional)
- Read `.claude/memory/decisions/DEC-*.md` to avoid re-litigating past decisions
- Use **planner agent** (design mode) → update architecture.md
- Record new architectural decisions as `DEC-####.md` in `memory/decisions/`
- Output: "✅ Architecture updated."

## PHASE 2: Execution Loop
For each pending task [ ] in project-state.md:
1. Use **builder agent**: implement + test
2. PASS → mark [x] in project-state.md, print "✅ [N]"
3. FAIL → builder retries (max 2). 3rd fail → STOP, ask user.

### Context Management (every 3 completed tasks)
- Use **/summarize-context** to compress state to project-state.md
- Print: "Context compressed. Continuing task N."

## PHASE 3: Finalization
- Verify ALL tasks [x] in project-state.md
- Use **git agent**: commit + push
- Use **/archive-state**: move state to archive/
