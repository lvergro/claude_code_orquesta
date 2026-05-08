---
name: discovery-architecture
description: >
  Discovery phase 5 — Architecture (C4 model). Produces context, container, and
  optionally component diagrams as markdown + PlantUML/Mermaid. Greenfield, review,
  or ingest. Foundation for memory/architecture.md after intake.
user-invocable: true
---

# /discovery-architecture

Phase 5. The C4 model in three levels. Component-level (level 3) is optional and worth doing only for the most critical containers.

**Driver agent:** `planner`.
**Output files:**
- `docs/architecture/c4-context.md` (level 1 — system in its environment)
- `docs/architecture/c4-container.md` (level 2 — high-level building blocks)
- `docs/architecture/c4-component.md` (level 3 — only critical containers)

**Reads:** `docs/glossary.md`, `docs/requirements/functional.md`, `docs/requirements/non-functional.md`, `docs/use-cases/*`.
**Depends on:** phase 1, 2, 3, 4.

---

## modes

### greenfield (Q&A)

#### Level 1 — Context
Ask:
1. "Who interacts with the system? (users, roles, external systems)"
2. "What does the system depend on externally? (payment gateway, email, third-party APIs)"

Propose `c4-context.md` with a Mermaid diagram + actor/system list.

#### Level 2 — Container
Ask:
1. "What runs as a separate process or deploys independently? (web app, API, worker, DB, cache)"
2. "How do they communicate? (HTTP, queue, shared DB)"
3. "Tech choice per container? (be specific — Postgres 15, Next.js 14, Redis 7)"

Propose `c4-container.md` with diagram + container table:

```markdown
| Container | Tech | Purpose | Talks to |
|-----------|------|---------|----------|
| Web App | Next.js 14 | UI + SSR | API |
| API | Node 20 + Fastify | Business logic | DB, Cache, Queue |
| DB | Postgres 15 | Persistence | — |
| Worker | Node 20 | Async jobs | DB, Queue |
```

#### Level 3 — Component (optional)
Only run if user opts in. For each picked container:
1. "What modules / packages exist inside?"
2. "Which is the entry point? Which are leaf utilities?"

Defer to `/feature` for finer-grained design — this level should set conventions, not pre-design every module.

### review
1. **Completeness** — every UC critical flow can be traced through containers.
2. **Consistency** — every container has a tech, every external system has a defined boundary, no orphan arrows.
3. **Drift** — for each container in `c4-container.md`:
   - Tech matches `package.json` / `Dockerfile` / `pyproject.toml`
   - Communication matches code (e.g. if "API → Worker via queue", grep for queue client usage)
   - Containers in code with no diagram entry → flag as undocumented

### ingest
Show the C4 levels present + container summary table. Confirm or review.

---

## diagrams

Use Mermaid for portability:

```markdown
\`\`\`mermaid
C4Container
  Person(user, "End user")
  System_Boundary(s, "MySaaS") {
    Container(web, "Web App", "Next.js 14")
    Container(api, "API", "Node + Fastify")
    ContainerDb(db, "DB", "Postgres 15")
  }
  Rel(user, web, "uses", "HTTPS")
  Rel(web, api, "calls", "REST")
  Rel(api, db, "reads/writes")
\`\`\`
```

PlantUML acceptable if the user prefers; the planner asks once at phase start.

---

## persistence

Write the c4-* files. Update `.discovery-state.md`:

```
## phase_5_architecture
status: complete
levels: [context, container]   # component if generated
container_count: <N>
```

If containers change, mark phase 6 (decisions) as `partial` and recommend re-review (tech choices in ADRs may be invalidated).

---

## stop conditions

Standard.
