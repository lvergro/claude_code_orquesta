# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Development orchestration system for Claude Code.**

A file-based orchestration system that structures how Claude Code plans, implements, and delivers features — using subagent roles, persistent memory, and issue-driven workflows.

**One feature = one issue = one worktree = one branch = one PR.**

**[Leer en Español](README_ES.md)** | Also available for **[Antigravity (Gemini)](antigravity/)**

---

## How It Works

Three subagents with constrained tool access, dispatched automatically:

| Agent | Role | Model | Can do | Cannot do |
|-------|------|-------|--------|-----------|
| `planner` | Architect + Researcher | opus | Read, analyze, design, write to memory/ | Code, commits, Bash |
| `builder` | Programmer + QA | sonnet | Write code, tests, execute commands | Edit architecture, commits |
| `git` | Release Manager | haiku | Commits and push | Write code or edit files |

One main workflow (`/feature`) orchestrates them through a pipeline:

```
/feature #42  (or free-text description)

PHASE 0 → Schema sync + resume check
PHASE 1 → Intake (create/read GitHub issue, auto-label)
PHASE 2 → Spec (planner: scope, acceptance criteria, tasks in waves)
PHASE 3 → Worktree setup (isolated branch + directory)
PHASE 4 → Execution (builder: implement + test each task, commit per wave)
PHASE 5 → Integration (validate, push, create PR)
PHASE 6 → Cleanup (archive state)
```

Interrupted? Run `/feature #42` again — resumes from where it left off.

Parallel features? Multiple terminals, each with a different `/feature #N`. Each worktree is fully isolated.

---

## Structure

```
.claude/
├── CLAUDE.md                          # Entry point
├── project.yml                        # WHAT: domain, invariants, critical flows
├── stack.yml                          # HOW: runtime, commands, paths
├── models.yml                         # Model routing (haiku/sonnet/opus)
├── settings.local.json                # Tool permissions
│
├── agents/                            # Subagents (native dispatch)
│   ├── planner.md
│   ├── builder.md
│   └── git.md
│
├── skills/                            # Workflows
│   ├── feature/SKILL.md               #   /feature — main pipeline
│   ├── research/SKILL.md              #   /research — technical investigation
│   ├── audit/SKILL.md                 #   /audit — security audit
│   ├── sync-schema/SKILL.md           #   /sync-schema — data model sync
│   ├── prepare-commit/SKILL.md        #   /prepare-commit
│   ├── validate-invariants/SKILL.md   #   Safety checks (auto)
│   ├── summarize-context/SKILL.md     #   Context compression (auto)
│   ├── write-tests/SKILL.md           #   Test strategy (auto)
│   ├── analyze-architecture/SKILL.md  #   Drift detection (auto)
│   └── archive-state/SKILL.md         #   State lifecycle (auto)
│
└── memory/                            # Persistent state
    ├── architecture.md                #   System design (source of truth)
    ├── schema.md                      #   Data model (auto-synced)
    ├── project-state.md               #   Active tasks + progress
    ├── research.md                    #   Research log
    ├── decisions/                     #   Architecture decision records
    └── archive/                       #   Completed states
```

---

## Getting Started

### 1. Copy the framework

```bash
cp -r /path/to/framework/.claude/ ./.claude/
```

### 2. Let Claude configure your project

```bash
claude
```

```
Configure this project's .claude/ directory.
It's a [describe your project — e.g., "multi-tenant SaaS for restaurant management"].

Stack: [e.g., "Next.js 14 + Supabase + Prisma, running in Docker"]
Entities: [e.g., "organizations, users, restaurants, menus, orders"]
Multi-tenant: [yes/no — e.g., "yes, RLS with org_id column"]

Key invariants:
- [e.g., "All queries must filter by org_id"]
- [e.g., "Order totals recalculated server-side"]

Critical flows:
- [e.g., "Order: validate menu → check availability → create order → notify kitchen"]

Read project.yml, stack.yml, and memory/architecture.md, then fill them in.
```

Claude fills in `project.yml`, `stack.yml`, and `architecture.md` aligned to your domain.

### 3. Start building

```bash
/feature Add user registration with email verification
/feature #42                    # existing issue
/research Compare Redis vs Memcached
/audit src/auth
/sync-schema                    # force data model sync
```

---

## What to Edit Per Project

| File | What to put | When |
|------|------------|------|
| `project.yml` | Domain, invariants, critical flows | Setup |
| `stack.yml` | Runtime commands, paths, schema config | Setup |
| `models.yml` | Model routing (haiku/sonnet/opus) | Setup or cost tuning |
| `memory/architecture.md` | System design, roles, patterns | Setup + evolves |

Everything else is generic — agents, skills, and CLAUDE.md are not edited.

<details>
<summary>Manual configuration examples</summary>

**project.yml:**
```yaml
name: MySaaS
description: Inventory management platform
domain:
  language: en
  entities: [organization (tenant), user, warehouse, product, order]
tenant:
  enabled: true
  column: org_id
  isolation: rls
invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id.
    severity: critical
```

**stack.yml:**
```yaml
name: node-docker-prisma
runtime:
  exec_prefix: "docker compose exec api"
commands:
  test: "npx vitest run"
  lint: "npx eslint {path}"
  build: "npm run build"
schema:
  source: models
  paths: [prisma/schema.prisma]
```

</details>

---

## Extending

### Add an agent

```yaml
# .claude/agents/my-agent.md
---
description: When to invoke this agent.
allowed-tools: [Read, Grep, Bash]
disallowed-tools: [Write]
---
# My Agent
Role instructions here.
```

### Add a skill

```yaml
# .claude/skills/my-skill/SKILL.md
---
name: my-skill
description: What this skill does.
user-invocable: true
---
# /my-skill
1. Step one
2. Step two
```

### Database MCP

```yaml
# In stack.yml
database:
  type: "postgresql"
  mcp: true
  read_only: true
```

---

## Recommended Tools

**[Claude Code Templates](https://github.com/davila7/claude-code-templates)** by **davila7** — the Analytics Dashboard (`npx claude-code-templates --analytics`) visualizes agent activity and token usage.

---

## License

Free to use. Adapt it to your project.
