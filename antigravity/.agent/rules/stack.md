# Stack Profile

Change THIS file to adapt the entire workflow to a different stack.
All workflows and skills reference these values instead of hardcoded commands.

## Runtime

- **Exec prefix:** (none)
<!-- - **Exec prefix (DB):** docker compose exec db -->
<!-- - **Note:** Host has NO local runtime. ALWAYS use exec prefix. -->

## Commands

- **Install:** (set your install command)
- **Test:** (set your test command)
- **Test single:** (set your single-file test command, use {file} placeholder)
- **Lint:** (set your lint command, use {path} placeholder)
- **Type check:** (set your type check command)
- **Build:** (set your build command)
- **Dev:** (set your dev server command)
<!-- - **Validate:** (tests + build combined) -->

<!-- Node.js example:
- **Install:** npm install
- **Test:** npm run test
- **Test single:** npx vitest run {file}
- **Lint:** npx eslint {path}
- **Type check:** npx tsc --noEmit
- **Build:** npm run build
- **Dev:** npm run dev
-->

<!-- Python example:
- **Install:** pip install -r requirements.txt
- **Test:** pytest
- **Test single:** pytest {file} -v
- **Lint:** ruff check {path}
- **Type check:** mypy {path}
- **Build:** echo 'no build step'
- **Dev:** uvicorn app.main:app --reload
-->

## Paths

- **Source:** src/
- **Tests:** tests/
- **Config:** package.json

## Conventions

- **Test file pattern:** {name}.test.ts
<!-- - **Module structure:** app/{route}/page.tsx -->

<!-- Python:
- **Test file pattern:** test_{name}.py
- **Module structure:** app/{module}/
-->

## Framework

<!-- Optional: Framework-specific metadata -->
<!-- - **Name:** Next.js 14+ (App Router) -->
<!-- - **Components:** Server Components by default -->
<!-- - **Backend:** Supabase (PostgreSQL + Auth + RLS) -->
<!-- - **ORM:** Prisma -->

## Schema

<!-- Schema sync — keeps .agent/memory/schema.md up to date -->
<!-- The /feature workflow auto-verifies at startup. -->
<!-- Manual sync: /sync-schema -->
<!-- - **Source:** models -->
<!-- - **Paths:** src/models/**/*.ts -->
<!-- Examples: -->
<!-- - **Source:** models, **Paths:** prisma/schema.prisma -->
<!-- - **Source:** migrations, **Paths:** src/migrations/*.py -->
<!-- - **Source:** sql, **Paths:** schema.sql -->

## Database

<!-- Optional: Database inspection -->
<!-- - **Type:** postgresql -->
<!-- - **Schema source:** schema.sql -->
<!-- - **MCP available:** true -->
<!-- - **Read only:** true -->
