# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Development orchestration system for Claude Code.**

A file-based orchestration system that structures how Claude Code plans, implements, and delivers features — using subagent roles, persistent memory, and issue-driven workflows.

**One feature = one issue = one worktree = one branch = one PR.**

**[Leer en Español](README_ES.md)** | Also available for **[Antigravity (Gemini)](antigravity/)**

---

## How It Works

Four subagents with **enforced** tool access (via `tools` / `disallowedTools` frontmatter), dispatched automatically:

| Agent | Role | Model | Can do | Cannot do |
|-------|------|-------|--------|-----------|
| `planner` | Architect + Researcher | `opus` | Read, analyze, design, write to memory/ | Bash, code, commits |
| `builder` | Programmer | `sonnet` | Write code, tests, run commands | Push, force-edit gate-protected areas |
| `git` | Release Manager | `haiku` | Commits and push | Edit/Write any file |
| `qa` | QA Validator | `sonnet` | Run tests, browser automation, write reports | (no source-edit restriction yet — by convention) |

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
├── CLAUDE.md                          # Entry point — imports project.yml + stack.yml
├── project.yml                        # WHAT: domain, invariants, gate-protected areas
├── stack.yml                          # HOW: runtime, commands, paths, schema source
│
├── settings.json                      # Team-shared: permissions (deny/ask), hooks
├── settings.local.json                # Personal/local: extra allows (gitignored if you want)
│
├── hooks/                             # Lifecycle hooks (run as shell scripts)
│   ├── gate-check.sh                  #   PreToolUse Edit|Write — blocks gate_protected_areas
│   └── session-context.sh             #   SessionStart — injects project-state Current Focus
│
├── rules/                             # Path-scoped rules (load only when matching files touched)
│   ├── migrations.md                  #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                       #   paths: **/*.test.*, tests/**
│
├── agents/                            # Subagents — model + tools enforced via frontmatter
│   ├── planner.md                     #   model: opus  — designs, never codes
│   ├── builder.md                     #   model: sonnet — codes silently
│   ├── git.md                         #   model: haiku — commits + pushes
│   └── qa.md                          #   model: sonnet — runs tests + browser E2E
│
├── skills/                            # Workflows (slash commands)
│   ├── feature/SKILL.md               #   /feature — main pipeline
│   ├── qa-test/SKILL.md               #   /qa-test — E2E QA validation
│   ├── research/SKILL.md              #   /research — technical investigation
│   ├── audit/SKILL.md                 #   /audit — security audit
│   ├── sync-schema/SKILL.md           #   /sync-schema — data model sync
│   ├── prepare-commit/SKILL.md        #   /prepare-commit
│   ├── validate-invariants/SKILL.md   #   Safety checks
│   ├── summarize-context/SKILL.md     #   Context compression
│   ├── write-tests/SKILL.md           #   Test strategy
│   ├── analyze-architecture/SKILL.md  #   Drift detection
│   └── archive-state/SKILL.md         #   State lifecycle
│
└── memory/                            # Persistent state — sources of truth across sessions
    ├── architecture.md                #   System design
    ├── schema.md                      #   Data model (auto-synced from stack.yml)
    ├── project-state.md               #   Active tasks + Current Focus + Blockers
    ├── research.md                    #   Research log
    ├── decisions/                     #   ADRs (DEC-*.md)
    └── archive/                       #   Completed states
```

---

## Getting Started

Two paths: **A. New project** (greenfield) or **B. Existing project** (brownfield).

### A. New project from scratch

For a project that doesn't exist yet, or one with no production code.

```bash
# 1. Create the project + git repo
mkdir my-saas && cd my-saas
git init

# 2. Drop in the framework
cp -r /path/to/claude-code-orquesta/.claude ./.claude

# 3. (Optional) ignore your local-only settings
echo ".claude/settings.local.json" >> .gitignore

# 4. Open Claude Code
claude
```

Then ask Claude to set up the framework with your domain and stack:

```
Configure this project's .claude/ directory for a new project.

Domain: [e.g., "Multi-tenant SaaS for restaurant inventory"]
Stack: [e.g., "Next.js 14 + Supabase + Prisma, runs in Docker"]
Entities: [e.g., "organization (tenant), user, restaurant, menu, order"]
Multi-tenant: [yes — RLS with org_id column / no]

Key invariants:
- [e.g., "All DB queries filter by org_id"]
- [e.g., "Order totals are server-recalculated"]

Critical flows:
- [e.g., "Order: validate menu → check stock → charge → notify kitchen"]

Gate-protected areas (extra confirmation before edits):
- migrations/
- [e.g., src/auth/]

Update project.yml, stack.yml, and memory/architecture.md from this brief.
Leave skills, agents, hooks, and CLAUDE.md untouched.
```

Then start your first feature:

```bash
/feature Bootstrap the project — Next.js + Supabase + Prisma scaffold
```

The `planner` agent will produce a spec, the `builder` will execute task-by-task,
and the `git` agent will commit each wave.

---

### B. Existing project (brownfield)

For a project that already has code, tests, and a production history.
The goal is to teach the framework what's already there, not regenerate it.

```bash
# 1. From the project root
cp -r /path/to/claude-code-orquesta/.claude ./.claude

# 2. Append .claude/settings.local.json to .gitignore (if you want personal allows out of the repo)
echo ".claude/settings.local.json" >> .gitignore

# 3. Open Claude Code in the repo
claude
```

Ask Claude to discover and document what already exists, instead of inventing it:

```
This is an existing project. Configure .claude/ by reading the codebase, not by guessing.

Steps:
1. Run /init to scan the repo and capture build/test/lint commands.
2. Fill stack.yml from package.json / pyproject.toml / Dockerfile.
   - Detect exec_prefix (Docker? bare metal?)
   - Detect test, lint, type_check, build, dev commands
   - Detect schema source (Prisma? migrations? raw SQL?) and set schema.paths
3. Fill project.yml:
   - Infer domain entities from src/models/ or db schema
   - Infer multi-tenant strategy from existing queries (look for tenant_id / org_id columns)
   - Add gate_protected_areas for migrations/, auth/, payment/, and any directory with sensitive code
4. Fill memory/architecture.md from the actual layered structure of src/.
   Reference real files, not aspirational ones.
5. Run /sync-schema to seed memory/schema.md from real models.
6. Pause for review. Show me the diff before any further work.
```

Important notes for brownfield:
- **Don't let Claude rewrite your code** during setup. Setup only edits `.claude/`.
- **Pick one feature first**, ideally a low-risk one, to validate the workflow:
  ```bash
  /feature Refactor user auth tokens to use the new session table
  ```
- **Tighten `gate_protected_areas`** for any area you don't want auto-edited (auth, billing, infra config). The `gate-check.sh` hook will force a confirmation prompt.
- **Existing CI/CD stays.** The framework only adds checks — it doesn't replace your pipeline.

---

### Common commands

```bash
/feature Add user registration with email verification   # free-text → creates issue
/feature #42                                             # existing issue
/qa-test                                                 # full QA pass (unit + E2E)
/research Compare Redis vs Memcached
/audit src/auth                                          # security audit on a path
/sync-schema                                             # force data model sync
/prepare-commit                                          # validate readiness + draft commit msg
```

---

## What to Edit Per Project

| File | What to put | When |
|------|------------|------|
| `project.yml` | Domain, invariants, critical flows | Setup |
| `stack.yml` | Runtime commands, paths, schema config | Setup |
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
name: my-agent
description: When to invoke this agent.
model: sonnet              # opus | sonnet | haiku
tools: [Read, Grep, Bash]  # allowlist
disallowedTools: [Write]   # denylist (camelCase — required by Claude Code)
---
# My Agent
Role instructions here.
```

> Frontmatter fields follow Claude Code's official subagent spec.
> `name` is required; `model` and `tools` are enforced by the runtime.

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

MIT License. See [LICENSE](LICENSE) for details.
