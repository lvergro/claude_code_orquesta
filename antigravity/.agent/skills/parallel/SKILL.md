---
name: parallel
description: Coordinates multiple simultaneous sessions working on the same wave. Uses locks.md to prevent duplicate work on the same task.
---

# Parallel — Multi-Session Execution

## Flow

1. Read `.agent/memory/project-state.md`
2. Identify current wave (first wave with pending `[ ]` tasks)
3. Read `.agent/memory/locks.md`
4. **Stale lock check:** Any lock older than 30 minutes is expired — remove it
5. For each unlocked task in the wave:
   - Write lock: `- [task_id]: LOCKED at [timestamp]` in locks.md
   - Implement + test using commands from `.agent/rules/stack.md`
   - If PASS → mark `[x]` in project-state.md, remove lock
   - If FAIL → remove lock, report error

## Usage

Open 2-3 Antigravity terminals:
```
# terminal 1: /parallel
# terminal 2: /parallel
```

Each session picks different tasks from the same wave automatically.

## locks.md Format

```
# Active Locks
- 1a: LOCKED at 2026-02-07T14:30Z
- 1b: LOCKED at 2026-02-07T14:31Z
```
