from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from tools.dashboard import gh, column_derivation
from tools.dashboard.docs_renderer import get_repo_root

router = APIRouter(prefix="/api", tags=["backlog"])


def _render_card(issue: dict, col: str, read_only: bool) -> str:
    n = issue["number"]
    title = issue.get("title", "")
    labels = issue.get("labels", [])

    label_chips = ""
    for lbl in labels:
        if isinstance(lbl, dict):
            name = lbl.get("name", "")
        else:
            name = str(lbl)
        label_chips += f'<span class="label-chip">{name}</span>'

    actions = ""
    if col != "done":
        if col == "backlog" and not read_only:
            actions += (
                f'<button class="btn-action"'
                f' hx-patch="/api/issues/{n}/label"'
                f' hx-vals=\'{{"action":"add_ready"}}\''
                f' hx-target=".kanban-board" hx-swap="outerHTML">Move to Ready</button>'
            )
        if col == "ready" and not read_only:
            actions += (
                f'<button class="btn-action"'
                f' hx-patch="/api/issues/{n}/label"'
                f' hx-vals=\'{{"action":"remove_ready"}}\''
                f' hx-target=".kanban-board" hx-swap="outerHTML">Move to Backlog</button>'
            )
        actions += (
            f'<button class="copy-btn" data-cmd="/feature #{n}"'
            f' onclick="navigator.clipboard.writeText(this.dataset.cmd);'
            f" this.textContent='Copied!';"
            f" setTimeout(()=>this.textContent='/feature #{n}',1500)\">/feature #{n}</button>"
        )
        if not read_only:
            actions += (
                f'<button class="btn-action btn-danger"'
                f' hx-delete="/api/issues/{n}"'
                f' hx-target=".kanban-board" hx-swap="outerHTML"'
                f' hx-confirm="Close issue #{n}?">Close</button>'
            )

    return (
        f'<div class="card" data-issue="{n}">'
        f'<div class="card-header">'
        f'<span class="card-num">#{n}</span>'
        f'<span class="card-labels">{label_chips}</span>'
        f'</div>'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-actions">{actions}</div>'
        f'</div>'
    )


def _render_board(read_only: bool) -> str:
    repo_root = str(get_repo_root())

    try:
        open_issues = gh.list_issues(repo_root, state="open", limit=100)
    except RuntimeError:
        open_issues = []

    try:
        closed_issues = gh.list_closed_issues(repo_root, limit=20)
    except RuntimeError:
        closed_issues = []

    try:
        local_branches = gh.list_local_branches(repo_root)
    except RuntimeError:
        local_branches = []

    try:
        remote_branches = gh.list_remote_branches(repo_root)
    except RuntimeError:
        remote_branches = []

    try:
        open_prs = gh.list_prs(repo_root, state="open")
    except RuntimeError:
        open_prs = []

    all_issues = open_issues + closed_issues

    columns: dict[str, list[dict]] = {
        "backlog": [],
        "ready": [],
        "in_progress": [],
        "done": [],
    }

    for issue in all_issues:
        col = column_derivation.derive_column(issue, local_branches, remote_branches, open_prs)
        columns[col].append(issue)

    def cards_html(col: str) -> str:
        return "".join(_render_card(issue, col, read_only) for issue in columns[col])

    backlog_count = len(columns["backlog"])
    ready_count = len(columns["ready"])
    in_progress_count = len(columns["in_progress"])
    done_count = len(columns["done"])

    create_form = ""
    if not read_only:
        create_form = (
            '<form class="create-form"'
            ' hx-post="/api/issues" hx-target="#col-backlog .cards" hx-swap="beforeend"'
            ' hx-on::after-request="this.reset()">'
            '<input name="title" placeholder="New task title" required>'
            '<textarea name="body" placeholder="Description (optional)"></textarea>'
            '<select name="label">'
            '<option value="enhancement">enhancement</option>'
            '<option value="bug">bug</option>'
            '<option value="documentation">documentation</option>'
            '</select>'
            '<button type="submit">+ Add</button>'
            '</form>'
        )

    html = (
        '<div class="kanban-board">'

        '<div class="kanban-col" id="col-backlog">'
        f'<h3>Backlog <span class="col-count">{backlog_count}</span></h3>'
        f'{create_form}'
        f'<div class="cards">{cards_html("backlog")}</div>'
        '</div>'

        '<div class="kanban-col" id="col-ready">'
        f'<h3>Ready <span class="col-count">{ready_count}</span></h3>'
        f'<div class="cards">{cards_html("ready")}</div>'
        '</div>'

        '<div class="kanban-col" id="col-in-progress">'
        f'<h3>In Progress <span class="col-count">{in_progress_count}</span></h3>'
        f'<div class="cards">{cards_html("in_progress")}</div>'
        '</div>'

        '<div class="kanban-col" id="col-done">'
        f'<h3>Done <span class="col-count">{done_count}</span></h3>'
        f'<div class="cards">{cards_html("done")}</div>'
        '</div>'

        '</div>'
    )
    return html


@router.get("/backlog")
def get_backlog(request: Request):
    read_only = request.app.state.read_only
    html = _render_board(read_only)
    return HTMLResponse(html)


class CreateIssue(BaseModel):
    title: str
    body: str = ""
    label: str = "enhancement"


@router.post("/issues")
def create_issue(data: CreateIssue, request: Request):
    if request.app.state.read_only:
        raise HTTPException(403, "Read-only mode")
    repo_root = str(get_repo_root())
    number = gh.create_issue(repo_root, data.title, data.body, data.label)
    issue = {"number": number, "title": data.title, "labels": [{"name": data.label}], "state": "OPEN"}
    html = _render_card(issue, "backlog", read_only=False)
    return HTMLResponse(html)


class LabelAction(BaseModel):
    action: str


@router.patch("/issues/{n}/label")
def update_label(n: int, data: LabelAction, request: Request):
    if request.app.state.read_only:
        raise HTTPException(403, "Read-only mode")
    repo_root = str(get_repo_root())
    if data.action == "add_ready":
        gh.edit_issue_labels(repo_root, n, add=["ready"])
    elif data.action == "remove_ready":
        gh.edit_issue_labels(repo_root, n, remove=["ready"])
    else:
        raise HTTPException(400, f"Unknown action: {data.action}")
    html = _render_board(read_only=False)
    return HTMLResponse(html)


class EditIssue(BaseModel):
    title: str | None = None
    body: str | None = None


@router.patch("/issues/{n}")
def edit_issue(n: int, data: EditIssue, request: Request):
    if request.app.state.read_only:
        raise HTTPException(403, "Read-only mode")
    repo_root = str(get_repo_root())
    gh.edit_issue(repo_root, n, title=data.title, body=data.body)
    html = _render_board(read_only=False)
    return HTMLResponse(html)


@router.delete("/issues/{n}")
def close_issue(n: int, request: Request):
    if request.app.state.read_only:
        raise HTTPException(403, "Read-only mode")
    repo_root = str(get_repo_root())
    gh.close_issue(repo_root, n)
    html = _render_board(read_only=False)
    return HTMLResponse(html)
