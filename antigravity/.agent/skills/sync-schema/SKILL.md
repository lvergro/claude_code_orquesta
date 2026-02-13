---
description: Reads project model/migration files and regenerates .agent/memory/schema.md with compact representation
---

# /sync-schema

Synchronizes `.agent/memory/schema.md` with the actual data model files.

## Flow

1. Read `.agent/rules/stack.md` → Schema section
   - `Schema source` not defined → `Error: No schema source configured in stack.md. Add a Schema section.`
   - `Schema paths` not defined → `Error: No schema paths configured in stack.md.`

2. Read all files matching schema paths globs

3. Extract entities, columns, types, relationships, constraints, and indexes from the source files
   - Adapt extraction to source type:
     - `models` → parse ORM model definitions (Prisma, Django, SQLAlchemy, Sequelize, TypeORM, etc.)
     - `migrations` → parse migration files in chronological order, apply changes sequentially
     - `sql` → parse SQL DDL statements (CREATE TABLE, ALTER TABLE)
     - `manual` → read the files as-is (user maintains them in compact format)

4. Generate compact YAML-like representation:
   ```
   table_name:
     pk: column (type)
     cols: [col1 (type, constraint), col2 (type, fk: other_table)]
     timestamps: true|false
     indexes: [col1, col2]
   ```
   Rules:
   - Omit `timestamps: false` (only show when true)
   - Omit `indexes` if none
   - Use short type names: `uuid`, `text`, `int`, `decimal`, `bool`, `json`, `datetime`
   - Mark constraints inline: `unique`, `nullable`, `fk: table`, `enum: val1|val2|val3`
   - Group related tables with a blank line

5. Write to `.agent/memory/schema.md`:
   - Update `Last synced:` timestamp
   - Replace the `## Tables` section content
   - Preserve any `## Notes` section the user may have added

6. Output: `Done: schema.md synced — N tables from {source}`

## Auto-Verification (used by /develop and /feature)

This is the verification step injected at pipeline start:

1. Read `.agent/rules/stack.md` → Schema section
   - Not configured → skip silently (no error)
2. Read `.agent/memory/schema.md` → extract `Last synced:` date
3. Check if any file in schema paths has been modified after the sync date:
   ```
   find {schema_paths} -newer .agent/memory/schema.md -type f
   ```
   - No newer files → schema is current, skip
   - Newer files found → run full sync (steps 2-6 above)
   - `schema.md` doesn't exist → run full sync
