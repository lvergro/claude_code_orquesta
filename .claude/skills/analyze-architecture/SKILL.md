---
name: analyze-architecture
description: >
  Audits architectural consistency by comparing current code structure
  against architecture.md. Detects drift, violations, and undocumented changes.
user-invocable: true
---

# /analyze-architecture — Drift Detection

## Context
1. Read `.claude/memory/architecture.md` — the source of truth
2. Explore current directory structure and file patterns

## Analysis
1. Are there undocumented directories or modules?
2. Are files in forbidden locations (e.g., business logic in view layer)?
3. Are naming conventions respected?
4. Do database queries match documented patterns?
5. Are new features properly declared in architecture.md?

## Output
- If consistent: "✅ Architecture consistent."
- If violations found: List each violation with suggested fix.

## Constraints
- Do NOT modify any files during analysis. Report only.
