# Claude Code Multi-Agent Framework

> **This is a proposal, not a prescription.** This framework represents one approach to orchestrating [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as a multi-agent development team. It is not the definitive way to work with Claude Code — it's a starting point you can adapt, modify, extend, or partially adopt to fit your workflow. Take what works, change what doesn't.

A multi-agent orchestration framework that turns Claude Code into a development team with specialized roles, persistent memory, and automated workflows.

It uses **native dispatch** — agents have `description` fields in their YAML frontmatter and Claude invokes them automatically. Skills use the standard `name/SKILL.md` format with `user-invocable: true`.

**[Leer en Espanol](README_ES.md)**

---

## Why This Exists

Claude Code is powerful out of the box, but for complex projects you often want:

- **Role separation** — a planner that doesn't write code, a builder that doesn't touch architecture decisions
- **Persistent memory** — context that survives across sessions (architecture docs, task state, decisions)
- **Structured workflows** — repeatable pipelines for features, quick fixes, research, audits
- **Traceability** — from GitHub Issue to spec to branch to commits to PR, all connected

This framework provides a file-based convention that gives Claude Code these capabilities without external tooling. It's just markdown files and YAML — Claude reads them and follows the instructions.

---

## Two Variants

The framework ships in two variants. Choose the one that fits your workflow:

| | **Linear** (`.claude/`) | **Feature-driven** (`worktree/.claude/`) |
|---|---|---|
| **Workflow** | One change at a time, sequential | One issue = one worktree = one branch |
| **GitHub Issues** | No | Yes — reads/creates issues, posts progress, creates PRs |
| **Isolation** | Works in the current directory | One git worktree per feature, parallel work |
| **Traceability** | Conventional commits | Issue → spec → worktree → commits → PR |
| **Resumability** | `/develop` resumes from `project-state.md` | `/feature #42` resumes from the worktree |
| **Best for** | Solo work, simple projects | Teams, issue-driven projects, multiple features |

You can start with Linear and switch to Feature-driven later — the Feature-driven variant is a superset (same agents + skills + one extra skill).

### Flow Visualization

**Linear (`/develop`)** — Sequential cycle for individual work:

```mermaid
flowchart LR
    A[Request] --> B{Triage}
    B -->|Clean state| C[Planner: Spec + Tasks]
    B -->|Pending tasks| D
    C --> D[Execution Loop]
    D --> E{Builder: Implement + Test}
    E -->|PASS| F[Mark task x]
    F -->|Every 3 tasks| G[/summarize-context]
    G --> D
    F -->|Tasks remaining| D
    E -->|FAIL x3| H[STOP: Ask for help]
    F -->|All x| I[Git Agent: Commit]
    I --> J[/archive-state]
```

**Feature-driven (`/feature`)** — Issue-based cycle with worktrees for teams:

```mermaid
flowchart LR
    A["#42 or free text"] --> B{gh auth status}
    B -->|OK| C{Worktree exists?}
    C -->|Yes| D[RESUME]
    C -->|No| E[Intake: gh issue create/view]
    E --> F[Planner: Spec → comment on issue]
    F --> G[git worktree add]
    G --> H[Execution Loop in WT_ROOT]
    D --> H
    H --> I{Builder: Implement + Test}
    I -->|PASS| J[Mark task x]
    J -->|Every 3 tasks| K[/summarize-context]
    K --> H
    J -->|Wave complete| L[git commit in worktree]
    L -->|Waves remaining| H
    I -->|FAIL x3| M[Post blocker on issue, STOP]
    L -->|All x| N[Final test + git push]
    N --> O[gh pr create]
    O --> P["Comment: PR URL on issue"]
```

### When to Choose Each

| Criteria | Linear | Feature-driven |
|----------|--------|----------------|
| Solo work, one change at a time | Ideal | Overkill |
| Team, multiple features in parallel | Insufficient | Ideal |
| Project without GitHub Issues | Only option | N/A |
| Project with issues + PRs as workflow | Possible but manual | Automated |
| Need issue → PR traceability | Not included | Built-in |
| Simple project (< 10 files) | Ideal | Overkill |
| Large project with protected areas | Works | Works + isolation |
| Need to resume after interruption | `/develop` resumes | `/feature #N` resumes with worktree intact |

**Rule of thumb**: If your workflow already uses GitHub Issues and Pull Requests, choose Feature-driven. If you work solo and commit straight to main, choose Linear.

---

## Getting Started

### Step 1: Copy the framework

**Linear variant** — sequential work, no GitHub Issues:

```bash
# From your project root
cp -r /path/to/framework/.claude/ ./.claude/
```

**Feature-driven variant** — with GitHub Issues, worktrees, and PRs:

```bash
# From your project root
cp -r /path/to/framework/worktree/.claude/ ./.claude/
```

> Both variants include the same agents, skills, and memory system. The feature-driven variant adds the `/feature` skill and permissions for `gh` and `git worktree`.

### Step 2: Configure your project

Edit `.claude/project.yml` — this defines WHAT your project is:

```yaml
name: MySaaS
description: Inventory management platform

domain:
  language: en
  entities:
    - organization (tenant)
    - user
    - warehouse
    - product
    - order

tenant:
  enabled: true
  column: org_id
  table: organizations
  isolation: rls

invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id. No cross-tenant data leaks.
    severity: critical
  - name: Stock Integrity
    rule: Stock decrements MUST be atomic. No overselling.
    severity: critical

critical_flows:
  - name: Order Fulfillment
    description: Validate stock → reserve → charge → dispatch
    tables: [orders, inventory, payments]
    type: transaction

gate_protected_areas:
  - pattern: "migrations/"
    reason: Schema changes require /develop
  - pattern: "middleware*"
    reason: Auth and routing
```

### Step 3: Configure your stack

Edit `.claude/stack.yml` — this defines HOW your project runs:

```yaml
name: node-docker-prisma

runtime:
  exec_prefix: "docker compose exec api"
  note: "No local runtime. Always use exec_prefix."

commands:
  install: "npm install"
  test: "npx vitest run"
  test_single: "npx vitest run {file}"
  lint: "npx eslint {path}"
  type_check: "npx tsc --noEmit"
  build: "npm run build"
  dev: "npm run dev"

paths:
  source: "src/"
  tests: "tests/"
  migrations: "prisma/migrations/"
  config: "package.json"

conventions:
  test_file_pattern: "{name}.test.ts"
  module_structure: "src/{module}/"

framework:
  name: "Express + Prisma"
  backend: "PostgreSQL"
  orm: "Prisma"
```

### Step 4: Document your architecture

Edit `.claude/memory/architecture.md` — this is the source of truth for your system design:

- System overview
- Stack and execution model
- Data model (entities, relationships)
- Roles and authorization
- Critical flows (contracts: inputs → validations → steps → outputs)
- Forbidden patterns

Agents consult this file before writing any code.

### Step 5: Start using it

```bash
claude
# Inside Claude Code:
/develop Implement notification system
/quick Fix the login button text
/research Compare Redis vs Memcached for caching
/feature #42                              # (Feature-driven only)
/feature Add real-time alerts system       # (Feature-driven only)
/feature #42                          # Resume if interrupted
```

---

## How It Works

### Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md                          # Entry point — refs to project.yml and stack.yml
│   ├── project.yml                        # WHAT: identity, domain, invariants, critical flows
│   ├── stack.yml                          # HOW: runtime, commands, paths, conventions
│   ├── settings.local.json                # Tool permissions
│   │
│   ├── agents/                            # 3 subagents with native frontmatter
│   │   ├── planner.md                     #   Plans, designs, researches
│   │   ├── builder.md                     #   Codes, tests, executes
│   │   └── git.md                         #   Commits, pushes (safety gate)
│   │
│   ├── skills/                            # User-invocable workflows (/name)
│   │   ├── develop/SKILL.md               #   Full E2E pipeline
│   │   ├── quick/SKILL.md                 #   Fast-path, no planning
│   │   ├── research/SKILL.md              #   Technical investigation
│   │   ├── feature/SKILL.md               #   (Feature-driven) Issue → PR pipeline
│   │   ├── parallel/SKILL.md              #   Multi-session execution
│   │   ├── audit/SKILL.md                 #   Security audit
│   │   ├── summarize-context/SKILL.md     #   Context compression
│   │   ├── validate-invariants/SKILL.md   #   Invariant verification
│   │   ├── write-tests/SKILL.md           #   Testing strategy
│   │   ├── prepare-commit/SKILL.md        #   Commit message generation
│   │   ├── analyze-architecture/SKILL.md  #   Architecture drift detection
│   │   └── archive-state/SKILL.md         #   Archive completed state
│   │
│   └── memory/                            # Persistent state
│       ├── architecture.md                #   System design (source of truth)
│       ├── project-state.md               #   Active tasks, progress (cap 80 lines)
│       ├── research.md                    #   Research log
│       ├── locks.md                       #   Multi-session coordination (TTL 30 min)
│       ├── decisions/                     #   Architectural decision records
│       │   └── TEMPLATE.md                #     DEC-####.md template
│       └── archive/                       #   Completed states
```

### Agents

Agents have `description` and `allowed-tools` in their YAML frontmatter. Claude Code invokes them automatically when the task fits.

| Agent | Role | Can | Cannot |
|-------|------|-----|--------|
| `planner` | Planner + Architect + Researcher | Read, analyze, design, write to memory/ | Code, commits, Bash |
| `builder` | Programmer + QA | Write code, tests, execute commands | Edit architecture, commits |
| `git` | Release Manager | Commits and push | Write code or edit files |

### Skills

Skills are workflows invoked with `/name` inside Claude Code.

**Primary:**

| Skill | When to use | Variant |
|-------|-------------|---------|
| `/develop` | New feature, complex bug, any change needing planning | Both |
| `/quick` | Trivial change not touching protected areas (typo, CSS, simple field) | Both |
| `/research` | Evaluate technical options before deciding | Both |
| `/feature` | Full pipeline: issue → spec → worktree → implementation → PR | Feature-driven |

**Auxiliary:**

| Skill | What it does |
|-------|-------------|
| `/parallel` | Execute tasks from the current wave in multiple terminals |
| `/audit` | Security audit of the codebase |
| `/write-tests` | Define testing strategy and generate tests |
| `/prepare-commit` | Validate tests + generate conventional commit message |
| `/validate-invariants` | Verify critical rules are not broken |
| `/analyze-architecture` | Compare current code vs architecture.md |
| `/summarize-context` | Compress state to free context window tokens |
| `/archive-state` | Archive completed state and reset the tracker |

---

## Workflows

### `/develop` — Full Pipeline

The main workflow. Plans, implements in a loop, and commits.

```
PHASE 0: Triage
  Read project-state.md → pending tasks? → RESUME
  Analyze request → needs architecture change?

PHASE 1: Architecture (conditional)
  Read decisions/ to avoid re-litigating past decisions
  Planner agent updates architecture.md
  Record new decisions as DEC-####.md
  Output: "✅ Architecture updated."

PHASE 2: Execution Loop
  For each task [ ] in project-state.md:
    Builder agent implements + tests
    PASS → mark [x], persist state
    FAIL → retry (max 2) → STOP on 3rd failure
  Every 3 tasks → /summarize-context

PHASE 3: Finalization
  Git agent commit + push
  /archive-state → reset project-state.md
```

### `/quick` — Fast Path

For trivial changes that don't need planning.

```
Gate: Read project.yml → touches protected area?
  YES → ABORT, suggest /develop

Preflight:
  git diff --stat → >5 files or >200 lines? → ABORT, suggest /develop
  /validate-invariants → FAIL? → ABORT

Build:
  Builder agent implements → Git agent commits
```

### `/feature` — Issue-to-PR (Feature-driven variant)

Full pipeline from GitHub Issue to Pull Request, with worktree isolation.

```
PHASE 0: Resume Check
  Parse input (#42, URL, or free-text description)
  gh auth status → verify authentication
  If worktree exists → RESUME from pending phase

PHASE 1: Intake
  Free text → gh issue create
  Existing issue → read content
  Post comment: "Session started"

PHASE 2: Spec
  Planner agent produces structured spec
  Post spec as comment on issue
  Write tasks to project-state.md

PHASE 3: Worktree Setup
  git fetch origin
  git worktree add WT_ROOT -b feat/ISSUE-SLUG origin/main
  Copy state to worktree

PHASE 4: Execution (inside the worktree)
  Builder agent implements + tests each task
  Commits per wave inside the worktree
  Post progress to issue

PHASE 5: Integration
  Test suite final → git push → gh pr create
  Post PR URL to issue

PHASE 6: Cleanup
  Archive state, post final summary
  DO NOT remove worktree (may need fixes post-review)
```

**Usage examples:**

```bash
claude
# Inside Claude Code:
/feature #42                          # Implement an existing issue
/feature Add real-time alerts system  # Create issue + implement
/feature #42                          # Resume if interrupted
```

**Worktree path convention:**

```
my-project/                          # REPO_ROOT (main checkout)
├── .claude/
├── src/
└── ...

.worktrees/                          # Sibling directory to repo
├── feat/42-add-notifications/       # Worktree for issue #42
└── feat/57-fix-auth/                # Another feature in parallel
```

### `/parallel` — Multi-session

Open multiple Claude Code terminals to execute tasks from the same wave in parallel:

```bash
# Terminal 1        # Terminal 2        # Terminal 3
/parallel           /parallel           /parallel
```

Each session claims a different task via coordination in `locks.md`. Locks older than 30 minutes are considered expired and released automatically.

---

## Work Organization (Waves)

**Waves** are the fundamental unit of work organization in the framework. A wave is a logical group of coherent tasks that are executed together, validated together, and committed together.

### What is a wave

```
Wave 1: Database
  [ ] Create migration with new tables
  [ ] Add columns to existing tables
  [ ] Update schema.sql

Wave 2: Backend
  [ ] Create server actions
  [ ] Update existing queries
  [ ] Add validations

Wave 3: UI
  [ ] Create form components
  [ ] Update existing pages
  [ ] Add visual feedback
```

### Why waves instead of a flat list

- **Context focus**: The builder agent works in one domain at a time (DB, then backend, then UI), reducing errors from context switching
- **Memory checkpoints**: `/summarize-context` runs every 3 tasks, and waves provide natural cut-off points
- **Atomic commits**: Each completed wave = one meaningful commit (`feat(auth): wave 1 — database schema`)
- **Parallelization**: With `/parallel`, multiple sessions pick tasks from the same wave without conflicts

### Wave lifecycle

```
Planner defines waves in project-state.md
        ↓
Builder executes task [ ] → test → PASS → mark [x]
        ↓ (every 3 tasks)
/summarize-context compresses state
        ↓ (wave complete)
Git agent: atomic commit for the wave
        ↓ (next wave)
Repeat until all [x]
        ↓
/archive-state → reset
```

### Waves in each variant

| | Linear (`/develop`) | Feature-driven (`/feature`) |
|---|---|---|
| Who defines waves | Planner agent in project-state.md | Planner agent, posted as comment on issue |
| Commit per wave | Yes, at the end of each wave | Yes, inside the worktree |
| Visible progress | In local project-state.md | In project-state.md + comments on GitHub Issue |
| Parallelizable | Yes, via `/parallel` | Yes, via `/parallel` inside the worktree |

---

## Automated Testing Strategy

The framework runs tests at multiple levels, configured in `stack.yml`. You don't need to invoke tests manually — they run automatically at the right moments.

### Testing levels

```
Level 3: System Validations ─────────────────────────────────
         /validate-invariants (critical rules from project.yml)
         /audit (security, tenant isolation, auth flows)
         /analyze-architecture (drift vs architecture.md)

Level 2: Integration Tests ──────────────────────────────────
         End of wave or pre-commit
         Command: {exec_prefix} {commands.test}
         Run by: /prepare-commit, /feature Phase 5

Level 1: Atomic Tests (Unit) ────────────────────────────────
         After each individual task
         Command: {exec_prefix} {commands.test_single}
         Run by: builder agent
```

### When each level runs

| Moment | Level 1 (Unit) | Level 2 (Integration) | Level 3 (System) |
|--------|----------------|-----------------------|-------------------|
| Builder completes a task | **Yes** — test_single | No | No |
| Wave complete | No | **Yes** — test | No |
| Pre-commit (`/prepare-commit`) | No | **Yes** — test | **Yes** — /validate-invariants |
| Pre-PR (`/feature` Phase 5) | No | **Yes** — full test suite | No |
| On demand | `/write-tests` generates | Manual | `/audit`, `/analyze-architecture` |

### Configuration in stack.yml

```yaml
commands:
  test: "npx vitest run"            # Level 2: full suite
  test_single: "npx vitest run {file}"  # Level 1: individual file
  lint: "npx eslint {path}"         # Code quality
  type_check: "npx tsc --noEmit"    # Type checking
```

### Failure behavior

| Level | Failure | Action |
|-------|---------|--------|
| Level 1 | Unit test fails | Builder retries (max 2). 3rd failure → STOP |
| Level 2 | Integration test fails | `/prepare-commit` rejects. `/feature` returns to Phase 4 with fix tasks |
| Level 3 | Invariant violated | `/validate-invariants` emits critical FAIL. Change rejected |

---

## Daily Operation Guide

### Path A: Sequential Work (Linear)

**Start of day — resume paused work:**

```bash
claude
/develop
# If pending tasks exist in project-state.md → resumes automatically
# If clean → describe the new task
```

**Quick change without planning:**

```bash
/quick Change the login button color
# Gate: checks it doesn't touch protected areas
# If it touches migrations/ or middleware → redirects to /develop
```

**Research before deciding:**

```bash
/research Compare Stripe vs Square for payments
# Planner investigates, writes to research.md, gives recommendation
```

**Typical flow for a complete feature:**

```
1. /develop Implement notification system
2. Planner creates spec with waves in project-state.md
3. Builder executes Wave 1 (DB) → test → commit
4. Builder executes Wave 2 (Backend) → test → commit
5. Builder executes Wave 3 (UI) → test → commit
6. /prepare-commit → final validation
7. Git agent: push
8. /archive-state → clean state
```

**If the session is interrupted:**

```bash
# Next session:
/develop
# Reads project-state.md → finds pending [ ] tasks → RESUME
```

### Path B: Issue Management (Feature-driven)

**Implement an existing issue:**

```bash
/feature #42
# Reads issue → generates spec → creates worktree → implements → PR
```

**Create issue from description:**

```bash
/feature Add email alerts system
# Creates issue on GitHub → generates spec → creates worktree → implements → PR
```

**Work on multiple features in parallel:**

```
Terminal 1: /feature #42    → worktree feat/42-add-alerts
Terminal 2: /feature #57    → worktree feat/57-fix-auth
# Each feature in its own worktree, no conflicts
```

**Resume an interrupted feature:**

```bash
/feature #42
# Detects existing worktree → reads worktree's project-state.md → RESUME
# The worktree preserves all state: code, commits, tests
```

**Complete lifecycle of an issue:**

```
1. /feature #42
2. gh reads issue → Planner generates spec → comment on issue
3. git worktree add → branch feat/42-slug
4. Builder executes waves inside the worktree
5. Each wave → commit → progress comment on issue
6. Final test suite → git push → gh pr create
7. Comment on issue: "PR created: URL"
8. State archived, worktree remains for post-review fixes
```

**Switch between worktrees without losing context:**

```bash
# Each feature's state lives in its worktree:
# .worktrees/feat/42-add-alerts/.claude/memory/project-state.md
# .worktrees/feat/57-fix-auth/.claude/memory/project-state.md

# Each /feature #N reads ITS project-state.md, not the main repo's
```

---

## What to Edit Per Project

Only 3 files contain your project-specific data. Everything else is generic framework.

| File | What to put | When to edit |
|------|------------|--------------|
| `project.yml` | Name, domain, tenant config, invariants, critical flows, protected areas | When adopting the framework |
| `stack.yml` | Runtime, commands, paths, stack conventions | When adopting the framework |
| `memory/architecture.md` | System design, data model, roles, patterns | At start and as architecture evolves |

Agents, skills, and CLAUDE.md **are not edited** — they're generic and reference `{stack.*}` and `{project.*}`.

---

## Memory and Resilience

### Memory files

| File | Purpose | Written by |
|------|---------|------------|
| `architecture.md` | System design | Planner agent |
| `project-state.md` | Active tasks, progress, focus | Planner + skills |
| `research.md` | Technical research | Planner agent |
| `decisions/DEC-*.md` | Architectural decisions with context and alternatives | Planner agent |
| `locks.md` | Multi-session coordination (TTL 30 min) | /parallel |

### Resilience mechanisms

- **Atomic persistence**: State is written to `project-state.md` after each task. If the session is interrupted, `/develop` or `/feature` resumes automatically.
- **Context compression**: `/summarize-context` runs every 3 tasks, keeping the tracker under 80 lines.
- **Archiving**: `/archive-state` moves completed states to `memory/archive/` and resets the tracker.
- **Decision log**: Architectural decisions persist in `memory/decisions/` to avoid re-litigating in future sessions.
- **Lock TTL**: Locks in `/parallel` expire after 30 minutes, preventing orphaned locks from interrupted sessions.

---

## Extending the Framework

This is a starting point. Modify it freely.

### Add an agent

Create `.claude/agents/my-agent.md`:

```yaml
---
description: >
  Description of when Claude should invoke this agent.
  Include usage context so automatic dispatch works.
allowed-tools:
  - Read
  - Grep
  - Bash
disallowed-tools:
  - Write
---

# My Agent

Role instructions here.
```

### Add a skill
Create `.claude/skills/my-skill/SKILL.md`:

```yaml
---
name: my-skill
description: >
  What this skill does and when to invoke it.
user-invocable: true
---

# /my-skill

## Flow
1. Step one
2. Step two
```

### Add tool permissions

Edit `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(docker compose exec:*)",
      "Bash(tree:*)",
      "Bash(test:*)"
    ]
  }
}
```

---

## FAQ

**Does it work without Docker?**
Yes. Set `exec_prefix: ""` in `stack.yml` and commands run directly.

**Can I use it with another LLM?**
It's designed for Claude Code, but the `.md` files are natural language instructions that other LLMs could interpret.

**What if Claude ignores a constraint?**
Constraints exist at 3 levels: `project.yml` (invariants), `architecture.md` (patterns), and `project-state.md` (active context). `/summarize-context` refreshes the state periodically.

**Can I use only some skills?**
Yes. Each skill is independent. Delete the ones you don't need.

**Do I need both variants?**
No. Pick one. If you're working solo on a simple project, Linear is fine. If you work with GitHub Issues and want worktree isolation, use Feature-driven.

**Is this the "right" way to use Claude Code?**
No. This is one approach that works well for structured, multi-step development. Claude Code is flexible — you might find a completely different organization that suits you better. Use this as inspiration, not gospel.

---

## License

Free to use. Adapt it to your project.
