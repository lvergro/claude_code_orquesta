---
name: validate-invariants
description: Verifies critical safety rules from project.md that must never be broken. Activates automatically before commits, deployments, and other important actions.
---

# Validate Invariants — Safety Check

## Source of Rules
Read `.agent/rules/project.md` → invariants section.

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
- All DB queries filter by tenant column (from project.md)
- No cross-tenant joins without validation

## Result
- **PASS**: `Done: Invariants validated — system is stable and secure.`
- **FAIL**: `Error: CRITICAL VIOLATION — [description]`. Reject the change.
