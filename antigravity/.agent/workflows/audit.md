---
description: Security audit of the codebase with auth, tenant, and input validation analysis
---

# /audit — Security Audit

## Scope

Input: directory path, module name, or blank for full codebase.

## Flow

1. Read `.agent/rules/project.md` → invariants and critical flows
2. Read `.agent/memory/architecture.md` → security patterns
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
