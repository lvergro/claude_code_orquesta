---
paths:
  - "migrations/**"
  - "**/migrations/**"
  - "prisma/schema.prisma"
  - "supabase/migrations/**"
---

# Migrations Rules

Schema changes are gate-protected (`project.yml` → `gate_protected_areas`).

## Before editing
1. Verify the migration is on the planner's spec — never invent schema changes mid-build.
2. Check `.claude/memory/schema.md` for current state. If stale, run `/sync-schema`.
3. Confirm rollback path exists (down migration or revert plan).

## Conventions
- One concern per migration. No mixing schema + data backfills unless atomic is required.
- Backfills on large tables: do NOT run synchronously in the migration. Use a separate job.
- Never DROP columns in the same migration that adds replacements — split into deploy → backfill → drop.
- New NOT NULL columns: add nullable → backfill → set NOT NULL in a follow-up.

## After editing
- Run the migration locally before commit.
- Update `.claude/memory/schema.md` (or run `/sync-schema`).
- Note the migration in the PR description, not just the diff.
