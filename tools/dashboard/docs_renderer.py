import re
from pathlib import Path

import markdown as md_lib


def get_repo_root() -> Path:
    """Return the repo root (two levels up from tools/dashboard/)."""
    return Path(__file__).parent.parent.parent


def build_file_tree(root: Path, label: str) -> list[dict]:
    """
    Walk root recursively, return list of nodes.
    Sort: dirs first, then files, both alphabetically.
    Skip hidden files/dirs (starting with .) except .claude.
    Skip __pycache__ dirs.
    """
    repo_root = get_repo_root()

    def _walk(path: Path) -> list[dict]:
        entries = []
        try:
            children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return []

        for child in children:
            name = child.name
            if name.startswith(".") and name != ".claude":
                continue
            if name == "__pycache__":
                continue

            try:
                rel = str(child.relative_to(repo_root))
            except ValueError:
                rel = str(child)

            if child.is_dir():
                entries.append({
                    "label": name,
                    "path": rel,
                    "type": "dir",
                    "children": _walk(child),
                })
            else:
                entries.append({
                    "label": name,
                    "path": rel,
                    "type": "file",
                    "children": [],
                })

        return entries

    try:
        rel_root = str(root.relative_to(repo_root))
    except ValueError:
        rel_root = str(root)

    return [{
        "label": label,
        "path": rel_root,
        "type": "dir",
        "children": _walk(root),
    }]


def render_markdown(path: Path) -> str:
    """
    Read file at path, render markdown to HTML.
    Mermaid fences are converted to <pre class="mermaid">...</pre>.
    """
    text = path.read_text(encoding="utf-8")

    # Extract mermaid blocks before markdown processing
    mermaid_placeholder = {}
    counter = [0]

    def replace_mermaid(m):
        key = f"MERMAID_PLACEHOLDER_{counter[0]}_END"
        mermaid_placeholder[key] = m.group(1)
        counter[0] += 1
        return key

    text = re.sub(r"```mermaid\n(.*?)```", replace_mermaid, text, flags=re.DOTALL)

    extensions = ["fenced_code", "tables", "nl2br"]
    html = md_lib.markdown(text, extensions=extensions)

    # Restore mermaid blocks as <pre class="mermaid">
    for key, content in mermaid_placeholder.items():
        html = html.replace(key, f'<pre class="mermaid">{content}</pre>')

    return html


def render_tree_html(sections: list[list[dict]]) -> str:
    """
    Render a list of tree-node dicts into an HTML sidebar fragment.
    Each section is a list of dicts (as returned by build_file_tree).
    """

    def render_nodes(nodes: list[dict]) -> str:
        if not nodes:
            return ""
        parts = ["<ul>"]
        for node in nodes:
            if node["type"] == "dir":
                inner = render_nodes(node["children"])
                parts.append(
                    f'<li><details><summary>{node["label"]}/</summary>{inner}</details></li>'
                )
            else:
                path = node["path"]
                label = node["label"]
                if label.endswith(".md"):
                    parts.append(
                        f'<li><a href="#" hx-get="/api/docs/file?path={path}" '
                        f'hx-target="#doc-content" hx-push-url="false" '
                        f'class="doc-link">{label}</a></li>'
                    )
                else:
                    parts.append(
                        f'<li><span class="doc-link non-md">{label}</span></li>'
                    )
        parts.append("</ul>")
        return "".join(parts)

    html_parts = ['<nav id="doc-tree">']
    for section in sections:
        for node in section:
            inner = render_nodes(node["children"])
            html_parts.append(
                f'<details open><summary>{node["label"]}</summary>{inner}</details>'
            )
    html_parts.append("</nav>")
    return "".join(html_parts)
