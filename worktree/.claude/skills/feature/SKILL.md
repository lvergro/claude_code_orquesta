---
name: feature
description: >
  End-to-end feature delivery: GitHub issue → spec → worktree → implementation → PR.
  One feature = one issue = one worktree = one branch. Full traceability via GitHub.
user-invocable: true
---

# /feature

End-to-end pipeline: GitHub Issue → Spec → Worktree → Implementation → PR.

Input: `#42`, `42`, issue URL, or free-text description.

---

## PHASE 0: RESUME CHECK

1. Parse input:
   - Number or `#N` → ISSUE = N
   - URL `https://github.com/.../issues/N` → extract N
   - Free text → will create issue in Phase 1

2. Verify GitHub CLI auth:
   ```
   gh auth status
   ```
   - FAIL → `❌ Error: Run 'gh auth login' first.`

3. If ISSUE exists, fetch it:
   ```
   gh issue view ISSUE --json number,title,body,state
   ```
   - Issue not found → `❌ Error: Issue #ISSUE not found.`
   - Issue closed → warn user, ask confirmation to proceed

4. Derive identifiers:
   - `SLUG` = kebab-case of issue title, max 40 chars
   - `BRANCH` = `feat/ISSUE-SLUG` (e.g. `feat/42-add-notifications`)
   - `REPO_ROOT` = `git rev-parse --show-toplevel`
   - `WT_ROOT` = `REPO_ROOT/../.worktrees/BRANCH`

5. Check if worktree already exists:
   ```
   git worktree list | grep BRANCH
   ```
   - **EXISTS** → Read `WT_ROOT/.claude/memory/project-state.md` → RESUME from pending phase
   - **NOT EXISTS** → continue to Phase 1

---

## PHASE 1: INTAKE

**Case A — Free-text description (no issue number):**
```
gh issue create --title "TITLE" --body "BODY"
```
- Capture the returned ISSUE number
- Derive SLUG, BRANCH, WT_ROOT from the new issue

**Case B — Existing issue:**
- Already have issue content from Phase 0

**Post session start comment:**
```
gh issue comment ISSUE --body "🚀 Session started. Branch: \`feat/ISSUE-SLUG\`"
```

---

## PHASE 2: SPEC

1. Invoke **planner agent** with context:
   - Issue body (title + description)
   - `.claude/memory/architecture.md`
   - `.claude/memory/decisions/DEC-*.md`
   - `.claude/project.yml`

2. Planner produces structured spec:
   - **Scope**: 1-3 sentences describing the change
   - **Tasks**: decomposed into waves (ordered groups)
   - **Files**: to create/modify
   - **Test strategy**: what to test and how
   - **Invariant check**: which invariants are affected

3. Post spec as issue comment:
   ```
   gh issue comment ISSUE --body "## Spec

   ### Scope
   ...

   ### Tasks
   - Wave 1: ...
   - Wave 2: ...

   ### Files
   ...

   ### Test Strategy
   ...
   "
   ```

4. Write tasks to `project-state.md` with metadata:
   ```
   skill: feature
   issue: #ISSUE
   branch: BRANCH
   phase: execution
   ```

---

## PHASE 3: WORKTREE SETUP

1. Fetch latest:
   ```
   git fetch origin
   ```

2. Create worktree directory:
   ```
   mkdir -p REPO_ROOT/../.worktrees
   git worktree add WT_ROOT -b BRANCH origin/main
   ```

3. Copy state to worktree:
   ```
   cp REPO_ROOT/.claude/memory/project-state.md WT_ROOT/.claude/memory/project-state.md
   ```

4. Initialize clean locks in worktree:
   - Write empty `WT_ROOT/.claude/memory/locks.md`

5. Post comment:
   ```
   gh issue comment ISSUE --body "🏗️ Worktree ready at \`WT_ROOT\`. Starting implementation."
   ```

---

## PHASE 4: EXECUTION (inside worktree)

**CRITICAL:** All file operations use absolute paths under `WT_ROOT`.

- Agents read config from: `WT_ROOT/.claude/stack.yml`, `WT_ROOT/.claude/memory/architecture.md`
- Bash commands: `cd WT_ROOT && {command}`

**For each task `[ ]` in `WT_ROOT/.claude/memory/project-state.md`:**

1. **Builder agent** implements + tests
2. **PASS** → mark `[x]`, print `✅ [task_number] task_description`
3. **FAIL** → retry (max 2 retries). 3rd failure → post blocker to issue, STOP:
   ```
   gh issue comment ISSUE --body "🚫 Blocked: [task description]. Error: [details]"
   ```

**After each completed wave:**
```
cd WT_ROOT && git add -A && git commit -m "feat(SLUG): wave N — [summary]"
```

**Every 3 tasks:** compress context via `/summarize-context`

**Post progress every wave:**
```
gh issue comment ISSUE --body "📊 Progress: X/Y tasks complete."
```

---

## PHASE 5: INTEGRATION

1. Verify ALL tasks are `[x]` in `WT_ROOT/.claude/memory/project-state.md`

2. Run final validation (tests + build):
   - Read `WT_ROOT/.claude/stack.yml` for validate command and exec_prefix
   - Execute: `cd WT_ROOT && {exec_prefix} {stack.commands.validate}`
   - If `validate` not defined, run `{stack.commands.test}` then `{stack.commands.build}`
   - Build step catches SSR/runtime errors (missing providers, import errors, type mismatches)
   - **FAIL** → create fix tasks, return to Phase 4

3. Push branch:
   ```
   cd WT_ROOT && git push -u origin BRANCH
   ```
   - Push rejected → `cd WT_ROOT && git pull --rebase origin BRANCH`, retry once

4. Create PR:
   ```
   gh pr create --title "feat: ISSUE_TITLE" --body "Closes #ISSUE

   ## Summary
   [spec scope from Phase 2]

   ## Changes
   [list of files changed]

   ## Test plan
   [test strategy from Phase 2]
   " --head BRANCH --base main
   ```

5. Post PR URL to issue:
   ```
   gh issue comment ISSUE --body "✅ PR created: PR_URL"
   ```

---

## PHASE 6: CLEANUP

1. Archive state:
   ```
   mkdir -p REPO_ROOT/.claude/memory/archive/
   cp WT_ROOT/.claude/memory/project-state.md REPO_ROOT/.claude/memory/archive/feature-ISSUE-$(date +%Y%m%d).md
   ```

2. Post final summary to issue:
   ```
   gh issue comment ISSUE --body "## Summary
   - Branch: \`BRANCH\`
   - PR: PR_URL
   - Tasks: Y/Y complete
   - Status: Ready for review"
   ```

3. **DO NOT remove worktree** — may need fixes post-review

4. Output: `✅ Feature #ISSUE delivered. PR: PR_URL`

---

## Error Handling

| Error | Action |
|-------|--------|
| `gh auth status` fails | `❌ Error: Run 'gh auth login' first.` |
| Issue not found | `❌ Error: Issue #ISSUE not found.` |
| Push rejected | `git pull --rebase origin BRANCH`, retry once |
| Task fails 3x | Post blocker comment to issue, STOP |
| Session interrupted | Next `/feature #ISSUE` resumes automatically from pending phase |
| Worktree conflicts | `cd WT_ROOT && git rebase origin/main`, resolve conflicts |

---

## Resumability

When `/feature #N` is invoked and a worktree for that issue already exists:

1. Read `WT_ROOT/.claude/memory/project-state.md`
2. Parse metadata: `skill`, `issue`, `branch`, `phase`
3. Find first uncompleted task `[ ]`
4. Resume from the appropriate phase:
   - All tasks `[ ]` and no spec → Phase 2
   - Tasks exist but no worktree work started → Phase 4
   - Some tasks `[x]`, some `[ ]` → Phase 4 (continue)
   - All tasks `[x]` → Phase 5

---

## Conventions

- **One feature = one issue = one worktree = one branch**
- Branch naming: `feat/ISSUE-SLUG`
- Worktree location: `REPO_ROOT/../.worktrees/feat/ISSUE-SLUG`
- Commits inside worktree use conventional format: `feat(SLUG): description`
- All GitHub communication via `gh` CLI — no API tokens needed beyond `gh auth`
