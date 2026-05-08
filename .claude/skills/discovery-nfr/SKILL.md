---
name: discovery-nfr
description: >
  Discovery phase 4 — Non-Functional Requirements (latency, throughput,
  security, availability, compliance). Each NFR must be measurable.
  Output: docs/requirements/non-functional.md.
user-invocable: true
---

# /discovery-nfr

Phase 4. NFRs become invariants in `project.yml` after intake — so every NFR must be **measurable** or it gets rejected.

**Driver agent:** `planner`.
**Output file:** `docs/requirements/non-functional.md`.
**Reads:** `docs/glossary.md`, `docs/requirements/functional.md`.
**Depends on:** phase 1.

---

## modes

### greenfield (Q&A)
Walk through 6 categories. Skip categories that don't apply (state explicitly):

1. **Performance** — p95/p99 latency targets per critical FR. Throughput. Concurrent users.
2. **Availability** — uptime target. RTO/RPO if applicable. Degraded modes.
3. **Security** — auth model. Tenant isolation strategy. Data encryption at rest/in transit. Audit logging.
4. **Compliance** — GDPR, PCI, HIPAA, SOC2 — only if the user's domain demands it.
5. **Scalability** — expected growth in 12 months. What scales horizontally vs. vertically.
6. **Observability** — what MUST be queryable in production (logs, metrics, traces).

For each NFR, demand a **measurable form**:

```markdown
## NFR-PERF-01 — API read latency
**Category:** Performance
**Metric:** p99 latency on GET endpoints
**Target:** ≤ 200ms
**Measured by:** prometheus histogram `http_request_duration_seconds`
**Applies to:** all endpoints under /api/v1/*
**Rationale:** SLA commitment with enterprise tier
```

If the user can't provide a metric or target, the planner pushes back: "We can't enforce 'fast' — give me a number or skip this." Mark as `⚠️ NEEDS METRIC` if user wants to defer.

### review
1. **Completeness** — every NFR has Metric + Target + Measured by.
2. **Consistency** — no contradictions (e.g. p99 < 100ms but uptime 99% — implies many slow tail incidents).
3. **Drift** — for each NFR, check if the corresponding observability is in place:
   - Performance NFR → metric exists in `prometheus.yml` / `monitoring/`
   - Security NFR → middleware / RLS policies / encryption configs in repo
   - Audit NFR → logging calls in code paths

### ingest
List NFRs grouped by category. Confirm or review.

---

## persistence

Write `docs/requirements/non-functional.md`. Update `.discovery-state.md`.

NFRs flagged `⚠️ NEEDS METRIC` block intake (phase 7) until resolved.

---

## stop conditions

Standard.
