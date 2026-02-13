# Orquesta for Antigravity

Multi-agent orchestration framework adapted for [Google Antigravity](https://antigravity.google) — the agentic IDE based on VS Code.

## What is this?

Orquesta provides structured workflows, persistent memory, and coordination patterns for agentic development. This version is adapted from the Claude Code original to work with Antigravity's native `.agent/` directory conventions.

## Quick Start

### Step 1: Copy to your project

```bash
cp -r antigravity/.agent /path/to/your/project/.agent
cp antigravity/GEMINI.md /path/to/your/project/GEMINI.md
```

### Step 2: Let the agent configure your project

Instead of editing files manually, **ask the agent to do it for you**. Open your project in Antigravity and describe your domain:

```
Configure this project's .agent/ directory for my project.
It's a [describe your project — e.g., "multi-tenant SaaS for restaurant management"].

Stack: [your stack — e.g., "Next.js 14 + Supabase + Prisma, running in Docker"]
Entities: [your domain entities — e.g., "organizations, users, restaurants, menus, orders, reservations"]
Multi-tenant: [yes/no, and how — e.g., "yes, RLS with org_id column"]

Key invariants:
- [e.g., "All queries must filter by org_id — no cross-tenant data leaks"]
- [e.g., "Order totals must be recalculated server-side — never trust client amounts"]

Critical flows:
- [e.g., "Order placement: validate menu → check availability → create order → notify kitchen"]

Read rules/project.md, rules/stack.md, and memory/architecture.md, then fill them in aligned to my domain.
```

The agent will:
1. Read the template files (`rules/project.md`, `rules/stack.md`, `memory/architecture.md`)
2. Fill in `project.md` with your entities, invariants, critical flows, and protected areas
3. Fill in `stack.md` with your runtime commands, paths, and conventions
4. Fill in `architecture.md` with your system design, data model, roles, and patterns
5. Optionally configure schema sync if you have ORM models or migrations

> **Tip:** The more specific you are about your domain rules and constraints, the better the agent will enforce them during development. Invariants are the guardrails — the agent will stop and report if any is violated.

### Step 3: Verify the configuration

After the agent configures the files, review them:

```
Read rules/project.md and rules/stack.md and tell me what you configured
```

Make sure:
- `project.md` has your entities, invariants, and critical flows
- `stack.md` has your actual commands (test, lint, build, dev)
- `architecture.md` reflects your real system design
- If you use ORM models, `stack.md` has the Schema section configured

### Step 4: Start your first feature

With the framework configured, you're ready to build. Use `/feature` for the full pipeline or `/develop` for linear work:

**Option A — `/feature` (recommended for issue-driven work):**

```
/feature Add user registration with email verification
```

Or reference an existing GitHub issue:

```
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

```
/develop Implement notification system
```

**Option C — `/quick` (for trivial changes):**

```
/quick Fix the login button text
```

**Other useful commands:**

```
/research Compare Redis vs Memcached for caching    # Investigate before deciding
/sync-schema                                         # Force-sync data model
/audit src/auth                                      # Security audit
/prepare-commit                                      # Validate and commit
```

## Structure

```
GEMINI.md                              ← Top-level instructions (always loaded)
.agent/
  rules/                               ← Always loaded into context
    project.md                         ← Project identity, domain, invariants
    stack.md                           ← Runtime commands and paths
    conventions.md                     ← Coding and git standards
  workflows/                           ← User-triggered with /
    feature.md                         ← /feature (issue → PR)
    develop.md                         ← /develop (E2E pipeline)
    quick.md                           ← /quick (fast path)
    research.md                        ← /research
    audit.md                           ← /audit
    prepare-commit.md                  ← /prepare-commit
  skills/                              ← Auto-activated by the agent
    validate-invariants/SKILL.md       ← Safety checks
    analyze-architecture/SKILL.md      ← Drift detection
    write-tests/SKILL.md              ← Test strategy
    summarize-context/SKILL.md        ← Context compression
    archive-state/SKILL.md            ← State lifecycle
    sync-schema/SKILL.md              ← Schema sync (auto + manual)
    parallel/SKILL.md                 ← Multi-session coordination
  memory/                              ← Persistent state (custom directory)
    architecture.md                    ← System design (source of truth)
    project-state.md                   ← Runtime state tracking
    research.md                        ← Investigation log
    locks.md                           ← Multi-session locks
    decisions/                         ← Architecture Decision Records
    archive/                           ← Completed state archives
```

## What to Customize

| File | What to change |
|------|---------------|
| `GEMINI.md` | Usually no changes needed |
| `rules/project.md` | Project name, entities, invariants, critical flows |
| `rules/stack.md` | Runtime commands, paths, framework metadata |
| `rules/conventions.md` | Coding style, test patterns (if different from defaults) |
| `memory/architecture.md` | Your system's actual architecture |

## Key Differences from Claude Code Version

| Aspect | Claude Code (orquesta) | Antigravity |
|--------|----------------------|-------------|
| Config dir | `.claude/` | `.agent/` |
| Top-level | `CLAUDE.md` | `GEMINI.md` |
| Project config | `project.yml` (YAML) | `rules/project.md` (Markdown) |
| Stack config | `stack.yml` (YAML) | `rules/stack.md` (Markdown) |
| Model routing | `models.yml` | Not needed (automatic) |
| Agent definitions | `agents/*.md` | Not needed (Agent Manager) |
| User pipelines | `skills/*/SKILL.md` (user-invocable) | `workflows/*.md` |
| Auto capabilities | `skills/*/SKILL.md` (auto) | `skills/*/SKILL.md` |

## How It Works Inside Antigravity

Once you open your project in Antigravity, everything loads automatically:

| Type | How Antigravity handles it |
|------|---------------------------|
| `GEMINI.md` | Injected into every prompt (like system instructions) |
| `.agent/rules/*.md` | Always loaded into context — the agent sees them on every interaction |
| `.agent/workflows/*.md` | Appear when you type `/` in the chat — user-triggered pipelines |
| `.agent/skills/*/SKILL.md` | Auto-activated — the agent loads them when semantically relevant to the task |
| `.agent/memory/` | Custom directory — not native to Antigravity, but rules reference it so the agent reads/writes there |

### Using Workflows

Type `/` in the Antigravity chat to see available workflows:

```
/feature agregar dashboard de estadísticas    → issue → spec → worktree → PR
/develop refactorizar sistema de roles        → plan → execute in loop → commit
/quick fix typo en login page                 → implement → test → commit
/research comparar date-fns vs dayjs          → investigate → write to research.md
/audit src/auth                               → security analysis → report
/prepare-commit                               → validate tests + invariants → commit message
```

### How Skills Auto-Activate

You don't invoke skills directly. The agent activates them when needed:

- Before a commit → **validate-invariants** checks safety rules
- During `/develop` every 3 tasks → **summarize-context** compresses state
- When `/develop` finishes → **archive-state** resets project-state.md
- When you open 2+ terminals with `/parallel` → **parallel** coordinates via locks
- When a workflow needs tests → **write-tests** defines strategy
- When checking architecture → **analyze-architecture** detects drift

### Memory System

Memory is not native to Antigravity — it's a convention enforced by the rules:

- `memory/architecture.md` — read before any code, source of truth for design
- `memory/schema.md` — compact data model, auto-synced at pipeline start
- `memory/project-state.md` — updated during development, enables resume across sessions
- `memory/research.md` — investigation log
- `memory/decisions/DEC-*.md` — architecture decision records
- `memory/locks.md` — multi-session coordination for `/parallel`

The agent reads and updates these files as part of workflow execution.

## Conventions

- **Rules** are always loaded — keep them concise
- **Workflows** are user-triggered — they contain the full pipeline logic
- **Skills** are auto-activated — the agent loads them when semantically relevant
- **Memory** is not a native Antigravity feature — it's a custom directory referenced by rules
