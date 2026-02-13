---
name: archive-state
description: >
  Archives completed project-state.md to the archive directory and resets
  the state file to a clean template. Use after a feature is fully committed.
user-invocable: true
---

# /archive-state — State Lifecycle

Read `.claude/models.yml` for model routing. This skill uses model: haiku.

## flow
1. Read `.claude/memory/project-state.md`
2. Verify phase is FINALIZATION and all tasks [x]
3. Copy current content to `.claude/memory/archive/[YYYY-MM-DD]-[feature-slug].md`
4. Reset project-state.md to clean template:

```markdown
# project state
updated: [timestamp]
skill: IDLE
phase: IDLE

## active tasks
(none)

## current focus
task: (none)
file: (none)
test: (none)

## blockers
(none)

## recent decisions (last 5)
(none)
```

5. Output: "✅ State archived. Ready for next feature."
