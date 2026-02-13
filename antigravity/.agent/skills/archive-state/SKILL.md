---
name: archive-state
description: Archives completed project-state.md to the archive directory and resets state to a clean template. Activates after a feature is fully committed.
---

# Archive State — State Lifecycle

## Flow

1. Read `.agent/memory/project-state.md`
2. Verify phase is completed and all tasks `[x]`
3. Copy current content to `.agent/memory/archive/[YYYY-MM-DD]-[feature-slug].md`
4. Reset project-state.md to clean template:

```
# Project State
updated: [timestamp]
skill: IDLE
phase: IDLE

## Active Tasks
(none)

## Current Focus
task: (none)
file: (none)
test: (none)

## Blockers
(none)

## Recent Decisions (last 5)
(none)
```

5. Output: `Done: State archived. Ready for next feature.`
