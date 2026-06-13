import subprocess
import re

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from tools.dashboard.project_state import parse_project_state
from tools.dashboard.gh import list_worktrees
from tools.dashboard.docs_renderer import get_repo_root

router = APIRouter(prefix="/api", tags=["state"])


def _get_github_repo_url(repo_root) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True, check=False,
        cwd=str(repo_root),
    )
    if result.returncode != 0:
        return ""
    url = result.stdout.strip()
    # Convert SSH or HTTPS git URL to https web URL
    # git@github.com:owner/repo.git  -> https://github.com/owner/repo
    # https://github.com/owner/repo.git -> https://github.com/owner/repo
    url = re.sub(r"\.git$", "", url)
    url = re.sub(r"^git@github\.com:", "https://github.com/", url)
    return url


def _escape(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_state_html(state: dict, worktrees: list[dict], repo_url: str = "") -> str:
    parts = ['<div class="state-panel">']

    # --- Pipeline State ---
    parts.append('<section class="state-section">')
    parts.append("<h3>Pipeline State</h3>")
    parts.append('<table class="state-table">')

    phase = _escape(state.get("phase", ""))
    phase_class = re.sub(r"[^a-z0-9-]", "-", phase.lower()) if phase else "unknown"

    rows = [
        ("Updated", _escape(state.get("updated", ""))),
        ("Skill",   _escape(state.get("skill", ""))),
        ("Issue",   _escape(state.get("issue", ""))),
    ]
    for th, td in rows:
        parts.append(f"<tr><th>{th}</th><td>{td}</td></tr>")

    branch = _escape(state.get("branch", ""))
    parts.append(f"<tr><th>Branch</th><td><code>{branch}</code></td></tr>")
    parts.append(
        f'<tr><th>Phase</th>'
        f'<td><span class="phase-badge {phase_class}">{phase}</span></td></tr>'
    )
    parts.append("</table>")
    parts.append("</section>")

    # --- Active Tasks ---
    parts.append('<section class="state-section">')
    parts.append("<h3>Active Tasks</h3>")
    waves = state.get("waves", [])
    for wave in waves:
        wave_name = _escape(wave.get("name", ""))
        parts.append('<div class="wave">')
        parts.append(f"<h4>{wave_name}</h4>")
        parts.append("<ul>")
        for task in wave.get("tasks", []):
            done = task.get("done", False)
            text = _escape(task.get("text", ""))
            if done:
                parts.append(f'<li class="task done">&#x2705; {text}</li>')
            else:
                parts.append(f'<li class="task pending">&#x2B1C; {text}</li>')
        parts.append("</ul>")
        parts.append("</div>")
    if not waves:
        parts.append("<p>No active tasks.</p>")
    parts.append("</section>")

    # --- Current Focus ---
    focus = state.get("current_focus", {})
    parts.append('<section class="state-section">')
    parts.append("<h3>Current Focus</h3>")
    parts.append("<dl>")
    parts.append(f'<dt>Task</dt><dd>{_escape(focus.get("task", ""))}</dd>')
    parts.append(f'<dt>File</dt><dd><code>{_escape(focus.get("file", ""))}</code></dd>')
    parts.append(f'<dt>Test</dt><dd>{_escape(focus.get("test", ""))}</dd>')
    parts.append("</dl>")
    parts.append("</section>")

    # --- Blockers ---
    blockers_text = state.get("blockers", "(none)")
    is_none = blockers_text.strip().lower() in ("(none)", "none", "")
    blocker_class = "none" if is_none else "has-blocker"
    parts.append('<section class="state-section">')
    parts.append("<h3>Blockers</h3>")
    parts.append(f'<p class="blockers {blocker_class}">{_escape(blockers_text)}</p>')
    parts.append("</section>")

    # --- Active Worktrees ---
    parts.append('<section class="state-section">')
    parts.append("<h3>Active Worktrees</h3>")
    if worktrees:
        parts.append('<ul class="worktree-list">')
        for wt in worktrees:
            wt_branch = _escape(wt.get("branch", ""))
            wt_path = _escape(wt.get("path", ""))
            issue_num = wt.get("issue_number")
            issue_link = ""
            if issue_num:
                if repo_url:
                    issue_link = (
                        f' &#x2192; <a href="{repo_url}/issues/{issue_num}" '
                        f'target="_blank">#{issue_num}</a>'
                    )
                else:
                    issue_link = f" &#x2192; #{issue_num}"
            parts.append(
                f"<li><code>{wt_branch}</code>{issue_link}"
                f" <small>{wt_path}</small></li>"
            )
        parts.append("</ul>")
    else:
        parts.append("<p>No active worktrees.</p>")
    parts.append("</section>")

    # --- Recent Decisions ---
    decisions = state.get("recent_decisions", [])
    parts.append('<section class="state-section">')
    parts.append("<h3>Recent Decisions</h3>")
    if decisions:
        parts.append("<ul>")
        for d in decisions:
            parts.append(f"<li>{_escape(d)}</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>No recent decisions.</p>")
    parts.append("</section>")

    parts.append("</div>")
    return "\n".join(parts)


@router.get("/state")
def get_state():
    repo = get_repo_root()
    state_path = repo / ".claude" / "memory" / "project-state.md"
    state = parse_project_state(state_path)

    try:
        worktrees = list_worktrees(str(repo))
    except Exception:
        worktrees = []

    for wt in worktrees:
        branch = wt.get("branch", "")
        m = re.match(r"feat/(\d+)-", branch)
        wt["issue_number"] = m.group(1) if m else None

    try:
        repo_url = _get_github_repo_url(repo)
    except Exception:
        repo_url = ""

    html = render_state_html(state, worktrees, repo_url)
    return HTMLResponse(html)
