---
name: qa-test
description: >
  Tests software functionality and validates user flows through the browser.
  Runs unit tests, integration tests, and E2E browser automation.
  Generates a structured QA report with pass/fail results and screenshots.
user-invocable: true
---

# /qa-test — Quality Assurance Testing

Read `.claude/models.yml` for model routing. This skill uses model: sonnet.

Input: `[target]` — a URL, feature name, flow description, test file path, or leave blank to run all tests.

Examples:
- `/qa-test` → run all automated tests
- `/qa-test login flow` → test the login flow through the browser
- `/qa-test http://localhost:3000/dashboard` → E2E test a specific URL
- `/qa-test tests/auth.test.ts` → run a single test file
- `/qa-test full` → full QA pass (unit + E2E)

---

## phase 0: setup

1. Read `.claude/stack.yml` → load `commands`, `exec_prefix`, `paths`
2. Read `.claude/project.yml` → load `critical_flows`, `invariants`
3. Parse input to determine mode:
   - No input or `all` → **Mode A: All automated tests**
   - `full` → **Mode D: Full QA pass**
   - Input is a URL (`http://...` or `localhost:...`) → **Mode C: Browser E2E**
   - Input is a file path (`.ts`, `.py`, `.spec.`) → **Mode A: Single test file**
   - Input is descriptive text → **Mode B: Flow testing** (browser + heuristic)

4. Create output directory:
   ```
   mkdir -p .claude/memory/qa
   ```

---

## Mode A: Automated Tests

### A1 — Single file
```
{exec_prefix} {stack.commands.test_single file=INPUT}
```

### A2 — All tests
```
{exec_prefix} {stack.commands.test}
```

**Output per suite:**
- `✅ PASS: [suite name]`
- `❌ FAIL: [suite name] — [first error line]`

**On failure:** extract the exact error message and failing assertion. Do NOT retry silently.

---

## Mode B: Browser Flow Testing

Invoke **QA agent** with:
- Flow description from user input
- Dev URL from `stack.yml` (if not configured, use `http://localhost:3000` as default)
- Critical flows from `project.yml` as reference

**QA agent steps:**
1. Navigate to the app URL
2. Execute the described flow step by step using Playwright MCP tools
3. Assert expected outcomes at each step
4. Take screenshot on each failure
5. Take final screenshot showing end state

**If Playwright MCP not available:** fall back to generating a manual test checklist in the report.

---

## Mode C: URL E2E Testing

Invoke **QA agent** with target URL.

**Standard checks performed:**
1. Page loads without console errors (`browser_evaluate`: `window.console.error` count)
2. No broken links (check `<a>` elements return 200)
3. Key interactive elements are present and clickable
4. Forms submit without errors
5. Auth-gated pages redirect correctly if not logged in

Take screenshot of the fully loaded page.

---

## Mode D: Full QA Pass

Run in order:
1. **Mode A** (all automated tests)
2. **Mode B** for each flow in `project.yml → critical_flows`
3. Generate consolidated report

---

## phase 1: report generation

Write `.claude/memory/qa-report.md`:

```markdown
# QA Report
date: YYYY-MM-DD
target: [input target]
mode: [A|B|C|D]
status: PASS | FAIL | PARTIAL

## Automated Tests
[results per suite]

## Browser Tests
[results per flow with screenshots]

## Issues Found
| Severity | Description | Steps to Reproduce |
|----------|-------------|-------------------|
| critical | ... | ... |
| high     | ... | ... |
| low      | ... | ... |

## Screenshots
[list of .claude/memory/qa/*.png]

## Summary
X/Y test suites passed. Z browser flows validated. N issues found.
```

---

## phase 2: output

- Print report summary to console
- `✅ QA complete: X/Y passed — report at .claude/memory/qa-report.md`
- If any failures: `❌ QA failed: N issues found — see .claude/memory/qa-report.md`

---

## error handling

| Error | Action |
|-------|--------|
| Dev server not running | `❌ Error: Start dev server first: {stack.commands.dev}` |
| Test command not configured | `❌ Error: Configure stack.commands.test in .claude/stack.yml` |
| Playwright MCP unavailable | Fall back to manual checklist in report |
| Test timeout | Mark as `❌ TIMEOUT` and continue |
| Auth required for URL | Skip auth-gated flows and note them in the report as `⚠️ SKIPPED: auth required` |

---

## conventions

- Screenshots: `.claude/memory/qa/qa-[flow]-[step]-[timestamp].png`
- Report: `.claude/memory/qa-report.md` (overwritten each run)
- Use test/staging accounts — NEVER use production credentials
- Each run overwrites the report; archive manually if needed
