# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Development orchestration system for Claude Code.**

Orquesta turns a Claude Code session into a disciplined engineering team: an **architect** that designs, a **programmer** that implements, a **release manager** that commits, and a **QA validator** that tests — each with enforced permissions, shared persistent memory, and a fully traceable path from idea to merged PR.

**One feature = one issue = one worktree = one branch = one PR.**

**[Leer en Español](README_ES.md)**

---

## Table of contents

1. [Why Orquesta?](#why-orquesta)
2. [How it works — the concepts](#how-it-works--the-concepts)
3. [Implementation — install it in your project](#implementation--install-it-in-your-project)
4. [Getting started: new vs. existing project](#getting-started-new-vs-existing-project)
5. [Tutorial: from idea to PR](#tutorial-from-idea-to-pr)
6. [Discovery walkthrough](#discovery-walkthrough)
7. [Day-to-day commands](#day-to-day-commands)
8. [Structure reference](#structure-reference)
9. [Extending](#extending)
10. [FAQ](#faq)

---

## Why Orquesta?

Working on a real project with a bare LLM session has predictable failure modes. Orquesta exists to close each one:

| Without Orquesta | With Orquesta |
|---|---|
| Context evaporates when the chat compacts or the session ends | All state lives in **files** (`.claude/memory/`). A `SessionStart` hook re-injects the current focus, so every session starts knowing what was in progress |
| One model does everything — expensive where it doesn't need to be, unpredictable where it matters | **Role-based agents with the right model for each job**: the planner inherits your session's strongest model, Sonnet codes (the bulk), Haiku commits (cheap, mechanical) |
| The assistant can edit anything, anytime | **Enforced tool access**: the planner physically cannot run Bash, the git agent cannot edit files, and native `ask` permission rules force confirmation before touching gate-protected paths (migrations, auth, billing…) |
| Big, unreviewable changes with no trail | Every feature follows **issue → spec → waves of tasks → commit per wave → PR**, with two living comments on the issue documenting requirements and execution |
| Parallel work stomps on itself | Each feature runs in an **isolated git worktree** — main stays clean, features don't collide |
| "Where were we?" after every interruption | Every pipeline is **resumable**: re-run `/feature #42` and it continues from the persisted state, including blocked tasks and pending CI |
| Design lives in someone's head (or a stale wiki) | `/discovery` produces **canonical design docs** (requirements, use cases, NFRs, C4, ADRs) in `docs/` *before* code, and derives compact runtime artifacts from them |

And the meta-advantages:

- **Stack-agnostic.** Agents never hardcode commands — they read `stack.yml`. Switching from Node to Python to Dockerized-anything is a one-file change.
- **No runtime dependencies.** Plain files: markdown, YAML, bash, python3, and the `gh` CLI. No server, no database, no build step.
- **Your CI/CD stays.** Orquesta adds checks and process; it never replaces your pipeline.
- **Token-economic by design.** Agents load a ~30-line architecture summary, not your whole design tree. Full detail stays in `docs/` and is read on demand.

---

## How it works — the concepts

### Two stages: design, then build

```
                        ┌──────────────────────┐         ┌──────────────────────┐
   idea / brief  ─────► │  /discovery pipeline │ ──────► │   /feature pipeline  │ ─────► PR
                        │  (design artifacts)  │         │  (issue → code → PR) │
                        └──────────────────────┘         └──────────────────────┘
                          docs/  +  .claude/                code  +  tests
```

- **`/discovery`** (run once per project, re-run when the design evolves) interviews you in small conversational turns and produces design documents under `docs/`. Its final phase derives the compact runtime config in `.claude/`.
- **`/feature`** (run for every feature) takes an issue or a free-text description and drives it through spec → implementation → tests → PR, committing wave by wave.

You can skip `/discovery` and configure `.claude/` by hand — `/feature` works either way. Discovery is how you make the design *explicit and auditable* first.

### The four agents

Subagents are defined in `.claude/agents/*.md`. Their `model`, `tools` and `disallowedTools` frontmatter is **enforced by the Claude Code runtime** — these are hard permissions, not suggestions:

| Agent | Role | Model | Can do | Cannot do |
|-------|------|-------|--------|-----------|
| `planner` | Architect + Researcher | `inherit`* | Read, analyze, design, write to `memory/` and `docs/` | Bash, code, commits |
| `builder` | Programmer | `sonnet` | Write code, tests, run commands | Push, force-edit gate-protected areas |
| `git` | Release Manager | `haiku` | Commits and push | Edit/Write any file |
| `qa` | QA Validator | `sonnet` | Run tests, browser automation, write reports | Edit app source (writes limited to QA artifacts + tests — by rule) |

\* `inherit` uses your session's model — on Max plans you can pin it to `opus`; on Pro it rides your session's Sonnet, which is where your quota goes furthest.

Why this matters:

- **Quality:** the model that decides *what* to build is not distracted by syntax; the model that builds (Sonnet) receives a finished spec.
- **Cost:** the expensive model runs only during planning — and only if your plan includes it. Routine work (commits, labels) runs on Haiku.
- **Safety:** a compromised or confused builder still cannot push; the git agent still cannot rewrite your code.

### Persistent memory

Chat history is never the source of truth. State lives in files:

| File | What it holds | Who writes it |
|------|---------------|---------------|
| `.claude/memory/architecture.md` | ~30-line executive summary of the system design | `/discovery-intake` (full C4 stays in `docs/architecture/`) |
| `.claude/memory/project-state.md` | Active tasks, current focus, blockers | planner (plans), builder (progress) |
| `.claude/memory/requirements.md` | FR↔UC index, one line per requirement | `/discovery-intake` |
| `.claude/memory/schema.md` | Compact data-model snapshot | `/sync-schema` (auto-verified at `/feature` start) |
| `.claude/memory/research.md` | Research log (problem → options → recommendation) | `/research` |
| `docs/**` | Canonical design: glossary, FRs, NFRs, UCs, C4, ADRs | `/discovery` phases (with your approval) |

One source of truth per artifact — `.claude/memory/` never duplicates `docs/`, it summarizes it.

### Hooks and permission rules — enforcement the model can't skip

Hooks run as shell scripts on lifecycle events, outside the model's control:

- **`auto-format.sh`** (`PostToolUse` on Edit/Write) — runs the right formatter (prettier, ruff/black, gofmt, rustfmt, shfmt, rubocop) on every modified file. Skips silently if not installed.
- **`session-context.sh`** (`SessionStart`) — injects the active tasks and current focus from `project-state.md`, so a fresh session knows immediately what's in flight.

Protected paths use Claude Code's **native permission system** instead of a custom hook: `gate_protected_areas` in `project.yml` is the declarative source (pattern + reason), compiled by `/discovery-intake` into `permissions.ask` rules in `settings.json` (`Edit(migrations/**)`, `Write(migrations/**)`…). The runtime itself prompts before any edit — no script in the path, nothing to fail open. CI checks parity between the two files.

### Path-scoped rules

`.claude/rules/*.md` load **only when matching files are touched** — zero context cost otherwise. Shipped rules: `migrations.md` (expand-then-contract, no sync backfills, rollback paths) and `tests.md` (test behavior not internals, mock at boundaries).

---

## Implementation — install it in your project

### Requirements

| Tool | Why |
|------|-----|
| [Claude Code](https://claude.com/claude-code) CLI | The runtime everything orchestrates |
| `git` | Worktrees, branches, commits |
| `gh` CLI, authenticated (`gh auth login`) | Issues, PRs, labels — all GitHub communication |
| `python3` | Used by the hooks (JSON parsing) |
| *(optional)* `prettier`, `ruff`, `gofmt`… | Auto-formatting hook picks up whatever is installed |

### Step 1 — Copy the framework

```bash
cd your-project
cp -r /path/to/claude-code-orquesta/.claude ./.claude
echo ".claude/settings.local.json" >> .gitignore
```

Commit `.claude/` to git — it's team-shared configuration. Only `settings.local.json` (personal permission grants) stays out.

### Step 2 — Tell it WHAT your project is (`project.yml`)

`.claude/project.yml` defines the project identity. Either let `/discovery` fill it for you (recommended), or edit by hand:

```yaml
name: MySaaS
description: Inventory management platform

domain:
  language: en
  entities: [organization (tenant), user, warehouse, product, order]

# Multi-tenancy: if enabled, the builder enforces the tenant column in every query
tenant:
  enabled: true
  column: org_id
  isolation: rls

# Rules that must NEVER break. Agents stop and report if one is violated.
invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id. No cross-tenant data leaks.
    severity: critical

# Paths where a native ask rule forces a confirmation before any edit
gate_protected_areas:
  - pattern: "migrations/"
    reason: Schema changes require careful planning
  - pattern: "auth/**"
    reason: Authentication logic
```

What each section buys you:

- **`entities`** — shared vocabulary; the planner uses these names in specs.
- **`tenant`** — if enabled, "filter by tenant" becomes an enforced rule for the builder, not a hope.
- **`invariants`** — checked by the planner during specs and by `/validate-invariants`; a critical violation stops the pipeline.
- **`gate_protected_areas`** — the only mechanism standing between an over-eager edit and your migrations folder. Declared here (pattern + reason), enforced as native `permissions.ask` rules in `settings.json` — `/discovery-intake` compiles them, or add the matching `Edit(pattern)`/`Write(pattern)` rules by hand.

### Step 3 — Tell it HOW to run things (`stack.yml`)

`.claude/stack.yml` is the only place commands live. Agents reference `{stack.commands.test}` etc. — never hardcoded:

```yaml
name: node-docker-prisma

runtime:
  exec_prefix: "docker compose exec api"   # prefixed to EVERY runtime command ("" if none)

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

conventions:
  test_file_pattern: "{name}.test.ts"

# Optional: keep memory/schema.md in sync with your real data model
schema:
  source: models
  paths: [prisma/schema.prisma]
```

The `schema` block enables auto-verification: every `/feature` run checks whether the schema snapshot is stale and re-syncs before planning.

### Step 4 — Optional integrations

**Issue tracker (hybrid model).** Design stays in `docs/`, state lives in your tracker:

```yaml
# stack.yml
tracker:
  type: linear        # linear | github | none
```

With a tracker configured, `/discovery-intake` mirrors every approved functional requirement as a parent issue, and `/feature FR-01` creates the implementation issue under it. `linear` uses the Linear MCP server; `github` uses the `gh` CLI directly.

**Database MCP.** Let the planner inspect the real schema instead of trusting docs:

```yaml
# stack.yml
database:
  type: "postgresql"
  mcp: true
  read_only: true
```

### Step 5 — Verify

Open `claude` in the repo and check that:

1. `/discovery`, `/feature`, `/qa-test` appear in the skills list (type `/`).
2. Editing a file under `migrations/` triggers the gate confirmation.
3. `cat .claude/memory/project-state.md` shows the idle template.

You're installed.

---

## Getting started: new vs. existing project

### A. New project (greenfield)

```bash
mkdir my-saas && cd my-saas
git init
cp -r /path/to/claude-code-orquesta/.claude ./.claude
echo ".claude/settings.local.json" >> .gitignore
claude
```

Then:

```
> /discovery
```

`/discovery` walks you through 7 phases (vision → requirements → use cases → NFRs → C4 → ADRs → intake), one conversational turn at a time. The final phase seeds `project.yml` and `memory/architecture.md` so `/feature` has a real source of truth.

When intake finishes, the planner suggests your first feature — typically the scaffold:

```
> /feature Bootstrap the project — Next.js + Supabase + Prisma scaffold
```

### B. Existing project (brownfield)

Same install, different first command. The goal is to teach the framework what already exists, not regenerate it.

**B.1 — You already have design docs** (Notion, Confluence, markdown): drop them into `docs/` matching the [structure](#structure-reference), then:

```
> /discovery review --deep
```

The planner audits each artifact (completeness, internal consistency, drift against the actual code) and walks you through findings one at a time. When clean, `/discovery-intake` seeds `.claude/`.

**B.2 — No design docs yet:**

```
> /discovery
```

For an existing codebase the planner infers answers from the code (entities from models, containers from top-level dirs, dependencies from `package.json`) and asks you to confirm — producing docs that match reality before they reach `.claude/`.

**Brownfield safety notes:**

- **Discovery never edits `src/`.** Only `docs/` and (after intake) `.claude/`.
- **Pick a low-risk first feature** to validate the workflow end to end.
- **Tighten `gate_protected_areas`** around anything you don't want auto-edited (auth, billing, infra).
- **Existing CI/CD stays untouched.**

---

## Tutorial: from idea to PR

This is what actually happens when you run a feature. Say you want CSV export on an orders list:

```
> /feature Add CSV export to the orders list
```

**Phase 0 — Resume check.** Verifies `gh auth`, checks whether `schema.md` is stale (re-syncs if so), and looks for an existing worktree for this feature. Finding one means a previous run was interrupted — it resumes instead of starting over.

**Phase 1 — Intake.** Creates GitHub issue `#57 "Add CSV export to the orders list"` and labels it (`enhancement`). If you had passed `#42` or an issue URL, it reads the existing issue instead. If you passed `FR-03`, it pulls that requirement's full block from `docs/requirements/functional.md` as built-in acceptance criteria.

**Phase 2 — Spec. The only approval gate in the pipeline.** The planner reads `architecture.md`, the relevant ADRs and your invariants, and produces:

```
Scope: Add an "Export CSV" action to the orders list that streams the
current filtered view as a CSV download.

Acceptance Criteria:
- GET /api/orders/export honors the same filters as the list view
- Export respects org_id isolation (invariant: Tenant Isolation)
- 10k-row export completes < 5s

Tasks:
  Wave 1 — Backend: endpoint, CSV serializer, filter reuse
  Wave 2 — UI: export button, download handling, loading state
  Wave 3 — Tests: serializer unit tests, endpoint integration test

Files: src/api/orders/export.ts, src/components/OrdersToolbar.tsx, ...
Test strategy: ...

Proceed with implementation? (yes/no)
```

You say `yes` (or `no` — nothing has been created yet beyond the issue). On yes, two comments are posted to the issue: **Requirements** (immutable) and **Execution Plan** (a living checklist, updated by ID after every wave).

**Phase 3 — Worktree.** Creates an isolated checkout at `../.worktrees/feat/57-add-csv-export-to-the-orders-list` on branch `feat/57-…`, branched off fresh `origin/main`. Your main checkout is untouched from here on.

**Phase 4 — Execution.** The builder (Sonnet) implements task by task: write → test → mark done. After **every wave**: commit (memory state excluded), fetch + rebase onto main if it moved, and update the Execution comment:

```
✅ 1 Add GET /api/orders/export endpoint
✅ 2 Reuse list filters in export query
✅ 3 Stream CSV serializer
→ commit: feat(57-add-csv-export): wave 1 — backend export endpoint
```

If a task fails 3 times, a blocker comment is posted to the issue and the pipeline stops with state saved. The next `/feature #57` asks "Blocker: … Resolved?" and continues.

**Phase 5 — Integration.** Full validation (tests + build), a code review pass scoped to the branch diff (critical findings get posted to the issue), push, and a **draft PR**:

```
Closes #57
## Summary / ## Changes / ## Test plan / ## Code Review
```

Then it watches CI (10-minute cap). Green → the PR flips to **ready for review** automatically. Red → a failure comment is posted and the PR stays draft; re-running `/feature #57` re-checks.

**Phase 6 — Cleanup.** State is archived to `.claude/memory/archive/`, the final status lands on the Execution comment, and you get:

```
✅ Feature #57 delivered. PR: https://github.com/you/repo/pull/58 — merge when ready.
```

Merging is **yours** — Orquesta never merges. After merging, reclaim disk:

```
> /cleanup-worktrees
```

It lists worktrees whose PRs merged/closed, asks once, and removes them (never `--force`).

**Parallel features?** Open another terminal, run `/feature #61`. Each worktree is fully isolated.

---

## Discovery walkthrough

### Scenario 1 — Brand-new project

```
> /discovery
```

1. Bootstraps `docs/` and `docs/.discovery-state.md`.
2. Detects every phase is greenfield; starts at **Phase 1 (Vision)**.
3. The planner asks 1–3 focused questions per turn — never dumps a full draft on you.
4. You answer; it proposes a draft; you redirect; it iterates.
5. On your explicit `ok`, the file is written and you advance.
6. Repeat through phases 2–6. Phase 7 shows the proposed `.claude/` diff and writes only on approval.

A full discovery from zero typically takes 2–4 sessions. `pause` at any time; `/discovery resume` continues.

### Scenario 2 — Existing docs need review

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

One issue at a time; each resolution updates the doc and the state file.

### Scenario 3 — Work a single phase

Each phase is a standalone skill:

```
> /discovery-functional        # only requirements
> /discovery-architecture      # only C4
> /discovery-decisions         # only ADRs
```

Phases declare dependencies — editing FRs (phase 2) flags phases 3 and 5 as `partial` so you remember to re-review them.

### Rules the planner always follows

- **No silent generation.** Every doc write is shown as a diff first; written only on explicit `ok`.
- **Small turns.** 1–3 questions, never a 30-question questionnaire.
- **Evidence-anchored review.** Every issue cites a file or line.
- **Discovery never edits `src/`.**

---

## Day-to-day commands

```bash
# Stage 1 — design
/discovery                                                # full pipeline (auto-mode)
/discovery review --deep                                  # re-audit all phases against code
/discovery <phase>                                        # jump to a specific phase
/discovery resume                                         # resume interrupted phase

# Stage 2 — build
/feature Add user registration with email verification    # free-text → creates issue
/feature #42                                              # existing issue
/feature FR-03                                            # implement a functional requirement
/qa-test                                                  # full QA pass (unit + E2E browser)
/research Compare Redis vs Memcached                      # investigation → research.md
/audit src/auth                                           # security audit on a path
/sync-schema                                              # force data-model sync
/prepare-commit                                           # validate readiness + draft commit msg
/cleanup-worktrees                                        # remove worktrees whose PRs merged
```

---

## Structure reference

```
.claude/
├── CLAUDE.md                           # Entry point — imports project.yml + stack.yml
├── project.yml                         # WHAT: domain, invariants, gate-protected areas
├── stack.yml                           # HOW: runtime, commands, paths, schema source
│
├── settings.json                       # Team-shared: permissions (deny/ask), hooks
├── settings.local.json                 # Personal/local: extra allows (gitignored)
│
├── hooks/                              # Lifecycle hooks (run as shell scripts)
│   ├── auto-format.sh                  #   PostToolUse Edit|Write — formats the modified file
│   └── session-context.sh              #   SessionStart — injects project-state Current Focus
│
├── rules/                              # Path-scoped rules (load only when matching files touched)
│   ├── migrations.md                   #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                        #   paths: **/*.test.*, tests/**
│
├── agents/                             # Subagents — model + tools enforced via frontmatter
│   ├── planner.md                      #   model: inherit — designs, never codes
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
│   ├── discovery-intake/SKILL.md       #     phase 7: docs/ → .claude/ (+ tracker sync)
│   │  # ── Build (stage 2) ──
│   ├── feature/SKILL.md                #   /feature — main build pipeline
│   ├── qa-test/SKILL.md                #   /qa-test — E2E QA validation
│   ├── research/SKILL.md               #   /research — technical investigation
│   ├── audit/SKILL.md                  #   /audit — security audit
│   ├── sync-schema/SKILL.md            #   /sync-schema — data model sync
│   ├── prepare-commit/SKILL.md         #   /prepare-commit
│   ├── validate-invariants/SKILL.md    #   Safety checks
│   ├── write-tests/SKILL.md            #   Test strategy
│   ├── analyze-architecture/SKILL.md   #   Drift detection
│   ├── archive-state/SKILL.md          #   State lifecycle
│   └── cleanup-worktrees/SKILL.md      #   /cleanup-worktrees — remove merged worktrees
│
└── memory/                             # Compact runtime state — derived from docs/, not duplicated
    ├── architecture.md                 #   Executive summary, ~30 lines (full C4 lives in docs/architecture/)
    ├── requirements.md                 #   FR↔UC index (one line per FR)
    ├── schema.md                       #   Data model (auto-synced from stack.yml)
    ├── project-state.md                #   Active tasks + Current Focus + Blockers
    ├── research.md                     #   Research log
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

### What to edit per project

| File | What to put | When |
|------|------------|------|
| `project.yml` | Domain, invariants, critical flows, gate-protected areas | Setup (or auto-populated by `/discovery-intake`) |
| `stack.yml` | Runtime commands, paths, schema config, tracker | Setup |
| `memory/architecture.md` | System design summary | Setup (or auto-populated by `/discovery-intake`) |
| `docs/**` | Vision, requirements, use cases, C4, ADRs | Continuously, via `/discovery` |

Everything else is generic — agents, skills, hooks, rules and CLAUDE.md are not edited per project.

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

## FAQ

**Do I have to run `/discovery` before `/feature`?**
No. `/feature` works with a hand-written `project.yml` + `architecture.md`. Discovery is the recommended way to make the design explicit, traceable and auditable — especially for teams.

**Does it merge my PRs?**
Never. Orquesta delivers a reviewed, CI-green PR and stops. Merging — and the judgment it implies — is yours.

**What does it cost to run?**
The planner inherits your session model (pin Opus only if your plan includes it); the bulk of work runs on Sonnet and the mechanical steps on Haiku. The memory model (compact summaries, path-scoped rules, on-demand docs) keeps per-turn context small. On a Pro account this default is the cheapest configuration that preserves the process.

**Does it work without GitHub?**
The `/feature` pipeline relies on `gh` for issues and PRs. Discovery, memory, hooks and all other skills work without it.

**Can I protect more areas after installing?**
Yes — add the pattern to `gate_protected_areas` in `project.yml` and the matching `Edit(pattern)`/`Write(pattern)` rules to `permissions.ask` in `settings.json` (or re-run `/discovery-intake`, which compiles them for you). CI verifies both files stay in sync.

**What happens if my session dies mid-feature?**
Nothing is lost. State is on disk and in the issue comments. `/feature #N` resumes from the exact phase, task and blocker where it stopped.

---

## Recommended tools

**[Claude Code Templates](https://github.com/davila7/claude-code-templates)** by **davila7** — the Analytics Dashboard (`npx claude-code-templates --analytics`) visualizes agent activity and token usage.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
