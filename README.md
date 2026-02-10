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
  validate: "npx vitest run && npm run build"  # tests + build (catches runtime errors)

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

Other stack examples:

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
  Post comment: "Session started"

PHASE 2: Spec
  Planner agent produces structured spec
  Post spec as comment on issue
  Write tasks to project-state.md

PHASE 3: Worktree Setup
  git fetch origin
  git worktree add WT_ROOT -b feat/ISSUE-SLUG origin/main
  Copy state to worktree

PHASE 4: Execution (inside the worktree — strict isolation)
  NEVER read/write to REPO_ROOT — worktree is the project root
  Builder agent implements + tests each task
  Commits per wave inside the worktree
  Post progress to issue

PHASE 5: Integration
  Run validate (tests + build) → catches runtime errors
  git push → gh pr create
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
