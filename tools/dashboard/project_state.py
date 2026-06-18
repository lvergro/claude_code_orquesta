from pathlib import Path
import re


_DEFAULTS = {
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


def parse_project_state(path: Path) -> dict:
    if not path.exists():
        return dict(_DEFAULTS)

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    result = dict(_DEFAULTS)
    result["waves"] = []
    result["current_focus"] = {"task": "", "file": "", "test": ""}
    result["recent_decisions"] = []

    # Identify section boundaries
    section_starts = {}  # section_name -> line index
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section_starts[line[3:].strip()] = i

    # Parse top-level YAML-ish key: value lines (before first ## section)
    first_section = min(section_starts.values()) if section_starts else len(lines)
    top_level_keys = {"updated", "skill", "issue", "branch", "phase"}
    for line in lines[:first_section]:
        m = re.match(r"^(\w[\w_]*):\s*(.*)", line)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip().strip('"')
            if key in top_level_keys:
                result[key] = val

    # Helper: get lines for a section
    section_names = list(section_starts.keys())

    def get_section_lines(name: str) -> list[str]:
        if name not in section_starts:
            return []
        start = section_starts[name]
        # Find next ## section
        idx = section_names.index(name)
        if idx + 1 < len(section_names):
            end = section_starts[section_names[idx + 1]]
        else:
            end = len(lines)
        # Skip the ## heading line itself
        return lines[start + 1:end]

    # Parse ## Active Tasks
    active_lines = get_section_lines("Active Tasks")
    current_wave = None
    for line in active_lines:
        wave_m = re.match(r"^###\s+(.*)", line)
        if wave_m:
            current_wave = {"name": wave_m.group(1).strip(), "tasks": []}
            result["waves"].append(current_wave)
            continue
        if current_wave is not None:
            done_m = re.match(r"^- \[x\]\s+(.*)", line, re.IGNORECASE)
            pending_m = re.match(r"^- \[ \]\s+(.*)", line)
            if done_m:
                current_wave["tasks"].append({"done": True, "text": done_m.group(1).strip()})
            elif pending_m:
                current_wave["tasks"].append({"done": False, "text": pending_m.group(1).strip()})

    # Parse ## Current Focus
    focus_lines = get_section_lines("Current Focus")
    for line in focus_lines:
        m = re.match(r"^(task|file|test):\s*(.*)", line, re.IGNORECASE)
        if m:
            result["current_focus"][m.group(1).lower()] = m.group(2).strip()

    # Parse ## Blockers
    blockers_lines = get_section_lines("Blockers")
    blockers_text = "\n".join(blockers_lines).strip()
    result["blockers"] = blockers_text if blockers_text else "(none)"

    # Parse ## Recent Decisions (last 5)  — match by prefix
    decisions_key = next(
        (k for k in section_names if k.startswith("Recent Decisions")), None
    )
    if decisions_key:
        decisions_lines = get_section_lines(decisions_key)
        for line in decisions_lines:
            m = re.match(r"^-\s+(.*)", line)
            if m:
                result["recent_decisions"].append(m.group(1).strip())

    return result
