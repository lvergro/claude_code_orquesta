---
name: audit
description: >
  Security audit of the codebase. Performs deep analysis of auth flows,
  tenant isolation, input validation, and generates actionable reports.
user-invocable: true
---

# /audit — Security Audit

## Scope
Audit: $ARGUMENTS (or full codebase if no arguments)

## Flow
1. Read `.claude/project.yml` → invariants and critical_flows
2. Read `.claude/memory/architecture.md` → security patterns
3. Analyze codebase for:
   - Tenant isolation violations (missing tenant column filters)
   - Auth bypasses (missing role checks)
   - Input validation gaps (SQL injection, XSS)
   - Hardcoded secrets or credentials
   - RLS policy gaps
4. Generate report

## Output
- Summary in conversation
- Full report: `/docs/audits/[date]-audit-full.md`
- Action items: `/docs/audits/TODO.md`
