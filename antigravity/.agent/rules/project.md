# Project Identity

This file defines WHAT the project is. Stack-agnostic.
Change THIS file when adapting the framework to a different project.

## Project

- **Name:** MyProject
- **Description:** Brief project description

## Domain

- **Language:** en
- **Entities:** (list your domain entities)
  <!-- Example:
  - organization (tenant)
  - user
  - order
  - product
  -->

## Multi-Tenancy

<!-- Remove this section or set enabled: false if single-tenant -->
- **Enabled:** false
<!-- - **Column:** tenant_id -->
<!-- - **Table:** organizations -->
<!-- - **Membership table:** org_memberships -->
<!-- - **Isolation:** rls -->
<!-- - **Global role:** super_admin -->

## Invariants

Rules that must NEVER be violated. The agent stops and reports if any breaks.

1. **Security** (critical): No hardcoded secrets. Auth tokens are the source of truth.
<!-- Add your project-specific invariants:
2. **Tenant Isolation** (critical): All DB queries filter by tenant_id. No cross-tenant data leaks.
3. **Atomic Transactions** (critical): Payment and inventory flows MUST be atomic. No partial success.
-->

## Critical Flows

<!-- Flows that require special care (transactions, security-critical, etc.) -->
<!-- Example:
1. **Payment Processing**: Validate payment → charge card → update balance → send receipt
   - Tables: payments, balances, receipts
   - Type: transaction
-->

## Gate-Protected Areas

Areas that `/quick` will reject — forces `/develop` instead.

- `migrations/` — Schema changes require full /develop pipeline
<!-- Add patterns for sensitive areas:
- `auth/**` — Authentication logic
- `middleware*` — Request routing and security
-->
