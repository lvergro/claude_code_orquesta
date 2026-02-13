---
description: End-to-end feature delivery from GitHub issue to PR with worktree isolation
---

# /feature — Issue to PR Pipeline

Input: `#42`, `42`, issue URL, or free-text description.

## Phase 0: Resume Check

1. **Schema verification** — Run `/sync-schema` auto-verification:
   - Read `.agent/rules/stack.md` → Schema section. Not configured → skip silently.
   - If configured, check if `schema.md` is stale (files in schema paths newer than `Last synced` date).
   - Stale or missing → run full `/sync-schema` before continuing.

2. Parse input:
   - Number or `#N` → ISSUE = N
   - URL `https://github.com/.../issues/N` → extract N
   - Free text → will create issue in Phase 1

3. Verify GitHub CLI: `gh auth status`
   - FAIL → `Error: Run 'gh auth login' first.`

4. If ISSUE exists, fetch it:
   ```
   gh issue view ISSUE --json number,title,body,state,labels
   ```

5. Derive identifiers:
   - `SLUG` = kebab-case of issue title, max 40 chars
   - `BRANCH` = `feat/ISSUE-SLUG`
   - `REPO_ROOT` = `git rev-parse --show-toplevel`
   - `WT_ROOT` = `REPO_ROOT/../.worktrees/BRANCH`

6. Check if worktree exists: `git worktree list | grep BRANCH`
   - EXISTS → Read `WT_ROOT/.agent/memory/project-state.md` → RESUME from pending phase
   - NOT EXISTS → continue to Phase 1

## Phase 1: Intake

**Free-text (no issue number):**
- `gh issue create --title "TITLE" --body "BODY"`
- Capture returned ISSUE number
- Apply preliminary label: defect → `bug`, docs → `documentation`, default → `enhancement`

**Existing issue:**
- If no labels, apply preliminary label as above

Allowed labels (GitHub defaults): `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `question`, `duplicate`, `invalid`, `wontfix`.

## Phase 2: Spec

1. Read context:
   - Issue body
   - `.agent/memory/architecture.md`
   - `.agent/memory/decisions/DEC-*.md`
   - `.agent/rules/project.md`

2. Produce structured spec:
   - **Scope**: 1-3 sentences
   - **Acceptance Criteria**: measurable conditions
   - **Invariants Affected**: from project.md
   - **Tasks**: decomposed into waves
   - **Files**: to create/modify
   - **Test strategy**: what to test
   - **Recommended labels**: additional labels

3. Apply labels: `gh issue edit ISSUE --add-label "label1,label2"`

4. Post Comment 1 — Requirements (posted ONCE, NEVER edited):
   ```
   gh issue comment ISSUE --body "## Requirements
   **Branch:** \`feat/ISSUE-SLUG\`

   ### Scope
   [scope]

   ### Acceptance Criteria
   [criteria]

   ### Invariants Affected
   [invariants]

   ### Files
   [files]

   ### Test Strategy
   [test strategy]
   "
   ```

5. Post Comment 2 — Execution Plan (living comment, edited throughout):
   ```
   gh issue comment ISSUE --body "## Execution

   ### Wave 1: [Name]
   - [ ] Task
   - [ ] Task

   ---
   **Status:** Starting execution
   "
   ```

6. Write tasks to `project-state.md`:
   ```
   skill: feature
   issue: #ISSUE
   branch: BRANCH
   phase: execution
   ```

## Phase 3: Worktree Setup

1. Sync main: `git fetch origin && git switch main && git merge --ff-only origin/main`
2. Create worktree: `mkdir -p REPO_ROOT/../.worktrees && git worktree add WT_ROOT -b BRANCH origin/main`
3. Copy state: `cp REPO_ROOT/.agent/memory/project-state.md WT_ROOT/.agent/memory/project-state.md`

## Phase 4: Execution (inside worktree)

### Isolation Rule
- ALL reads/writes MUST use absolute paths under `WT_ROOT`
- NEVER read from or write to REPO_ROOT
- The worktree IS the project root

### For each task `[ ]` in project-state.md:
1. Implement + test using commands from `.agent/rules/stack.md`
2. PASS → mark `[x]`, print `Done: [N/total] task`
3. FAIL → retry max 2. 3rd fail → post blocker to issue, STOP

### After EVERY completed wave:
1. Commit: `cd WT_ROOT && git add -A && git commit -m "feat(SLUG): wave N — [summary]"`
2. Update Comment 2 via `--edit-last`:
   ```
   gh issue comment ISSUE --edit-last --body "## Execution
   [updated checklist]
   ---
   **Status:** Wave N complete — X/Y tasks done
   "
   ```
3. Every 3 tasks: compress context (summarize-context skill activates)

## Phase 5: Integration

1. Verify ALL tasks `[x]`
2. Run final validation (test + build from stack.md)
   - FAIL → create fix tasks, return to Phase 4
3. Push: `cd WT_ROOT && git push -u origin BRANCH`
4. Create PR:
   ```
   gh pr create --title "feat: ISSUE_TITLE" --body "Closes #ISSUE
   ## Summary
   [scope]
   ## Changes
   [files]
   ## Test plan
   [test strategy]
   " --head BRANCH --base main
   ```
5. Final update to Comment 2 with PR URL

## Phase 6: Cleanup

1. Archive state: copy project-state.md to `.agent/memory/archive/feature-ISSUE-YYYYMMDD.md`
2. Do NOT remove worktree — may need fixes post-review
3. Output: `Done: Feature #ISSUE delivered. PR: PR_URL`

## Error Handling

| Error | Action |
|-------|--------|
| `gh auth status` fails | `Error: Run 'gh auth login' first.` |
| Issue not found | `Error: Issue #ISSUE not found.` |
| Push rejected | `git pull --rebase origin BRANCH`, retry once |
| Task fails 3x | Post blocker comment, STOP |
| Session interrupted | Next `/feature #ISSUE` resumes from pending phase |

## Resumability

When invoked with an existing worktree:
1. Read `WT_ROOT/.agent/memory/project-state.md`
2. Find first uncompleted `[ ]` task
3. Resume from appropriate phase

## Conventions

- One feature = one issue = one worktree = one branch
- Branch naming: `feat/ISSUE-SLUG`
- Worktree location: `REPO_ROOT/../.worktrees/feat/ISSUE-SLUG`
- 2 comments only: Comment 1 (Requirements — immutable), Comment 2 (Execution — living)
