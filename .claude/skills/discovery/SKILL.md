---
name: discovery
description: >
  Iterative, conversational design discovery that produces docs/ artifacts
  (requirements, use cases, C4, ADRs) before /feature. Auto-detects greenfield,
  review, or ingest mode based on existing docs/. Each phase persists to disk
  only on explicit approval. Run /discovery to start, /discovery <phase> to
  jump in, /discovery resume to continue.
user-invocable: true
---

# /discovery

Conversational design pipeline. Produces `docs/` upstream of `.claude/` so the framework consumes a stable, human-reviewable source of truth.

**Driver agent:** `planner` (opus) — designs and asks. Never executes code.
**Output:** files under `docs/` + state in `docs/.discovery-state.md`.
**Final phase only** writes to `.claude/` via `/discovery-intake`.

---

## phase 0: bootstrap & mode detection

1. Read `.claude/stack.yml` → `docs.root` (default: `docs/`). Resolve `DOCS_ROOT`.

2. If `DOCS_ROOT` doesn't exist, create the skeleton:
   ```
   docs/
   ├── glossary.md                         # empty stub
   ├── requirements/
   │   ├── functional.md
   │   └── non-functional.md
   ├── use-cases/                          # one UC-*.md per use case
   ├── architecture/
   │   ├── c4-context.md
   │   ├── c4-container.md
   │   └── c4-component.md
   ├── decisions/                          # ADR-*.md
   └── .discovery-state.md
   ```

3. **Mode detection per phase** — for each of the 7 phases, classify:
   - `greenfield` — file missing or only template stub
   - `partial` → enters **review** mode — file exists with content but flagged issues, or user requested review
   - `complete` → enters **ingest** mode — file exists, last reviewed within freshness window, no open issues

4. Read `.discovery-state.md` if present. Show summary:
   ```
   Discovery State (last updated: 2026-05-08)

   PHASE 1 — Vision & Domain          ✅ complete
   PHASE 2 — Functional Reqs          🔄 review (3 issues open)
   PHASE 3 — Use Cases                ⚪ greenfield
   PHASE 4 — Non-Functional Reqs      ⚪ greenfield
   PHASE 5 — Architecture (C4)        ⚪ greenfield
   PHASE 6 — Key Decisions (ADRs)     ⚪ greenfield
   PHASE 7 — Intake → .claude/        ⏸ blocked (waiting on phases 2-6)
   ```

5. Parse input:
   - `/discovery` → start at first non-complete phase
   - `/discovery <phase-name>` → jump to that phase (e.g. `/discovery functional`)
   - `/discovery resume` → resume in_progress phase from state file
   - `/discovery review --deep` → re-audit all completed phases against current code
   - `/discovery <phase> --mode greenfield|review|ingest` → force mode

---

## phases

Each phase is a separate skill. Invoke and wait for completion before advancing.

| # | Skill | Output | Depends on |
|---|-------|--------|------------|
| 1 | `/discovery-vision` | `docs/glossary.md` + vision summary | — |
| 2 | `/discovery-functional` | `docs/requirements/functional.md` | 1 |
| 3 | `/discovery-use-cases` | `docs/use-cases/UC-*.md` | 2 |
| 4 | `/discovery-nfr` | `docs/requirements/non-functional.md` | 1 |
| 5 | `/discovery-architecture` | `docs/architecture/c4-*.md` | 3, 4 |
| 6 | `/discovery-decisions` | `docs/decisions/ADR-*.md` | 5 |
| 7 | `/discovery-intake` | populates `.claude/` from `docs/` | 1-6 |

**Dependency rule:** if a downstream phase is `complete` and an upstream phase is updated, mark downstream as `partial` and recommend re-review (don't auto-rerun).

---

## conversational loop (shared by every phase)

Each phase skill implements this same shape:

1. **Detect mode** (greenfield | review | ingest).
2. **Greenfield:** open Q&A. Ask 1-3 focused questions. Wait for user. Never dump a generated draft on the first turn.
3. **Review:** run audit (3 lenses below). Present findings as a numbered list. Ask which to discuss first.
4. **Ingest:** show summary. Ask `confirm | review | edit`.
5. **Iterate:** propose draft → user redirects → propose v2 → repeat. Stop when user says explicit ok.
6. **Persist:** write to `docs/<file>.md` only on explicit approval. Update `.discovery-state.md`.
7. **Next:** suggest the next phase or pause.

### audit lenses (review mode)

For each artifact, the planner checks:

1. **Completeness** — required sections present? (defined per phase skill)
2. **Internal consistency** — contradictions across `docs/`?
3. **Drift with reality** — only if code exists in repo:
   - Glossary entities ↔ `src/models/` or schema
   - C4 Containers ↔ actual top-level dirs/services
   - NFRs ↔ real configs (timeouts, indexes, rate limits)
   - ADRs ↔ `package.json` / `requirements.txt` / Dockerfile

Default scope: only files referenced by the doc. `--deep` widens to repo-wide scan.

---

## state file format (`docs/.discovery-state.md`)

```markdown
# Discovery State
last_updated: 2026-05-08

## phase_1_vision
mode: greenfield
status: complete
last_reviewed: 2026-05-08
issues_open: 0
issues_resolved: 4

## phase_2_functional
mode: review
status: in_progress
last_reviewed: 2026-05-08
issues_open: 3
issues_resolved: 2
notes: "Pending discussion on FR-12 scope"

## phase_3_use_cases
status: pending
```

Status values: `pending` | `in_progress` | `complete` | `blocked`.

---

## behavior rules (planner)

- **No silent generation.** Never write a doc file without showing the diff and getting "ok".
- **Small turns.** Ask 1-3 questions max per turn. Don't ambush with a 30-question questionnaire.
- **Forward propagation.** When a phase changes, list which downstream phases need re-review.
- **No code changes.** Discovery never edits `src/`. Only `docs/` and `.discovery-state.md`.
- **Anchor to evidence.** In review mode, every issue must cite a file/line. No vague "this seems incomplete".

---

## stop conditions

- User says `pause` / `stop` / `enough` → save state, exit cleanly.
- All 7 phases `complete` → suggest `/feature` to start building.
- Hard error (missing `stack.yml`, broken state file) → `❌ Error: [details]`. Don't attempt recovery.
