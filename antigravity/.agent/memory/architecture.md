# System Architecture

This document is the SINGLE SOURCE OF TRUTH for system design.
All code must conform to it.

---

## 1. System Overview

<!-- Describe your project in 2-3 sentences. What does it do? Who uses it? -->

---

## 2. High-Level Architecture

<!-- Document your stack and execution model -->

### Frontend
<!-- e.g., Next.js, React, Vue, etc. -->

### Backend
<!-- e.g., Express, FastAPI, Supabase, etc. -->

### Execution Model
<!-- e.g., Monolith, microservices, serverless, etc. -->

---

## 3. Data Model

<!-- Describe your core entities and relationships in prose or with SQL/diagrams -->

---

## 4. Roles & Authorization

<!-- Define your role hierarchy and permission model -->

---

## 5. Critical Flows

<!-- Document the contracts for business-critical operations -->
<!-- For each flow: inputs → validations → steps → outputs -->
<!-- Indicate which flows require atomic transactions -->

---

## 6. Forbidden Patterns

<!-- List patterns that must NEVER appear in the codebase -->
<!-- e.g., business logic in view layer, hardcoded secrets, etc. -->

---

## 7. Change Policy

Only architecture-level analysis may modify this file.

All changes must be:
- Explicit
- Intentional
- Reviewed

---

## Changelog

<!-- Record architectural decisions here -->
<!-- Format: ### YYYY-MM-DD: [Change Title] -->
<!-- Include: Status, Changes, Rationale, Next Steps -->
