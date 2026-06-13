from unittest.mock import patch, MagicMock
from pathlib import Path

from fastapi.testclient import TestClient

from tools.dashboard.main import create_app

app_ro = create_app(read_only=True)
app_rw = create_app(read_only=False)

client_ro = TestClient(app_ro, raise_server_exceptions=False)
client_rw = TestClient(app_rw, raise_server_exceptions=False)


def test_post_issues_ro_returns_403():
    resp = client_ro.post("/api/issues", json={"title": "Test", "body": "", "label": "enhancement"})
    assert resp.status_code == 403


def test_patch_issue_label_ro_returns_403():
    resp = client_ro.patch("/api/issues/1/label", json={"action": "add_ready"})
    assert resp.status_code == 403


def test_patch_issue_ro_returns_403():
    resp = client_ro.patch("/api/issues/1", json={"title": "New title"})
    assert resp.status_code == 403


def test_delete_issue_ro_returns_403():
    resp = client_ro.delete("/api/issues/1")
    assert resp.status_code == 403


def test_get_docs_tree_ro_returns_200():
    with patch("tools.dashboard.docs_renderer.get_repo_root") as mock_root:
        tmp = Path("/tmp")
        mock_root.return_value = tmp
        resp = client_ro.get("/api/docs/tree")
    assert resp.status_code == 200


def test_get_state_ro_returns_200():
    with (
        patch("tools.dashboard.state_router.get_repo_root") as mock_root,
        patch("tools.dashboard.state_router.list_worktrees") as mock_wt,
        patch("tools.dashboard.state_router._get_github_repo_url") as mock_url,
        patch("tools.dashboard.project_state.parse_project_state") as mock_parse,
    ):
        tmp = Path("/tmp")
        mock_root.return_value = tmp
        mock_wt.return_value = []
        mock_url.return_value = ""
        mock_parse.return_value = {
            "updated": "",
            "skill": "",
            "issue": "",
            "branch": "",
            "phase": "",
            "waves": [],
            "current_focus": {"task": "", "file": "", "test": ""},
            "blockers": "(none)",
            "recent_decisions": [],
        }
        resp = client_ro.get("/api/state")
    assert resp.status_code == 200
