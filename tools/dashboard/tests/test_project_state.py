import tempfile
from pathlib import Path

from tools.dashboard.project_state import parse_project_state

SAMPLE_MD = """\
updated: 2026-06-12
skill: feature
issue: 42
branch: feat/42-orquesta-studio
phase: execution

## Active Tasks

### Wave 1 — Backend

- [x] Implement column derivation
- [x] Add gh helpers
- [ ] Write tests

### Wave 2 — UI

- [ ] Build kanban board
- [ ] Add state panel

## Current Focus

task: Write tests for column_derivation
file: tools/dashboard/tests/test_column_derivation.py
test: pending

## Blockers

(none)

## Recent Decisions (last 5)

- Use FastAPI for the dashboard
- Derive kanban columns from GitHub state, no local DB
- Read-only mode via --read-only flag
"""


def _write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_top_level_fields():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    assert result["skill"] == "feature"
    assert result["issue"] == "42"
    assert result["branch"] == "feat/42-orquesta-studio"
    assert result["phase"] == "execution"
    assert result["updated"] == "2026-06-12"


def test_wave_count():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    assert len(result["waves"]) == 2


def test_tasks_done_and_pending():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    wave1 = result["waves"][0]
    done_tasks = [t for t in wave1["tasks"] if t["done"]]
    pending_tasks = [t for t in wave1["tasks"] if not t["done"]]
    assert len(done_tasks) == 2
    assert len(pending_tasks) == 1
    assert done_tasks[0]["text"] == "Implement column derivation"
    assert pending_tasks[0]["text"] == "Write tests"


def test_current_focus_fields():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    focus = result["current_focus"]
    assert focus["task"] == "Write tests for column_derivation"
    assert focus["file"] == "tools/dashboard/tests/test_column_derivation.py"
    assert focus["test"] == "pending"


def test_blockers_none():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    assert result["blockers"] == "(none)"


def test_recent_decisions_length():
    path = _write_temp(SAMPLE_MD)
    result = parse_project_state(path)
    assert len(result["recent_decisions"]) == 3


def test_missing_file_returns_defaults():
    missing = Path("/tmp/nonexistent_project_state_xyz.md")
    result = parse_project_state(missing)
    assert result["skill"] == ""
    assert result["issue"] == ""
    assert result["branch"] == ""
    assert result["phase"] == ""
    assert result["updated"] == ""
    assert result["waves"] == []
    assert result["current_focus"] == {"task": "", "file": "", "test": ""}
    assert result["blockers"] == "(none)"
    assert result["recent_decisions"] == []
