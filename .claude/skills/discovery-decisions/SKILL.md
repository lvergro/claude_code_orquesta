---
name: discovery-decisions
description: >
  Discovery phase 6 — Architectural Decision Records (ADRs). Captures
  technology and design choices with context, options considered, decision,
  and consequences. Output: docs/decisions/ADR-NNN-*.md.
user-invocable: true
---

# /discovery-decisions

Phase 6. ADRs document why the architecture is the way it is. They survive long after team turnover.

**Driver agent:** `planner`. May invoke `/research` for option comparison.
**Output:** `docs/decisions/ADR-NNN-<slug>.md` (one per decision).
**Reads:** `docs/architecture/c4-*.md`.
**Depends on:** phase 5.

---

## modes

### greenfield (Q&A)

The planner extracts decision points from `c4-container.md` and asks one by one:

> "You picked Postgres 15 as the primary DB. Walk me through: what alternatives did you consider, and why this one?"

For each, propose:

```markdown
---
id: ADR-001
title: Use Postgres 15 as primary database
status: accepted          # proposed | accepted | superseded
date: 2026-05-08
deciders: [team]
---

## Context
<situation forcing the decision>

## Decision
<what was chosen, in one paragraph>

## Options considered
| Option | Pros | Cons |
|--------|------|------|
| Postgres 15 | mature, RLS, JSONB | vertical scaling first |
| MongoDB | flexible schema | weaker consistency |
| DynamoDB | managed, scalable | vendor lock |

## Consequences
- Positive: <…>
- Negative: <…>
- Neutral: <…>

## Related
- Containers: API, Worker
- NFRs: NFR-PERF-01
- Supersedes: <ADR-id if applicable>
```

If user is unsure of options, planner offers to invoke `/research` for that specific decision.

### review
1. **Completeness** — every ADR has Context + Decision + Options + Consequences.
2. **Consistency** — `status: accepted` ADRs aren't contradicted by later `accepted` ADRs unless explicit `Supersedes:`.
3. **Drift** — every ADR's tech choice still matches `c4-container.md` and the actual repo.

### ingest
List ADRs by status. Confirm or review.

---

## persistence

One file per ADR. IDs are stable — never renumber, even if superseded. Filename: `ADR-<NNN>-<slug>.md`.

Update `.discovery-state.md`:
```
## phase_6_decisions
status: complete
adr_count: <N>
adrs_accepted: <N>
adrs_superseded: <N>
```

---

## stop conditions

Standard.
