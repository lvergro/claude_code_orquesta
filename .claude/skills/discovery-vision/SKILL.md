---
name: discovery-vision
description: >
  Discovery phase 1 — Vision & Domain. Establishes the problem, audience, and
  domain vocabulary. Output: docs/glossary.md with entity definitions plus a
  short vision summary at the top.
user-invocable: true
---

# /discovery-vision

Phase 1. Foundation for every other phase — every later artifact references the entities defined here.

**Driver agent:** `planner`.
**Output file:** `docs/glossary.md`.
**Reads:** nothing (this is the root phase).

---

## modes

### greenfield (Q&A)
Three turns minimum:

1. **Problem & audience** — "What pain does this solve, for whom? One sentence each."
2. **Boundaries** — "What's NOT this product? Name 2-3 things people might confuse it with."
3. **Vocabulary** — "List the nouns that already appear when you describe it. Don't define them yet — just list."

Then propose `docs/glossary.md`:

```markdown
# Vision
<one-paragraph summary>

# Glossary

## <Entity>
**Definition:** <one-line>
**Synonyms / aliases:** <if any>
**Lifecycle:** <created when… deleted when…>
**Relationships:** <belongs to / has many …>
```

Iterate until "ok". Keep glossary tight — every term should pull weight in later phases.

### review
Audit the existing glossary:

1. **Completeness** — every entity has Definition + Lifecycle + Relationships.
2. **Consistency** — no entity referenced in `docs/use-cases/*` is missing here.
3. **Drift** (if `src/` exists) — every model in `src/models/` (or schema) maps to a glossary entry. Flag orphans both ways.

### ingest
Show entity list. Confirm or jump to review.

---

## persistence

Write `docs/glossary.md`. Update `.discovery-state.md`:

```
## phase_1_vision
status: complete
last_reviewed: <today>
entity_count: <N>
```

If glossary changes, mark phases 2, 3, 5 as `partial`.

---

## stop conditions

Standard (see `/discovery`).
