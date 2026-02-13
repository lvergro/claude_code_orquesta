# Orquesta for Antigravity

Multi-agent orchestration framework adapted for [Google Antigravity](https://antigravity.google) — the agentic IDE based on VS Code.

## What is this?

Orquesta provides structured workflows, persistent memory, and coordination patterns for agentic development. This version is adapted from the Claude Code original to work with Antigravity's native `.agent/` directory conventions.

## Quick Start

1. **Copy to your project:**
   ```bash
   cp -r antigravity/.agent /path/to/your/project/.agent
   cp antigravity/GEMINI.md /path/to/your/project/GEMINI.md
   ```

2. **Configure your project identity:**
   Edit `.agent/rules/project.md` — set your project name, domain entities, invariants.

3. **Configure your stack:**
   Edit `.agent/rules/stack.md` — set your runtime commands (test, lint, build, dev).

4. **Document your architecture:**
   Edit `.agent/memory/architecture.md` — describe your system design.

5. **Start working:**
   - `/feature` — End-to-end feature delivery (issue → PR)
   - `/develop` — Master pipeline for complex changes
   - `/quick` — Fast path for trivial fixes
   - `/research` — Technical investigation
   - `/audit` — Security audit
   - `/sync-schema` — Sync data model from source files
   - `/prepare-commit` — Validate and commit

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
