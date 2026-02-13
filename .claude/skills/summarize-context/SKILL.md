---
name: summarize-context
description: >
  Compresses current session state into project-state.md to free context
  window tokens. Captures key decisions and progress without losing the thread.
user-invocable: true
---

# /summarize-context — Context Compression

Read `.claude/models.yml` for model routing. This skill uses model: haiku.

## target file
`.claude/memory/project-state.md`

## steps
1. Analyze recent conversation: What was achieved? What decisions were made? What's pending?
2. Update project-state.md with current state:
   - Mark completed tasks [x]
   - Update current focus
   - Record blockers
   - Add recent decisions (keep last 5)
3. Output: "Memory updated in project-state.md. Ready to continue with clean context."

## cap
project-state.md MUST NOT exceed 80 lines. If over cap:
- Archive completed waves to `.claude/memory/archive/`
- Keep only active wave + current focus + blockers
