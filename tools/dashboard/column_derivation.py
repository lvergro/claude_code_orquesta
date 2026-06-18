import re


def derive_column(
    issue: dict,
    local_branches: list[str],
    remote_branches: list[str],
    open_prs: list[dict],
) -> str:
    if issue.get("state") == "CLOSED":
        return "done"

    n = issue["number"]
    pattern = re.compile(rf"feat/{n}-")

    for branch in local_branches:
        if pattern.search(branch):
            return "in_progress"

    for branch in remote_branches:
        if pattern.search(branch):
            return "in_progress"

    for pr in open_prs:
        if pattern.search(pr.get("headRefName", "")):
            return "in_progress"

    for label in issue.get("labels", []):
        if isinstance(label, dict):
            name = label.get("name", "")
        else:
            name = str(label)
        if name == "ready":
            return "ready"

    return "backlog"
