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

## phase 0: resume check

1. **Schema verification** — Run `/sync-schema` auto-verification:
   - Read `.claude/stack.yml` → `schema` section. Not configured → skip silently.
   - If configured, check if `schema.md` is stale (files in `schema.paths` newer than `Last synced` date).
   - Stale or missing → run full `/sync-schema` before continuing.

2. Parse input:
   - Number or `#N` → ISSUE = N
   - URL `https://github.com/.../issues/N` → extract N
   - **`FR-\d+` (or free text containing `(FR-\d+)`)** → set FR_ID and read
     `docs/requirements/functional.md`. Extract that FR's full block (Actor,
     Trigger, Outcome, Verifiable by) into FR_CONTEXT. The planner uses this
     as built-in acceptance criteria during Phase 2 (Spec). If the project has
     `stack.yml → tracker.type: linear` and a parent issue exists in Linear with
     title prefix `[FR-N]`, set PARENT_LINEAR_ID; the issue created in Phase 1
     becomes a child of that parent. If `docs/requirements/functional.md` does
     not contain FR_ID, abort with `❌ Error: FR-N not found in docs. Run /discovery-functional first.`
   - Free text → will create issue in Phase 1

3. Verify GitHub CLI auth:
   ```
   gh auth status
   ```
   - FAIL → `❌ Error: Run 'gh auth login' first.`

4. If ISSUE exists, fetch it:
   ```
   gh issue view ISSUE --json number,title,body,state,labels
   ```
   - Issue not found → `❌ Error: Issue #ISSUE not found.`
   - Issue closed → print `⚠️ Issue #ISSUE is closed. Proceeding anyway.` and continue

5. Derive identifiers:
   - `SLUG` = kebab-case of issue title, max 40 chars
   - `BRANCH` = `feat/ISSUE-SLUG` (e.g. `feat/42-add-notifications`)
   - `REPO_ROOT` = `git rev-parse --show-toplevel`
   - `WT_ROOT` = the existing worktree's path for BRANCH from `git worktree list`
     if one exists; otherwise `REPO_ROOT/../.worktrees/BRANCH` (manual fallback
     location — native worktree isolation may place it elsewhere)

6. Check if worktree already exists:
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

1. Invoke **planner agent** with context:
   - Issue body (title + description)
   - `.claude/memory/architecture.md` (compact summary)
   - `docs/decisions/ADR-*.md` (canonical ADRs — pick the relevant ones)
   - If FR_CONTEXT is set: the FR markdown block from `docs/requirements/functional.md`.
   - `.claude/project.yml`

2. Planner produces structured spec:
   - **Scope**: 1-3 sentences describing the change
   - **Acceptance Criteria**: measurable conditions for done
   - **Invariants Affected**: which invariants from project.yml are touched
   - **Tasks**: decomposed into waves (ordered groups)
   - **Files**: to create/modify
   - **Test strategy**: what to test and how
   - **Recommended labels**: additional labels based on analysis

3. **Present plan to user and wait for approval — ONLY USER GATE IN THIS PIPELINE:**
   - If the session is in plan mode, present the spec through the native plan
     approval (ExitPlanMode) — a runtime gate is harder to skip than a prompt.
   - Otherwise print the full spec: Scope, Acceptance Criteria, Invariants Affected, Tasks (all waves), Files, Test Strategy
   - Print: `Proceed with implementation? (yes/no)`
   - **YES** → continue to step 4
   - **NO** → print `❌ Cancelled by user.` and STOP. Do NOT post GitHub comments or create worktree.

4. Apply labels from planner analysis (model: haiku):
   ```
   gh issue edit ISSUE --add-label "label1,label2"
   ```

5. Post **Comment 1 — Requirements** (posted ONCE, NEVER edited):
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

6. Post **Comment 2 — Execution Plan** (living comment, edited throughout):
   ```
   COMMENT2_URL=$(gh issue comment ISSUE --body "## Execution

   ### Wave 1: [Name]
   - [ ] Task description
   - [ ] Task description

   ### Wave 2: [Name]
   - [ ] Task description

   ---
   **Status:** Starting execution
   ")
   ```
   Extract `COMMENT2_ID` from the returned URL (`...#issuecomment-<ID>`).
   ALL later updates edit this comment by ID — never `--edit-last`, which
   would overwrite whatever comment happens to be last (e.g. a blocker or
   CI-failure comment posted in between).

7. Write tasks to `project-state.md` with metadata:
   ```
   skill: feature
   issue: #ISSUE
   branch: BRANCH
   comment2_id: COMMENT2_ID
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

2. Create the worktree:
   - **Native (preferred):** if the runtime offers worktree isolation (an
     EnterWorktree tool or `--worktree`), use it with branch BRANCH — it honors
     `worktree.symlinkDirectories` (no duplicated node_modules per worktree)
     and `worktree.baseRef` from settings.json. Set WT_ROOT to the path it
     reports.
   - **Fallback (manual):**
     ```
     mkdir -p REPO_ROOT/../.worktrees
     git worktree add WT_ROOT -b BRANCH origin/main
     ```

3. Copy state to worktree:
   ```
   cp REPO_ROOT/.claude/memory/project-state.md WT_ROOT/.claude/memory/project-state.md
   ```

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

**Tracker sync** (if `stack.yml → tracker.type: linear` and LINEAR_ISSUE_ID is set):
- Phase 4 start → set issue status to **In Progress**
- Phase 5 step 6 (PR created) → set issue status to **In Review**
- Phase 6 → set issue status to **Done**
- Use `gh` or Linear CLI as configured in `stack.yml → tracker.cli`. Skip silently if CLI unavailable.

**For each task `[ ]` in `WT_ROOT/.claude/memory/project-state.md`:**

If the runtime exposes a native task list (TaskCreate/TaskUpdate), mirror the
wave's tasks there for in-session visibility — `project-state.md` remains the
durable source for cross-session resume.

1. **Builder agent** (model: sonnet) implements + tests
2. **PASS** → mark `[x]`, print `✅ [task_number] task_description`
3. **FAIL** → retry (max 2 retries). 3rd failure → post blocker to issue, write state, STOP:
   ```
   gh issue comment ISSUE --body "Blocked: [task description]. Error: [details]"
   ```
   Then write to `WT_ROOT/.claude/memory/project-state.md`:
   ```
   phase: blocked
   blocker: [task description] — [error summary]
   ```
   Resume: next `/feature #ISSUE` reads `phase: blocked` → prints blocker description → asks user:
   `"Blocker: [description]. Resolved? (yes/no)"` → YES: set `phase: execution`, continue from first `[ ]` task → NO: STOP.

**After EVERY completed wave, run these 3 steps in order — NO EXCEPTIONS:**

1. **Commit** — stage everything except memory state (session-local; committing
   it churns every PR and contradicts the git agent's "never -A" rule):
   ```
   cd WT_ROOT && git add -- . ':!.claude/memory' && git commit -m "feat(SLUG): wave N — [summary]"
   ```

2. **Rebase check** — detect main divergence before it compounds:
   ```
   cd WT_ROOT && git fetch origin && git merge-base --is-ancestor origin/main HEAD
   ```
   - Exit 0 (main is ancestor of HEAD, no divergence) → continue
   - Exit 1 (main has new commits) → rebase:
     ```
     cd WT_ROOT && git rebase origin/main
     ```
     - Conflicts → resolve, then `git rebase --continue`. If unresolvable → post blocker comment and STOP:
       ```
       gh issue comment ISSUE --body "Blocked: rebase conflict after wave N. Resolve manually in WT_ROOT."
       ```

3. **Update Comment 2 (Execution Plan) by ID** (`comment2_id` from project-state.md):
   ```
   gh api repos/{owner}/{repo}/issues/comments/COMMENT2_ID -X PATCH -f body="## Execution

   ### Wave 1: [Name]
   - [x] Task description
   - [x] Task description

   ### Wave 2: [Name]
   - [ ] Task description

   ---
   **Status:** Wave N complete — X/Y tasks done
   "
   ```
   If `comment2_id` is missing from project-state.md (state written by an older
   run), post a new comment, extract its ID from the returned URL, and persist
   it to project-state.md before continuing.

*(Context compression is the runtime's job — auto-compact handles it. Do not
spend turns summarizing manually; just keep project-state.md current so a
compacted or fresh session can resume.)*

---

## phase 5: integration

1. Verify ALL tasks are `[x]` in `WT_ROOT/.claude/memory/project-state.md`

2. Run final validation (tests + build):
   - Read `WT_ROOT/.claude/stack.yml` for validate command and exec_prefix
   - Execute: `cd WT_ROOT && {exec_prefix} {stack.commands.validate}`
   - If `validate` not defined, run `{stack.commands.test}` then `{stack.commands.build}`
   - Build step catches SSR/runtime errors (missing providers, import errors, type mismatches)
   - **FAIL** → create fix tasks, return to Phase 4

3. **Code review** (built-in `/code-review`):
   - Scope: files changed in this branch only — `cd WT_ROOT && git diff main...HEAD --name-only`
   - Run `/code-review` on those files (not the full codebase)
   - Collect findings (model: sonnet)
   - **Findings severity: critical** (security issue, data loss risk, invariant violation) →
     post as a GitHub comment:
     ```
     gh issue comment ISSUE --body "⚠️ Code review flagged critical issues before PR creation:\n\n[findings]"
     ```
     Then continue — do NOT block the pipeline.
   - **No critical findings** → append a `## Code Review` section to the PR body in step 5

4. Manual verification (if stack uses docker) — the Phase 4 isolation rule
   still applies: never `cd REPO_ROOT`, never stop the main checkout's services.
   - Start containers in worktree: `cd WT_ROOT && docker compose up -d`
   - Port already in use (main checkout running) → print
     `ℹ️ Port busy — stop the main checkout's containers manually to verify this worktree.`
     and continue.
   - On success print: `ℹ️ App running at [URL from stack.commands.dev / compose ports] — proceeding to push.`
   - Continue without waiting for user input.

5. Push branch:
   ```
   cd WT_ROOT && git push -u origin BRANCH
   ```
   - Push rejected → `cd WT_ROOT && git pull --rebase origin BRANCH`, retry once

6. Create PR as **draft** (model: haiku):
   ```
   gh pr create --draft --title "feat: ISSUE_TITLE" --body "Closes #ISSUE

   ## Summary
   [spec scope from Phase 2]

   ## Changes
   [list of files changed]

   ## Test plan
   [test strategy from Phase 2]

   ## Code Review
   [findings from step 3, or "No issues found." if clean]
   " --head BRANCH --base main
   ```
   Draft prevents premature review requests while CI runs.

7. **CI monitoring** — wait for checks after PR creation:
   ```
   timeout 600 gh pr checks PR_URL --watch --interval 30
   ```
   - `timeout` enforces the 10-minute cap. Exit 124 (timed out) → treat as CI
     still pending: leave the PR as draft and STOP; next `/feature #ISSUE` re-checks.
   - If no checks registered after 2 minutes → skip silently (repo may not have CI).
   - **All checks pass** → mark PR ready for review:
     ```
     gh pr ready PR_URL
     ```
     Note `CI: ✅` in step 8 comment update.
   - **Any check fails** → post comment on issue:
     ```
     gh issue comment ISSUE --body "CI failed on PR_URL:\n\n[failing check names and links]"
     ```
     Then update Comment 2 with `CI: ❌` and STOP. PR stays as draft. Do NOT proceed to Phase 6 until CI is green.
     Resume: next `/feature #ISSUE` detects all tasks `[x]` + PR exists → skips to CI re-check.

8. Final update to Comment 2 (Execution Plan) by ID:
   ```
   gh api repos/{owner}/{repo}/issues/comments/COMMENT2_ID -X PATCH -f body="## Execution

   ### Wave 1: [Name]
   - [x] Task description
   ...

   ---
   **PR:** PR_URL
   **CI:** ✅ / ❌
   **Status:** Complete — Y/Y tasks done. Awaiting user merge.
   "
   ```

---

## phase 6: cleanup

1. Archive state and sync back to main repo (model: haiku):
   ```
   mkdir -p REPO_ROOT/.claude/memory/archive/
   cp WT_ROOT/.claude/memory/project-state.md REPO_ROOT/.claude/memory/archive/feature-ISSUE-$(date +%Y%m%d).md
   cp WT_ROOT/.claude/memory/project-state.md REPO_ROOT/.claude/memory/project-state.md
   ```

2. **DO NOT remove worktree** — may need fixes post-review if CI fails or reviewer requests changes.

3. Output: `✅ Feature #ISSUE delivered. PR: PR_URL — merge when ready.`

4. **Stale worktree notice** — list worktrees untouched for 7+ days
   (branches contain a slash, so worktree dirs sit at depth 2):
   ```
   find REPO_ROOT/../.worktrees -mindepth 2 -maxdepth 2 -type d -mtime +7 2>/dev/null
   ```
   If any found, print:
   `"ℹ️ Stale worktrees detected. Run /cleanup-worktrees to review and remove merged ones."`

*(Merging and worktree cleanup are the user's responsibility.)*

---

## error handling

| Error | Action |
|-------|--------|
| `gh auth status` fails | `❌ Error: Run 'gh auth login' first.` |
| Issue not found | `❌ Error: Issue #ISSUE not found.` |
| Push rejected | `git pull --rebase origin BRANCH`, retry once |
| Task fails 3x | Post blocker comment to issue, STOP |
| Rebase conflict during wave | Post blocker comment, STOP — resolve manually in WT_ROOT |
| CI checks fail | Post failure comment, STOP — next `/feature #ISSUE` re-checks CI |
| Session interrupted | Next `/feature #ISSUE` resumes automatically from pending phase |
| Worktree conflicts | `cd WT_ROOT && git rebase origin/main`, resolve conflicts |

---

## resumability

When `/feature #N` is invoked and a worktree for that issue already exists:

1. Read `WT_ROOT/.claude/memory/project-state.md`
2. Parse metadata: `skill`, `issue`, `branch`, `comment2_id`, `phase`
3. Find first uncompleted task `[ ]`
4. Resume from the appropriate phase:
   - All tasks `[ ]` and no spec → Phase 2
   - Tasks exist but no worktree work started → Phase 4
   - Some tasks `[x]`, some `[ ]` → Phase 4 (continue)
   - `phase: blocked` → print blocker description, ask user if resolved → YES: resume Phase 4 → NO: STOP
   - All tasks `[x]`, no PR → Phase 5
   - All tasks `[x]`, PR exists, CI pending/failed → Phase 5 step 7 (CI re-check)
   - All tasks `[x]`, PR exists, CI passed → Phase 6

---

## conventions

- **One feature = one issue = one worktree = one branch**
- Branch naming: `feat/ISSUE-SLUG`
- Worktree location: `REPO_ROOT/../.worktrees/feat/ISSUE-SLUG`
- Commits inside worktree use conventional format: `feat(SLUG): description`
- All GitHub communication via `gh` CLI — no API tokens needed beyond `gh auth`
- **2 pipeline comments**: Comment 1 (Requirements — immutable), Comment 2 (Execution — living, edited via stored `comment2_id`, never `--edit-last`). Blocker/CI comments are additional and never edited.
- **Labels**: GitHub defaults only (`bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `question`, `duplicate`, `invalid`, `wontfix`)
