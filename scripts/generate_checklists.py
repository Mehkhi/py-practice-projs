#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "125-python-projects-roadmap.md"

level_header_re = re.compile(r"^##\s+(Level\s+\d+\s+—\s+.+?)\s*$")
project_header_re = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*$")

SECTION_LABELS = [
    ("what", ["**What you build:**"]),
    ("skills", ["**Skills you’ll learn:**", "**Skills you'll learn:**"]),
    ("milestones", ["**Milestones:**"]),
    ("stretch", ["**Stretch goals:**", "**Stretch Goals:**"]),
]

def load_lines():
    text = ROADMAP.read_text(encoding="utf-8")
    # Normalize newlines
    return text.splitlines()

def parse_levels(lines):
    levels = []
    i = 0
    n = len(lines)
    while i < n:
        m = level_header_re.match(lines[i])
        if not m:
            i += 1
            continue
        level_title = m.group(1)
        start = i
        i += 1
        # Collect description until first project or next level
        desc_lines = []
        while i < n and not lines[i].startswith("### ") and not level_header_re.match(lines[i]):
            desc_lines.append(lines[i])
            i += 1

        # Collect projects until next level or EOF
        projects = []
        while i < n and not level_header_re.match(lines[i]):
            pm = project_header_re.match(lines[i])
            if not pm:
                i += 1
                continue
            num = int(pm.group(1))
            title = pm.group(2)
            i += 1
            block = []
            while i < n and not level_header_re.match(lines[i]) and not project_header_re.match(lines[i]):
                block.append(lines[i])
                i += 1
            # Extract sections (single-line values after labels)
            details = {k: "" for k, _ in SECTION_LABELS}
            for key, labels in SECTION_LABELS:
                for j, line in enumerate(block):
                    s = line.strip()
                    for lbl in labels:
                        if s.startswith(lbl):
                            # Take the text after the label
                            after = s[len(lbl):].lstrip()
                            # Remove leading colon if present (should already be in lbl, but safe)
                            if after.startswith(":"):
                                after = after[1:].lstrip()
                            details[key] = after
                            break
                    if details[key]:
                        break
            projects.append({
                "num": num,
                "title": title,
                "block": block,
                "details": details,
            })

        levels.append({
            "title": level_title,
            "desc": desc_lines,
            "projects": projects,
        })
    return levels

def ensure_level_folders(levels):
    for lvl in levels:
        # Extract numeric part for folder naming consistency (e.g., "Level 1")
        m = re.match(r"Level\s+(\d+)", lvl["title"]) 
        folder_name = f"Level {m.group(1)}" if m else lvl["title"].split(" — ")[0]
        d = ROOT / folder_name
        d.mkdir(parents=True, exist_ok=True)
        # Write CHECKLIST.md
        out = []
        out.append(f"# {lvl['title']}")
        # Description
        desc = [ln for ln in lvl['desc'] if ln.strip() != ""]
        if desc:
            out.append("")
            out.extend(desc)
        out.append("")
        out.append("## Checklist")
        out.append("")
        for p in lvl["projects"]:
            out.append(f"- [ ] {p['num']}. {p['title']}")
            # Nested bullets for details if present
            det = p["details"]
            # Only add bullets for non-empty items
            if any(det.values()):
                if det.get("what"):
                    out.append(f"  - What you build: {det['what']}")
                if det.get("skills"):
                    out.append(f"  - Skills: {det['skills']}")
                if det.get("milestones"):
                    out.append(f"  - Milestones: {det['milestones']}")
                if det.get("stretch"):
                    out.append(f"  - Stretch goals: {det['stretch']}")
            out.append("")
        (d / "CHECKLIST.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

def insert_checklists_into_main(lines, levels):
    # Build map from level header index to inserted checklist text
    new_lines = []
    i = 0
    n = len(lines)
    level_idx = 0
    while i < n:
        m = level_header_re.match(lines[i])
        if not m:
            new_lines.append(lines[i])
            i += 1
            continue
        # At a level header
        lvl = levels[level_idx]
        new_lines.append(lines[i])  # the level header line
        i += 1
        # Copy description lines, but check if a Checklist already exists before first project
        desc_buf = []
        while i < n and not lines[i].startswith("### ") and not level_header_re.match(lines[i]):
            desc_buf.append(lines[i])
            i += 1
        # Determine if checklist already present
        has_checklist = any("Checklist" in ln for ln in desc_buf[:10])
        new_lines.extend(desc_buf)
        if not has_checklist:
            # Insert checklist summary for this level
            new_lines.append("")
            new_lines.append("#### Checklist")
            for p in lvl["projects"]:
                new_lines.append(f"- [ ] {p['num']}. {p['title']}")
            new_lines.append("")
        # Continue copying until next level or EOF
        while i < n and not level_header_re.match(lines[i]):
            new_lines.append(lines[i])
            i += 1
        level_idx += 1
    return new_lines

def main():
    lines = load_lines()
    levels = parse_levels(lines)
    if not levels:
        raise SystemExit("No levels found; aborting.")

    # 1) Create per-level folders and CHECKLIST.md files
    ensure_level_folders(levels)

    # 2) Insert per-level checklist summaries into the main roadmap
    updated = insert_checklists_into_main(lines, levels)
    ROADMAP.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

