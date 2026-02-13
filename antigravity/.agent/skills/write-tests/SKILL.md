---
name: write-tests
description: Generates automated test suites based on testing strategy. Reads stack configuration to infer framework, paths, and conventions.
---

# Write Tests — Test Strategy

## Context
- Read `.agent/rules/stack.md` for test framework and commands
- Read `.agent/rules/project.md` for critical flows

## Strategy (priority order)
1. **Security Flows**: Auth, authorization, input validation, tenant isolation
2. **Money Flows**: Calculations, transactions, idempotency, precision
3. **Happy Path**: Normal operation for each function
4. **Edge Cases**: Null, negative, malformed inputs, boundary values

## Rules
- Mock external dependencies — no real API calls
- Each test is self-contained and independent
- Test file location and naming from stack.md conventions
- Run via the test command from stack.md
