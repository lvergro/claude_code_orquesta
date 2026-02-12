---
name: write-tests
description: >
  Generates automated test suites. Defines testing strategy without code
  examples — the builder infers syntax from the stack configuration.
user-invocable: true
---

# /write-tests — Test Strategy

Read `.claude/models.yml` for model routing. This skill uses model: sonnet.

## Context
- Read `.claude/stack.yml` for test framework and commands
- Read `.claude/project.yml` for critical flows

## Strategy (priority order)
1. **Security Flows**: Auth, authorization, input validation, tenant isolation
2. **Money Flows**: Calculations, transactions, idempotency, precision
3. **Happy Path**: Normal operation for each function
4. **Edge Cases**: Null, negative, malformed inputs, boundary values

## Rules
- Mock external dependencies — no real API calls
- Each test is self-contained and independent
- Test file location: `{stack.paths.tests}` with pattern `{stack.conventions.test_file_pattern}`
- Run via: `{stack.runtime.exec_prefix} {stack.commands.test}`
