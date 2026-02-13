# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

> **Note:** This is an orchestration method I have been testing in a few projects. Take what works, change what doesn't.

**Orquesta** is a multi-agent framework that turns Claude Code into a development team with specialized roles, persistent memory, and automated workflows.

It uses **native dispatch** — agents have `description` fields in their YAML frontmatter and Claude invokes them automatically. Skills use the standard `name/SKILL.md` format with `user-invocable: true`.

**[Leer en Español](README_ES.md)**

## 🤝 Recommended Tools

We recommend using **[Claude Code Templates](https://github.com/davila7/claude-code-templates)** by **davila7** alongside Orquesta.
Specifically, the **Analytics Dashboard** (`npx claude-code-templates --analytics`) provides real-time visualization of your Orquesta agents' thought process and token usage.

---

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

### Step 2: Let Claude configure your project

Instead of editing files manually, **ask Claude to do it for you**. Open Claude Code in your project and describe your domain:

```bash
claude
```

Then tell Claude what your project is about. Be specific about your domain, stack, and constraints:

```
Configure this project's .claude/ directory for my project.
It's a [describe your project — e.g., "multi-tenant SaaS for restaurant management"].

Stack: [your stack — e.g., "Next.js 14 + Supabase + Prisma, running in Docker"]
Entities: [your domain entities — e.g., "organizations, users, restaurants, menus, orders, reservations"]
Multi-tenant: [yes/no, and how — e.g., "yes, RLS with org_id column"]

Key invariants:
- [e.g., "All queries must filter by org_id — no cross-tenant data leaks"]
- [e.g., "Order totals must be recalculated server-side — never trust client amounts"]

Critical flows:
- [e.g., "Order placement: validate menu → check availability → create order → notify kitchen"]

Read project.yml, stack.yml, and memory/architecture.md, then fill them in aligned to my domain.
```

Claude will:
1. Read the template files (`project.yml`, `stack.yml`, `architecture.md`)
2. Fill in `project.yml` with your entities, invariants, critical flows, and protected areas
3. Fill in `stack.yml` with your runtime commands, paths, and conventions
4. Fill in `architecture.md` with your system design, data model, roles, and patterns
5. Optionally configure `schema` sync if you have ORM models or migrations

> **Tip:** The more specific you are about your domain rules and constraints, the better Claude will enforce them during development. Invariants are the guardrails — Claude will stop and report if any is violated.

### Step 3: Verify the configuration

After Claude configures the files, review them:

```bash
# Inside Claude Code:
Read .claude/project.yml and .claude/stack.yml and tell me what you configured
```

Make sure:
- `project.yml` has your entities, invariants, and critical flows
- `stack.yml` has your actual commands (test, lint, build, dev)
- `architecture.md` reflects your real system design
- If you use ORM models, `stack.yml` has the `schema` section configured

### Step 4: Start your first feature

With the framework configured, you're ready to build. Use `/feature` for the full pipeline (Feature-driven variant) or `/develop` for the linear pipeline:

**Option A — `/feature` (recommended for issue-driven work):**

```bash
claude
# Describe what you want to build:
/feature Add user registration with email verification

# Or reference an existing GitHub issue:
/feature #42
```

What happens:
1. Creates a GitHub issue (or reads an existing one)
2. Plans the implementation: scope, acceptance criteria, tasks in waves
3. Posts the spec as a comment on the issue
4. Creates an isolated worktree and branch (`feat/42-add-user-registration`)
5. Implements each task, running tests after each one
6. Commits per wave, updates the issue with progress
7. Pushes and creates a PR when done

If interrupted at any point, just run `/feature #42` again — it resumes from where it left off.

**Option B — `/develop` (for linear, sequential work):**

```bash
claude
/develop Implement notification system
```

**Option C — `/quick` (for trivial changes):**

```bash
claude
/quick Fix the login button text
```

**Other useful commands:**

```bash
/research Compare Redis vs Memcached for caching    # Investigate before deciding
/sync-schema                                         # Force-sync data model
/audit src/auth                                      # Security audit
```

### Manual configuration reference

If you prefer to edit the files manually instead of asking Claude, here are examples:

<details>
<summary>project.yml example</summary>

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

</details>

<details>
<summary>stack.yml example</summary>

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
  validate: "npx vitest run && npm run build"

paths:
  source: "src/"
  tests: "tests/"
  migrations: "prisma/migrations/"
  config: "package.json"

conventions:
  test_file_pattern: "{name}.test.ts"
  module_structure: "src/{module}/"

schema:
  source: models
  paths:
    - prisma/schema.prisma

framework:
  name: "Express + Prisma"
  backend: "PostgreSQL"
  orm: "Prisma"
```

</details>

<details>
<summary>Other stack examples</summary>

```yaml
# Python + FastAPI
name: python-docker
runtime:
  exec_prefix: "docker compose exec api"
commands:
  test: "pytest"
  lint: "ruff check {path}"
  type_check: "mypy {path}"
paths:
  source: "app/"
  tests: "tests/"
conventions:
  test_file_pattern: "test_{name}.py"

# Go (no Docker)
name: go-local
runtime:
  exec_prefix: ""
commands:
  test: "go test ./..."
  lint: "golangci-lint run"
paths:
  source: "internal/"
  tests: "internal/"
conventions:
  test_file_pattern: "{name}_test.go"
```

</details>

---

## How It Works

### Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md                          # Entry point — refs to project.yml, stack.yml, models.yml
│   ├── project.yml                        # WHAT: identity, domain, invariants, critical flows
│   ├── stack.yml                          # HOW: runtime, commands, paths, conventions
│   ├── models.yml                         # Model routing: task complexity → haiku/sonnet/opus
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
│   │   ├── sync-schema/SKILL.md            #   Schema sync (auto + manual)
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
| `/sync-schema` | Sync `memory/schema.md` with model/migration files |
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

PHASE 2: Execution Loop
  For each task [ ] in project-state.md:
    Builder agent implements + tests
    PASS → mark [x], persist state
    FAIL → retry (max 2) → STOP on 3rd failure
  Every 3 tasks → /summarize-context

PHASE 3: Finalization
  Run validate (tests + build) → catches runtime errors
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
  Auto-label: enhancement, bug, or documentation

PHASE 2: Spec
  Planner agent (opus) produces structured spec + acceptance criteria
  Apply labels from analysis
  Post Comment 1 — Requirements (immutable)
  Post Comment 2 — Execution Plan (living, updated throughout)
  Write tasks to project-state.md

PHASE 3: Worktree Setup
  git fetch origin
  git worktree add WT_ROOT -b feat/ISSUE-SLUG origin/main
  Copy state to worktree

PHASE 4: Execution (inside the worktree — strict isolation)
  NEVER read/write to REPO_ROOT — worktree is the project root
  Builder agent (sonnet) implements + tests each task
  Commits per wave inside the worktree
  Update Comment 2 with progress after each wave

PHASE 5: Integration
  Run validate (tests + build) → catches runtime errors
  git push → gh pr create (haiku)
  Final update to Comment 2 with PR URL

PHASE 6: Cleanup
  Archive state (haiku)
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

## What to Edit Per Project

Only 4 files contain your project-specific data. Everything else is generic framework.

| File | What to put | When to edit |
|------|------------|--------------|
| `project.yml` | Name, domain, tenant config, invariants, critical flows, protected areas | When adopting the framework |
| `stack.yml` | Runtime, commands, paths, stack conventions | When adopting the framework |
| `models.yml` | Model routing: which Claude model (haiku/sonnet/opus) per task type | When adopting the framework or tuning costs |
| `memory/architecture.md` | System design, roles, patterns | At start and as architecture evolves |
| `memory/schema.md` | Auto-synced data model (configure `schema` in stack.yml) | Auto-updated by pipelines |

Agents, skills, and CLAUDE.md **are not edited** — they're generic and reference `{stack.*}` and `{project.*}`.

---

## Memory and Resilience

### Memory files

| File | Purpose | Written by |
|------|---------|------------|
| `architecture.md` | System design | Planner agent |
| `schema.md` | Data model (compact, token-efficient) | /sync-schema (auto at pipeline start) |
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

### Connect a database MCP

If your project uses a database, you can configure a [Model Context Protocol](https://modelcontextprotocol.io/) server so the planner agent can inspect the real schema instead of relying on documentation.

In `stack.yml`:

```yaml
database:
  type: "postgresql"              # postgresql, mysql, sqlite, mongodb
  schema_source: "schema.sql"     # Fallback file if no MCP available
  mcp: true                       # Set to true if DB MCP is configured
  read_only: true                 # MCP should NEVER write to the database
```

When `database.mcp: true`, the planner will use MCP tools to query the live schema. When `false` or absent, it falls back to reading the `schema_source` file.

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
