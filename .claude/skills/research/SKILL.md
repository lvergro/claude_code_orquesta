---
name: research
description: >
  Technical investigation of tools, libraries, patterns, or alternatives.
  Produces structured findings in research.md with options table and recommendation.
user-invocable: true
---

# /research — Technical Investigation

Read `.claude/models.yml` for model routing.

## Flow
1. Use **planner agent** (model: opus, research mode)
   - Define scope, key questions, comparison criteria
   - Investigate (docs, code, web)
   - Write findings to `.claude/memory/research.md`
2. Output: structured summary with recommendation

## research.md Format
```markdown
## [YYYY-MM-DD] — [Topic]
**Problem**: ...
| Option | Pros | Cons |
|--------|------|------|
| A      | ...  | ...  |
**Recommendation**: ...
```
