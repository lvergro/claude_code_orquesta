from tools.dashboard.column_derivation import derive_column


def _issue(number: int, state: str = "OPEN", labels: list = None) -> dict:
    return {"number": number, "state": state, "labels": labels or []}


def test_closed_issue_is_done():
    issue = _issue(42, state="CLOSED")
    assert derive_column(issue, [], [], []) == "done"


def test_local_branch_matching_issue_is_in_progress():
    issue = _issue(42)
    assert derive_column(issue, ["feat/42-my-feature"], [], []) == "in_progress"


def test_remote_branch_matching_issue_is_in_progress():
    issue = _issue(42)
    assert derive_column(issue, [], ["feat/42-my-feature"], []) == "in_progress"


def test_open_pr_matching_issue_is_in_progress():
    issue = _issue(42)
    prs = [{"number": 10, "headRefName": "feat/42-my-feature", "state": "OPEN"}]
    assert derive_column(issue, [], [], prs) == "in_progress"


def test_ready_label_is_ready():
    issue = _issue(42, labels=[{"name": "ready"}])
    assert derive_column(issue, [], [], []) == "ready"


def test_no_branch_no_label_open_is_backlog():
    issue = _issue(42)
    assert derive_column(issue, [], [], []) == "backlog"


def test_branch_for_different_issue_does_not_match():
    issue = _issue(42)
    assert derive_column(issue, ["feat/99-bar"], [], []) == "backlog"


def test_closed_issue_with_matching_branch_is_done():
    issue = _issue(42, state="CLOSED")
    assert derive_column(issue, ["feat/42-my-feature"], [], []) == "done"
