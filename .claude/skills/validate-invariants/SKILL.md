---
name: validate-invariants
description: >
  Verifies critical safety rules that must never be broken.
  Acts as a mandatory safety check before important actions.
user-invocable: true
---

# /validate-invariants — Safety Check

## Source of Rules
Read `.claude/project.yml` → `invariants` section.

## Checks

### Security
- No hardcoded API keys, tokens, or passwords in source code
- No PII or sensitive data printed in logs or console

### Architecture
- Code respects layer boundaries defined in architecture.md
- New files are in correct directories per conventions

### Business Logic
- Changes don't include unrequested features (gold plating)
- Domain rules are respected

### Tenant Isolation
- All DB queries filter by tenant column (from project.yml)
- No cross-tenant joins without validation

## Result
- **PASS**: "✅ Invariants validated: system is stable and secure."
- **FAIL**: "❌ CRITICAL VIOLATION: [description]". Reject the change.
