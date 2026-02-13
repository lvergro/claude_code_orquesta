# Data Model Schema

Last synced: (never)

This file is the lightweight, token-efficient representation of the project's data model.
It is updated automatically at the start of `/feature` when drift is detected.
Manual sync: `/sync-schema`

---

## Tables

<!-- Use compact YAML-like format:
users:
  pk: id (uuid)
  cols: [email (unique), name, role (enum: admin|user), tenant_id (fk: orgs)]
  timestamps: true
  indexes: [email]

orders:
  pk: id (uuid)
  cols: [user_id (fk: users), total (decimal), status (enum: pending|paid|cancelled)]
  timestamps: true
-->

(no tables defined yet — run `/sync-schema` or start a `/feature` to auto-populate)
