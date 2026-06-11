---
name: cleanup-worktrees
description: >
  Lists worktrees under ../.worktrees, detects which branches were merged or
  had their PR closed, and removes them after a single confirmation. Closes
  the lifecycle that /feature intentionally leaves open.
user-invocable: true
---

# /cleanup-worktrees

1. Resolve roots:
   - `REPO_ROOT` = `git rev-parse --show-toplevel`
   - `WT_BASE` = `REPO_ROOT/../.worktrees`
   - No worktrees under WT_BASE → `✅ No worktrees to clean.` and stop.

2. For each worktree in `git worktree list --porcelain` whose path is under WT_BASE:
   - `BRANCH` from its `branch refs/heads/...` line
   - **Dirty check:** `git -C PATH status --porcelain` non-empty → mark `⚠️ dirty`, never a candidate.
   - **PR state:** `gh pr view BRANCH --json state` (no PR → treat as active)
     - `MERGED` → candidate: remove worktree + delete branch
     - `CLOSED` (not merged) → candidate: remove worktree, keep branch
     - `OPEN` or no PR → keep, list as active

3. Present the table:
   ```
   Worktree                                  Branch                      PR       Action
   ../.worktrees/feat/42-add-notifications   feat/42-add-notifications   MERGED   remove + delete branch
   ../.worktrees/feat/57-export-csv          feat/57-export-csv          OPEN     keep
   ../.worktrees/feat/61-dark-mode           feat/61-dark-mode           dirty ⚠️ keep (uncommitted changes)
   ```
   No candidates → `✅ Nothing to clean.` and stop.

4. Ask ONCE — the only gate in this skill: `Remove N worktrees? (yes/no)`

5. On yes, for each candidate:
   - `git worktree remove PATH` — never `--force`; if git refuses (untracked files), report and skip.
   - Merged branches only: `git branch -d BRANCH` — lowercase `-d`; if not fully merged, report and skip.
   - Finish with `git worktree prune`.

6. Output: `✅ Removed X worktrees, deleted Y branches. Z kept (active/dirty).`

## Rules

- NEVER `git worktree remove --force` or `git branch -D`. If git refuses, the user decides manually.
- NEVER touch the main checkout or worktrees outside WT_BASE.
