---
name: validate-invariants
description: >
  Verifies critical safety rules that must never be broken.
  Acts as a mandatory safety check before important actions.
user-invocable: true
---

# /validate-invariants — Safety Check

Read `.claude/models.yml` for model routing. This skill uses model: sonnet.

## source of rules
Read `.claude/project.yml` → `invariants` section.

## checks

### security
- No hardcoded API keys, tokens, or passwords in source code
- No PII or sensitive data printed in logs or console

### architecture
- Code respects layer boundaries defined in architecture.md
- New files are in correct directories per conventions

### business logic
- Changes don't include unrequested features (gold plating)
- Domain rules are respected

### tenant isolation
- All DB queries filter by tenant column (from project.yml)
- No cross-tenant joins without validation

## result
- **PASS**: "✅ Invariants validated: system is stable and secure."
- **FAIL**: "❌ CRITICAL VIOLATION: [description]". Reject the change.
