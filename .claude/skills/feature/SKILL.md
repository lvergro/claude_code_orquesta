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

Read `.claude/models.yml` for model routing.

---

## phase 0: resume check

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
   gh issue view ISSUE --json number,title,body,state,labels
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

## phase 1: intake

**Case A — Free-text description (no issue number):**
```
gh issue create --title "TITLE" --body "BODY"
```
- Capture the returned ISSUE number
- Derive SLUG, BRANCH, WT_ROOT from the new issue
- Apply preliminary label based on content analysis (model: haiku):
  - Defect/bug description → `gh issue edit ISSUE --add-label "bug"`
  - Documentation-focused → `gh issue edit ISSUE --add-label "documentation"`
  - Default → `gh issue edit ISSUE --add-label "enhancement"`

**Case B — Existing issue:**
- Already have issue content from Phase 0
- If no labels exist, apply preliminary label as in Case A

**Allowed labels** (GitHub defaults only): `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `question`, `duplicate`, `invalid`, `wontfix`.

---

## phase 2: spec

1. Invoke **planner agent** (model: opus) with context:
   - Issue body (title + description)
   - `.claude/memory/architecture.md`
   - `.claude/memory/decisions/DEC-*.md`
   - `.claude/project.yml`

2. Planner produces structured spec:
   - **Scope**: 1-3 sentences describing the change
   - **Acceptance Criteria**: measurable conditions for done
   - **Invariants Affected**: which invariants from project.yml are touched
   - **Tasks**: decomposed into waves (ordered groups)
   - **Files**: to create/modify
   - **Test strategy**: what to test and how
   - **Recommended labels**: additional labels based on analysis

3. Apply labels from planner analysis (model: haiku):
   ```
   gh issue edit ISSUE --add-label "label1,label2"
   ```

4. Post **Comment 1 — Requirements** (posted ONCE, NEVER edited):
   ```
   gh issue comment ISSUE --body "## Requirements
   **Branch:** \`feat/ISSUE-SLUG\`

   ### Scope
   [scope from planner]

   ### Acceptance Criteria
   [acceptance criteria from planner]

   ### Invariants Affected
   [invariants from planner]

   ### Files
   [files from planner]

   ### Test Strategy
   [test strategy from planner]
   "
   ```

5. Post **Comment 2 — Execution Plan** (living comment, edited throughout):
   ```
   gh issue comment ISSUE --body "## Execution

   ### Wave 1: [Name]
   - [ ] Task description
   - [ ] Task description

   ### Wave 2: [Name]
   - [ ] Task description

   ---
   **Status:** Starting execution
   "
   ```

6. Write tasks to `project-state.md` with metadata:
   ```
   skill: feature
   issue: #ISSUE
   branch: BRANCH
   phase: execution
   ```

---

## phase 3: worktree setup

1. Sync local main with remote:
   ```
   git fetch origin
   git switch main && git merge --ff-only origin/main
   ```
   - If merge fails (local has diverged) → `❌ Error: Local main has diverged from origin. Resolve manually.`

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

---

## phase 4: execution (inside worktree)

### isolation rule — mandatory
From this phase until Phase 5 completes:
- **ALL reads and writes MUST use absolute paths under `WT_ROOT`**
- **NEVER read from REPO_ROOT** — the main checkout is off-limits
- **NEVER write to REPO_ROOT** — no copying files back to main
- **NEVER `cd` to REPO_ROOT** — stay inside the worktree
- The worktree IS the project root. Treat `WT_ROOT` as if REPO_ROOT does not exist.

If an agent or skill tries to reference a path outside WT_ROOT → STOP and fix the path.

### execution
- Agents read config from: `WT_ROOT/.claude/stack.yml`, `WT_ROOT/.claude/memory/architecture.md`
- Bash commands: `cd WT_ROOT && {command}`
- State updates: `WT_ROOT/.claude/memory/project-state.md`

**For each task `[ ]` in `WT_ROOT/.claude/memory/project-state.md`:**

1. **Builder agent** (model: sonnet) implements + tests
2. **PASS** → mark `[x]`, print `✅ [task_number] task_description`
3. **FAIL** → retry (max 2 retries). 3rd failure → post blocker to issue, STOP:
   ```
   gh issue comment ISSUE --body "Blocked: [task description]. Error: [details]"
   ```

**After EVERY completed wave, run these 3 steps in order — NO EXCEPTIONS:**

1. **Commit:**
   ```
   cd WT_ROOT && git add -A && git commit -m "feat(SLUG): wave N — [summary]"
   ```

2. **Update Comment 2 (Execution Plan) via `--edit-last`:**
   ```
   gh issue comment ISSUE --edit-last --body "## Execution

   ### Wave 1: [Name]
   - [x] Task description
   - [x] Task description

   ### Wave 2: [Name]
   - [ ] Task description

   ---
   **Status:** Wave N complete — X/Y tasks done
   "
   ```
   If `--edit-last` fails (first wave, no previous comment by this actor), post a new comment:
   ```
   gh issue comment ISSUE --body "## Execution
   ...
   "
   ```

3. **Every 3 tasks:** compress context via `/summarize-context` (model: haiku)

---

## phase 5: integration

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

4. Create PR (model: haiku):
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

5. Final update to Comment 2 (Execution Plan) via `--edit-last`:
   ```
   gh issue comment ISSUE --edit-last --body "## Execution

   ### Wave 1: [Name]
   - [x] Task description
   ...

   ---
   **PR:** PR_URL
   **Status:** Complete — Y/Y tasks done
   "
   ```

---

## phase 6: cleanup

1. Archive state (model: haiku):
   ```
   mkdir -p REPO_ROOT/.claude/memory/archive/
   cp WT_ROOT/.claude/memory/project-state.md REPO_ROOT/.claude/memory/archive/feature-ISSUE-$(date +%Y%m%d).md
   ```

2. **DO NOT remove worktree** — may need fixes post-review

3. Output: `✅ Feature #ISSUE delivered. PR: PR_URL`

*(No Comment 3 — Comment 2 already contains the PR URL and final status.)*

---

## error handling

| Error | Action |
|-------|--------|
| `gh auth status` fails | `❌ Error: Run 'gh auth login' first.` |
| Issue not found | `❌ Error: Issue #ISSUE not found.` |
| Push rejected | `git pull --rebase origin BRANCH`, retry once |
| Task fails 3x | Post blocker comment to issue, STOP |
| Session interrupted | Next `/feature #ISSUE` resumes automatically from pending phase |
| Worktree conflicts | `cd WT_ROOT && git rebase origin/main`, resolve conflicts |

---

## resumability

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

## conventions

- **One feature = one issue = one worktree = one branch**
- Branch naming: `feat/ISSUE-SLUG`
- Worktree location: `REPO_ROOT/../.worktrees/feat/ISSUE-SLUG`
- Commits inside worktree use conventional format: `feat(SLUG): description`
- All GitHub communication via `gh` CLI — no API tokens needed beyond `gh auth`
- **2 comments only**: Comment 1 (Requirements — immutable), Comment 2 (Execution — living)
- **Labels**: GitHub defaults only (`bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `question`, `duplicate`, `invalid`, `wontfix`)
