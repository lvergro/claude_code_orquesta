---
name: parallel
description: >
  Execute parallelizable tasks from the current wave.
  For use with multiple simultaneous Claude Code sessions.
  Coordinates via locks.md to prevent duplicate work.
user-invocable: true
---

# /parallel — Multi-Session Execution

Read `.claude/models.yml` for model routing.

## flow
1. Read `project-state.md`
2. Identify current wave (first wave with pending [ ] tasks)
3. Read `.claude/memory/locks.md`
4. **Stale lock check:** Any lock older than 30 minutes is expired — remove it and treat the task as unlocked.
5. For each unlocked task in the wave:
   - Write lock: `- [task_id]: LOCKED at [timestamp]` in locks.md
   - Use **builder agent** (model: sonnet): implement + test
   - If PASS → mark [x] in project-state.md, remove lock
   - If FAIL → remove lock, report error

## usage
Open 2-3 Claude Code terminals:
```bash
# terminal 1
/parallel

# terminal 2
/parallel
```

Each session picks different tasks from the same wave automatically.

## locks.md Format
```markdown
# Active Locks
- 1a: LOCKED at 2026-02-07T14:30Z
- 1b: LOCKED at 2026-02-07T14:31Z
```
