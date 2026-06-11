---
name: audit
description: >
  Security audit of the codebase. Performs deep analysis of auth flows,
  tenant isolation, input validation, and generates actionable reports.
user-invocable: true
---

# /audit — Security Audit


## scope
Input: directory path, module name, or blank for full codebase. Examples: `src/auth`, `payments`, `/audit`.
Audit: $ARGUMENTS (or full codebase if no arguments)

## flow
1. Read `.claude/project.yml` → invariants and critical_flows
2. Read `.claude/memory/architecture.md` → security patterns
3. **Generic checks — delegate when possible:** if the runtime ships a built-in
   `/security-review`, run it for the generic surface (injection, XSS, secrets,
   dependency issues) and fold its findings into the report instead of
   re-deriving them.
4. **Project-specific checks — this skill's real job:**
   - Tenant isolation violations (missing `{tenant.column}` filters, per project.yml)
   - Auth bypasses on the declared critical_flows (missing role checks)
   - Invariant violations (each `severity: critical` invariant gets an explicit pass)
   - RLS policy gaps (if `tenant.isolation: rls`)
5. Generate report

## output
- Summary in conversation
- Full report: `/docs/audits/[date]-audit-full.md`
- Action items: `/docs/audits/TODO.md`
