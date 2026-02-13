# Orquesta for Antigravity

**Development orchestration system for [Antigravity](https://antigravity.google).**

A file-based orchestration system that structures how the AI agent plans, implements, and delivers features — using persistent memory and issue-driven workflows. Adapted from the Claude Code original to work with Antigravity's native `.agent/` directory conventions.

**One feature = one issue = one worktree = one branch = one PR.**

**[Leer en Español](README.es.md)**

---

## How It Works

One main workflow (`/feature`) orchestrates the agent through a pipeline:

```
/feature #42  (or free-text description)

PHASE 0 → Schema sync + resume check
PHASE 1 → Intake (create/read GitHub issue, auto-label)
PHASE 2 → Spec (scope, acceptance criteria, tasks in waves)
PHASE 3 → Worktree setup (isolated branch + directory)
PHASE 4 → Execution (implement + test each task, commit per wave)
PHASE 5 → Integration (validate, push, create PR)
PHASE 6 → Cleanup (archive state)
```

Interrupted? Run `/feature #42` again — resumes from where it left off.

Parallel features? Multiple terminals, each with a different `/feature #N`. Each worktree is fully isolated.

---

## Structure

```
GEMINI.md                              ← Entry point (always loaded)
.agent/
  rules/                               ← Always loaded into context
    project.md                         ← Domain, invariants, critical flows
    stack.md                           ← Runtime commands and paths
    conventions.md                     ← Coding and git standards
  workflows/                           ← User-triggered with /
    feature.md                         ← /feature (issue → PR)
    research.md                        ← /research
    audit.md                           ← /audit
    prepare-commit.md                  ← /prepare-commit
  skills/                              ← Auto-activated by the agent
    validate-invariants/SKILL.md       ← Safety checks
    analyze-architecture/SKILL.md      ← Drift detection
    write-tests/SKILL.md              ← Test strategy
    summarize-context/SKILL.md        ← Context compression
    archive-state/SKILL.md            ← State lifecycle
    sync-schema/SKILL.md              ← Schema sync
  memory/                              ← Persistent state
    architecture.md                    ← System design (source of truth)
    schema.md                         ← Data model (auto-synced)
    project-state.md                   ← Active tasks + progress
    research.md                        ← Research log
    decisions/                         ← Architecture decision records
    archive/                           ← Completed states
```

---

## Getting Started

### 1. Copy to your project

```bash
cp -r antigravity/.agent /path/to/your/project/.agent
cp antigravity/GEMINI.md /path/to/your/project/GEMINI.md
```

### 2. Let the agent configure your project

```
Configure this project's .agent/ directory.
It's a [describe your project — e.g., "multi-tenant SaaS for restaurant management"].

Stack: [e.g., "Next.js 14 + Supabase + Prisma, running in Docker"]
Entities: [e.g., "organizations, users, restaurants, menus, orders"]
Multi-tenant: [yes/no — e.g., "yes, RLS with org_id column"]

Key invariants:
- [e.g., "All queries must filter by org_id"]
- [e.g., "Order totals recalculated server-side"]

Read rules/project.md, rules/stack.md, and memory/architecture.md, then fill them in.
```

### 3. Start building

```
/feature Add user registration with email verification
/feature #42
/research Compare Redis vs Memcached
/audit src/auth
/sync-schema
```

---

## What to Customize

| File | What to change | When |
|------|---------------|------|
| `rules/project.md` | Domain, invariants, critical flows | Setup |
| `rules/stack.md` | Runtime commands, paths, schema config | Setup |
| `memory/architecture.md` | System design, roles, patterns | Setup + evolves |

---

## Key Differences from Claude Code Version

| Aspect | Claude Code | Antigravity |
|--------|------------|-------------|
| Config dir | `.claude/` | `.agent/` |
| Entry point | `CLAUDE.md` | `GEMINI.md` |
| Project config | `project.yml` (YAML) | `rules/project.md` (Markdown) |
| Stack config | `stack.yml` (YAML) | `rules/stack.md` (Markdown) |
| Model routing | `models.yml` | Not needed (automatic) |
| Agent definitions | `agents/*.md` | Not needed (Agent Manager) |
| User pipelines | `skills/*/SKILL.md` | `workflows/*.md` |
| Auto capabilities | `skills/*/SKILL.md` | `skills/*/SKILL.md` |
