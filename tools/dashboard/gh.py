import subprocess
import json
import re
from pathlib import Path


def _run(cmd: list[str], cwd: str | None = None) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command {cmd} failed: {result.stderr}")
    return result.stdout


def list_issues(repo_root: str, state: str = "open", limit: int = 100) -> list[dict]:
    out = _run(
        ["gh", "issue", "list", "--state", state, "--limit", str(limit),
         "--json", "number,title,body,labels,assignees,state"],
        cwd=repo_root,
    )
    return json.loads(out)


def get_issue(repo_root: str, number: int) -> dict:
    out = _run(
        ["gh", "issue", "view", str(number),
         "--json", "number,title,body,labels,assignees,state"],
        cwd=repo_root,
    )
    return json.loads(out)


def create_issue(repo_root: str, title: str, body: str, label: str | None = None) -> int:
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    if label:
        cmd += ["--label", label]
    out = _run(cmd, cwd=repo_root)
    url = out.strip()
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise RuntimeError(f"Could not parse issue number from: {url}")
    return int(m.group(1))


def edit_issue_labels(repo_root: str, number: int, add: list[str] = [], remove: list[str] = []) -> None:
    cmd = ["gh", "issue", "edit", str(number)]
    for label in add:
        cmd += ["--add-label", label]
    for label in remove:
        cmd += ["--remove-label", label]
    _run(cmd, cwd=repo_root)


def edit_issue(repo_root: str, number: int, title: str | None = None, body: str | None = None) -> None:
    cmd = ["gh", "issue", "edit", str(number)]
    if title is not None:
        cmd += ["--title", title]
    if body is not None:
        cmd += ["--body", body]
    _run(cmd, cwd=repo_root)


def close_issue(repo_root: str, number: int) -> None:
    _run(["gh", "issue", "close", str(number)], cwd=repo_root)


def list_prs(repo_root: str, state: str = "open") -> list[dict]:
    out = _run(
        ["gh", "pr", "list", "--state", state,
         "--json", "number,title,headRefName,state"],
        cwd=repo_root,
    )
    return json.loads(out)


def list_local_branches(repo_root: str) -> list[str]:
    out = _run(["git", "branch", "--list", "feat/*"], cwd=repo_root)
    branches = []
    for line in out.splitlines():
        branch = line.strip().lstrip("* ").strip()
        if branch:
            branches.append(branch)
    return branches


def list_remote_branches(repo_root: str) -> list[str]:
    out = _run(["git", "branch", "-r", "--list", "origin/feat/*"], cwd=repo_root)
    branches = []
    for line in out.splitlines():
        branch = line.strip()
        if branch.startswith("origin/"):
            branch = branch[len("origin/"):]
        if branch:
            branches.append(branch)
    return branches


def list_worktrees(repo_root: str) -> list[dict]:
    out = _run(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    worktrees = []
    current: dict = {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            current = {"path": line[len("worktree "):].strip()}
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            ref = line[len("branch "):].strip()
            if ref.startswith("refs/heads/"):
                ref = ref[len("refs/heads/"):]
            current["branch"] = ref
        elif line == "" and current:
            if "branch" in current:
                worktrees.append(current)
            current = {}
    if current and "branch" in current:
        worktrees.append(current)
    return worktrees


def list_closed_issues(repo_root: str, limit: int = 20) -> list[dict]:
    out = _run(
        ["gh", "issue", "list", "--state", "closed", "--limit", str(limit),
         "--json", "number,title,labels,assignees,state"],
        cwd=repo_root,
    )
    return json.loads(out)
