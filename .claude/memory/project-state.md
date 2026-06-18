# Project State
updated: 2026-06-18
skill: feature
issue: "#3"
branch: feat/3-orquesta-studio-local-zero-database-dash
comment2_id: "4698856296"
phase: done

## Active Tasks

### Wave 1: Foundation
- [x] Create `tools/dashboard/` package: `__init__.py`, `requirements.txt`, `run.sh`
- [x] `main.py`: FastAPI app factory with `--port` and `--read-only` CLI flags
- [x] `templates/index.html`: 3-tab shell (Docs / Backlog / State) with htmx wired

### Wave 2: Docs tab
- [x] `docs_renderer.py`: walk `docs/` and `.claude/memory/`, render markdown → HTML
- [x] `/api/docs/tree` GET + `/api/docs/file` GET endpoints
- [x] Docs tab UI: sidebar tree + content pane via htmx

### Wave 3: Backlog tab
- [x] `gh.py`: subprocess wrappers for gh/git CLI calls
- [x] `column_derivation.py`: pure column derivation function
- [x] `/api/backlog` GET + `/api/issues` POST/PATCH/DELETE endpoints
- [x] Backlog tab UI: kanban, create form, card detail, copy-command button

### Wave 4: State tab
- [x] `project_state.py`: parse `project-state.md`
- [x] `/api/state` GET endpoint
- [x] State tab UI

### Wave 5: Tests + Docs
- [x] `tests/test_column_derivation.py`
- [x] `tests/test_project_state.py`
- [x] `tests/test_readonly.py`
- [x] README.md + README_ES.md: Orquesta Studio section

## Current Focus
task: all waves complete — ready for PR
test: 21 passed

## Blockers
(none)

## Recent Decisions (last 5)
- FastAPI + htmx chosen (Python-only, no build step)
- gh CLI for all GitHub writes (reuses user auth, no tokens in code)
- Column derivation is a pure function over issue state + branch list (no DB)
