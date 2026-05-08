---
name: discovery-use-cases
description: >
  Discovery phase 3 — Use Cases. One file per UC under docs/use-cases/.
  Each UC traces to ≥1 functional requirement. Greenfield, review, or ingest mode.
user-invocable: true
---

# /discovery-use-cases

Phase 3. Each functional requirement gets ≥1 use case that walks through actor → trigger → main flow → alternate flows → outcome.

**Driver agent:** `planner`.
**Output:** `docs/use-cases/UC-NN-<slug>.md` (one per UC).
**Reads:** `docs/glossary.md`, `docs/requirements/functional.md`.
**Depends on:** phase 1, 2.

---

## modes

### greenfield
For each FR (or batch the user picks), the planner walks through:

1. **Happy path** — "Walk me through the most common version, step by step."
2. **Pre/post conditions** — "What must be true before? After?"
3. **Alternate flows** — "What can go wrong at each step? Authentication failure? Stock empty? Timeout?"

Then proposes a UC file:

```markdown
---
id: UC-01
title: Register user with email verification
related_fr: [FR-01, FR-03]
actor: end user
priority: must-have
---

## Preconditions
- User has a valid email
- User is not yet registered

## Main flow
1. User submits email + password
2. System creates account with status=pending
3. System sends verification email
4. User clicks verification link within 24h
5. System activates account

## Alternate flows
- 4a. Link expired → user can request a new one (UC-02)
- 2a. Email already in use → return error, suggest password reset

## Postconditions
- Account row in `users` table with status=active
- Verification event logged
```

### review
Audits per UC:
1. **Completeness** — has Main flow + Pre/Postconditions + ≥1 Alternate flow.
2. **Consistency** — `related_fr` IDs exist; entities match glossary.
3. **Drift** — for UCs marked `priority: must-have`, check that endpoints/handlers exist in `src/`.

### ingest
List all UCs with their FR mapping. Confirm or jump to review.

---

## persistence

One file per UC. Filename: `UC-<NN>-<kebab-slug>.md`.

Update `.discovery-state.md`:
```
## phase_3_use_cases
status: complete
uc_count: <N>
orphan_frs: []         # FRs without UCs
```

If new UCs are added, mark phase 5 (architecture) as `partial`.

---

## stop conditions

Standard.
