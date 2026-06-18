from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
from tools.dashboard.docs_renderer import build_file_tree, render_markdown, render_tree_html, get_repo_root

router = APIRouter(prefix="/api/docs", tags=["docs"])


@router.get("/tree")
def docs_tree():
    """Return HTML fragment: two-column layout with file tree and content pane."""
    repo = get_repo_root()
    docs_dir = repo / "docs"
    memory_dir = repo / ".claude" / "memory"

    sections = []
    if docs_dir.exists():
        sections.append(build_file_tree(docs_dir, "docs/"))
    if memory_dir.exists():
        sections.append(build_file_tree(memory_dir, ".claude/memory/"))

    tree_html = render_tree_html(sections)

    html = f"""
<div style="display:flex;gap:0;height:calc(100vh - 80px);">
  <div style="width:25%;min-width:180px;max-width:320px;overflow-y:auto;border-right:1px solid #373a40;padding:12px 8px;">
    {tree_html}
  </div>
  <div id="doc-content" style="flex:1;overflow-y:auto;padding:20px 28px;">
    <p>Select a file to view.</p>
  </div>
</div>
"""
    return HTMLResponse(html)


@router.get("/file")
def docs_file(path: str):
    """Render a single markdown file. path is relative to repo root."""
    repo = get_repo_root()
    abs_path = (repo / path).resolve()
    if not str(abs_path).startswith(str(repo.resolve())):
        return HTMLResponse("<p>Access denied.</p>", status_code=403)
    if not abs_path.exists() or abs_path.suffix != ".md":
        return HTMLResponse("<p>File not found.</p>", status_code=404)
    html = render_markdown(abs_path)
    return HTMLResponse(html)
