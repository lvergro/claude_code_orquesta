# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Development orchestration system for Claude Code.**

A file-based orchestration system that structures how Claude Code **designs, plans, implements, and delivers** features — using subagent roles, persistent memory, and issue-driven workflows.

**One feature = one issue = one worktree = one branch = one PR.**

**[Leer en Español](README_ES.md)** | Also available for **[Antigravity (Gemini)](antigravity/)**

---

## How It Works

Four subagents with **enforced** tool access (via `tools` / `disallowedTools` frontmatter), dispatched automatically:

| Agent | Role | Model | Can do | Cannot do |
|-------|------|-------|--------|-----------|
| `planner` | Architect + Researcher | `opus` | Read, analyze, design, write to memory/ and docs/ | Bash, code, commits |
| `builder` | Programmer | `sonnet` | Write code, tests, run commands | Push, force-edit gate-protected areas |
| `git` | Release Manager | `haiku` | Commits and push | Edit/Write any file |
| `qa` | QA Validator | `sonnet` | Run tests, browser automation, write reports | (no source-edit restriction yet — by convention) |

---

## Two-stage workflow: design, then build

Orquesta covers the full path from *idea* to *shipped feature* in two stages:

```
                        ┌──────────────────────┐         ┌──────────────────────┐
   idea / brief  ─────► │  /discovery pipeline │ ──────► │   /feature pipeline  │ ─────► PR
                        │  (design artifacts)  │         │  (issue → code → PR) │
                        └──────────────────────┘         └──────────────────────┘
                          docs/  +  .claude/                code  +  tests
```

### Stage 1 — `/discovery` (design)

A conversational pipeline driven by the `planner` that produces design artifacts under `docs/` and seeds `.claude/` with them. Run it once at the start of a project, then re-run individual phases whenever the design evolves.

| # | Phase | Output |
|---|-------|--------|
| 1 | `/discovery-vision` | `docs/glossary.md` + vision summary |
| 2 | `/discovery-functional` | `docs/requirements/functional.md` |
| 3 | `/discovery-use-cases` | `docs/use-cases/UC-*.md` |
| 4 | `/discovery-nfr` | `docs/requirements/non-functional.md` |
| 5 | `/discovery-architecture` | `docs/architecture/c4-*.md` (Context, Container, Component) |
| 6 | `/discovery-decisions` | `docs/decisions/ADR-*.md` |
| 7 | `/discovery-intake` | populates `.claude/project.yml` + `memory/architecture.md` + `memory/decisions/` from `docs/` |

Each phase auto-detects mode based on the existing `docs/`:

- **greenfield** — no docs yet → conversational Q&A drafts the first version.
- **review** — docs exist but flagged for issues → audit (completeness / internal consistency / drift with code) → iterate.
- **ingest** — docs complete and fresh → confirm and advance.

The deep walkthrough (with example sessions for each scenario) is in [Discovery walkthrough](#discovery-walkthrough) below.

### Stage 2 — `/feature` (build)

Once `.claude/` is seeded, every feature follows a single pipeline:

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
├── CLAUDE.md                           # Entry point — imports project.yml + stack.yml
├── project.yml                         # WHAT: domain, invariants, gate-protected areas
├── stack.yml                           # HOW: runtime, commands, paths, schema source
│
├── settings.json                       # Team-shared: permissions (deny/ask), hooks
├── settings.local.json                 # Personal/local: extra allows (gitignored if you want)
│
├── hooks/                              # Lifecycle hooks (run as shell scripts)
│   ├── gate-check.sh                   #   PreToolUse Edit|Write — blocks gate_protected_areas
│   └── session-context.sh              #   SessionStart — injects project-state Current Focus
│
├── rules/                              # Path-scoped rules (load only when matching files touched)
│   ├── migrations.md                   #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                        #   paths: **/*.test.*, tests/**
│
├── agents/                             # Subagents — model + tools enforced via frontmatter
│   ├── planner.md                      #   model: opus  — designs, never codes
│   ├── builder.md                      #   model: sonnet — codes silently
│   ├── git.md                          #   model: haiku — commits + pushes
│   └── qa.md                           #   model: sonnet — runs tests + browser E2E
│
├── skills/                             # Workflows (slash commands)
│   │  # ── Discovery (stage 1 — design) ──
│   ├── discovery/SKILL.md              #   /discovery — orchestrator (mode detection + state)
│   ├── discovery-vision/SKILL.md       #     phase 1: glossary + vision
│   ├── discovery-functional/SKILL.md   #     phase 2: functional requirements
│   ├── discovery-use-cases/SKILL.md    #     phase 3: use cases
│   ├── discovery-nfr/SKILL.md          #     phase 4: non-functional requirements
│   ├── discovery-architecture/SKILL.md #     phase 5: C4 architecture
│   ├── discovery-decisions/SKILL.md    #     phase 6: ADRs
│   ├── discovery-intake/SKILL.md       #     phase 7: docs/ → .claude/
│   │  # ── Build (stage 2) ──
│   ├── feature/SKILL.md                #   /feature — main build pipeline
│   ├── qa-test/SKILL.md                #   /qa-test — E2E QA validation
│   ├── research/SKILL.md               #   /research — technical investigation
│   ├── audit/SKILL.md                  #   /audit — security audit
│   ├── sync-schema/SKILL.md            #   /sync-schema — data model sync
│   ├── prepare-commit/SKILL.md         #   /prepare-commit
│   ├── validate-invariants/SKILL.md    #   Safety checks
│   ├── summarize-context/SKILL.md      #   Context compression
│   ├── write-tests/SKILL.md            #   Test strategy
│   ├── analyze-architecture/SKILL.md   #   Drift detection
│   └── archive-state/SKILL.md          #   State lifecycle
│
└── memory/                             # Persistent state — sources of truth across sessions
    ├── architecture.md                 #   System design (populated by /discovery-intake)
    ├── schema.md                       #   Data model (auto-synced from stack.yml)
    ├── project-state.md                #   Active tasks + Current Focus + Blockers
    ├── research.md                     #   Research log
    ├── decisions/                      #   ADRs as DEC-*.md (mirrored from docs/decisions/)
    └── archive/                        #   Completed states
```

The `/discovery` pipeline also creates a `docs/` tree at the repository root:

```
docs/
├── glossary.md                         # Domain entities + vision summary
├── requirements/
│   ├── functional.md                   # FR list
│   └── non-functional.md               # NFR list (each NFR must be measurable)
├── use-cases/                          # UC-NN-*.md (one per use case)
├── architecture/                       # c4-context.md, c4-container.md, c4-component.md
├── decisions/                          # ADR-NNN-*.md
└── .discovery-state.md                 # Per-phase status, mode, and open audit issues
```

---

## Getting Started

Two paths: **A. New project** (greenfield) or **B. Existing project** (brownfield). Both rely on `/discovery` as the recommended first command — it builds (or audits) the design artifacts that `.claude/` consumes.

### A. New project from scratch

For a project that does not exist yet, or one with no production code.

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

Then in Claude Code:

```
> /discovery
```

`/discovery` walks you through 7 phases (vision → requirements → use cases → NFRs → C4 → ADRs → intake), one conversational turn at a time. The final phase seeds `.claude/project.yml` and `memory/architecture.md` so `/feature` has a real source of truth to work from.

When the intake finishes, the planner suggests your first feature — typically the project scaffold:

```bash
/feature Bootstrap the project — Next.js + Supabase + Prisma scaffold
```

The `planner` produces a spec, the `builder` executes task-by-task, and the `git` agent commits each wave.

See [Discovery walkthrough → Scenario 1](#scenario-1--brand-new-project) for a step-by-step example.

---

### B. Existing project (brownfield)

For a project that already has code, tests, and a production history. The goal is to teach the framework what already exists, not regenerate it.

```bash
# 1. From the project root
cp -r /path/to/claude-code-orquesta/.claude ./.claude

# 2. Append local settings to .gitignore (optional)
echo ".claude/settings.local.json" >> .gitignore

# 3. Open Claude Code in the repo
claude
```

Two sub-paths depending on what design documentation already exists:

**B.1 — You already have design docs** (in Notion, Confluence, markdown). Drop them into `docs/` matching the convention shown in the structure above, then run:

```
> /discovery review --deep
```

The planner audits each artifact (completeness, internal consistency, drift with the actual code) and walks you through the issues one at a time. When everything is clean, `/discovery-intake` seeds `.claude/`.

**B.2 — You do not have design docs yet.** Run `/discovery` and answer based on what the codebase already does:

```
> /discovery
```

In greenfield mode the planner asks open-ended questions; for an existing project, it can also infer answers from the code (entities from `src/models/`, containers from top-level dirs, dependencies from `package.json`) and ask you to confirm. This produces docs that match reality before they get into `.claude/`.

See [Discovery walkthrough → Scenario 2](#scenario-2--existing-docs-need-review).

**Important notes for brownfield:**
- **Discovery never edits `src/`.** Only `docs/` and (after intake) `.claude/`.
- **Pick a low-risk first feature** to validate the workflow:
  ```bash
  /feature Refactor user auth tokens to use the new session table
  ```
- **Tighten `gate_protected_areas`** for any area you do not want auto-edited (auth, billing, infra config). The `gate-check.sh` hook will force a confirmation prompt.
- **Existing CI/CD stays.** The framework only adds checks; it does not replace your pipeline.

---

## Discovery walkthrough

### Scenario 1 — Brand new project

After running steps 1–4 of [Getting Started A](#a-new-project-from-scratch):

```
> /discovery
```

What happens:

1. The skill bootstraps `docs/` and `docs/.discovery-state.md`.
2. Detects every phase is greenfield. Starts at **phase 1 (Vision)**.
3. The planner asks 1–3 focused questions per turn — never dumps a full draft on you.
4. You answer; the planner proposes a draft; you redirect; the planner iterates.
5. When you say `ok`, the file is written and you advance to phase 2.
6. Repeat through phases 2–6.
7. Phase 7 (`/discovery-intake`) shows the proposed diff for `.claude/` and writes only on your approval.
8. After intake, the planner suggests `/feature Bootstrap project scaffold per the C4 plan`.

A full discovery from zero typically takes 2–4 sessions. You can pause at any time:

```
> pause
```

State is saved. Resume with `/discovery resume`.

### Scenario 2 — Existing docs need review

If you already wrote requirements, use cases, C4, or ADRs (in any format), copy them into `docs/` matching the convention in [Structure](#structure), then:

```
> /discovery review --deep
```

The planner audits each artifact through three lenses (completeness, internal consistency, drift with code) and presents findings:

```
PHASE 5 — Architecture (Review)
✅ c4-context.md — no issues
⚠️ c4-container.md — 2 issues:
   - Container "PaymentService" not found in src/, deprecated?
   - Missing "NotificationWorker" (seen in src/workers/notify.ts)
❌ c4-component.md — missing, recommended for src/api/

Discuss in order, or pick one (1/2/3)?
```

You discuss one issue at a time. Each resolved issue updates the doc and the state file. When all phases are clean, run `/discovery-intake` to seed `.claude/`.

### Scenario 3 — Work on a single phase

You do not have to run the whole pipeline. Each phase is a standalone skill:

```
> /discovery-functional        # only requirements
> /discovery-architecture      # only C4
> /discovery-decisions         # only ADRs
```

Useful when you already have a partial setup and just want to evolve one piece. Phases declare their dependencies — if you edit FRs (phase 2), phases 3 and 5 are flagged as `partial` so you remember to re-review them later.

### Behavior rules the planner follows

- **No silent generation.** Every doc write is shown as a diff first; only written on explicit `ok`.
- **Small turns.** 1–3 questions per turn, never a 30-question questionnaire.
- **Evidence-anchored review.** Every issue cites a file or line, not vague hand-waving.
- **Discovery never edits `src/`.** Only `docs/` and `.discovery-state.md` until intake.

---

## Common commands

```bash
# Stage 1 — design
/discovery                                                # full pipeline (auto-mode)
/discovery review --deep                                  # re-audit all phases against code
/discovery <phase>                                        # jump to a specific phase
/discovery resume                                         # resume interrupted phase

# Stage 2 — build
/feature Add user registration with email verification    # free-text → creates issue
/feature #42                                              # existing issue
/qa-test                                                  # full QA pass (unit + E2E)
/research Compare Redis vs Memcached
/audit src/auth                                           # security audit on a path
/sync-schema                                              # force data model sync
/prepare-commit                                           # validate readiness + draft commit msg
```

---

## What to Edit Per Project

| File | What to put | When |
|------|------------|------|
| `project.yml` | Domain, invariants, critical flows, gate-protected areas | Setup (or auto-populated by `/discovery-intake`) |
| `stack.yml` | Runtime commands, paths, schema config, optional `docs:` overrides | Setup |
| `memory/architecture.md` | System design, roles, patterns | Setup (or auto-populated by `/discovery-intake`) |
| `docs/**` | Vision, requirements, use cases, C4, ADRs | Continuously, via `/discovery` |

Everything else is generic — agents, skills, hooks, rules, and CLAUDE.md are not edited per project.

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
