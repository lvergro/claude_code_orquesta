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
2. **Workflow Fidelity** (high): Strictly follow `/feature` phases (0-6). GitHub issues must mirror `project-state.md`.
3. **Test Coverage** (high): Every core logic change MUST include a corresponding test (`write-tests` skill).
<!-- Add your project-specific invariants:
4. **Tenant Isolation** (critical): All DB queries filter by tenant_id. No cross-tenant data leaks.
5. **Atomic Transactions** (critical): Payment and inventory flows MUST be atomic. No partial success.
-->

## Critical Flows

<!-- Flows that require special care (transactions, security-critical, etc.) -->
<!-- Example:
1. **Payment Processing**: Validate payment → charge card → update balance → send receipt
   - Tables: payments, balances, receipts
   - Type: transaction
-->

## Gate-Protected Areas

Areas that require extra care during `/feature` execution.

- `migrations/` — Schema changes require careful planning
<!-- Add patterns for sensitive areas:
- `auth/**` — Authentication logic
- `middleware*` — Request routing and security
-->
