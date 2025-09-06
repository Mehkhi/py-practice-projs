#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[1]
LEVEL_DIRS = [ROOT / "Levels" / f"Level {n}" for n in (2, 3, 4, 5)]

RE_FEATURE = re.compile(r"^- \*\*(?P<title>.+?)\*\*\s+—\s+\*\*Difficulty\s+(?P<diff>\d+/5)\*\*\s*$")
# Accept both ### and #### for subheadings
RE_SUBHEAD_REQ = re.compile(r"^#{3,4}\s+Required Features")
RE_SUBHEAD_BONUS = re.compile(r"^#{3,4}\s+Bonus Features")
RE_TOP_HEADING = re.compile(r"^###\s+\d+\)\s+")  # Level 2-5 sections use ### N) Title


def parse_spec(spec_path: Path) -> Tuple[str, List[dict], List[dict]]:
    title = spec_path.parent.name
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    section = None
    features_req: List[dict] = []
    features_bonus: List[dict] = []
    current = None
    i = 0
    found_req = False
    found_bonus = False
    while i < len(lines):
        line = lines[i]
        if RE_SUBHEAD_REQ.match(line):
            if found_req:
                break
            section = "req"
            found_req = True
            i += 1
            continue
        if RE_SUBHEAD_BONUS.match(line):
            if found_bonus:
                break
            section = "bonus"
            found_bonus = True
            i += 1
            continue
        if (found_req or found_bonus) and RE_TOP_HEADING.match(line):
            break

        m = RE_FEATURE.match(line)
        if m and section in ("req", "bonus"):
            if current is not None:
                (features_req if current["section"] == "req" else features_bonus).append(current)
            current = {
                "section": section,
                "title": m.group("title").strip(),
                "difficulty": m.group("diff").strip(),
                "accept": [],
            }
            i += 1
            while i < len(lines):
                l2 = lines[i]
                if RE_FEATURE.match(l2) or RE_SUBHEAD_REQ.match(l2) or RE_SUBHEAD_BONUS.match(l2):
                    i -= 1
                    break
                if l2.strip().startswith("- **Acceptance criteria:**"):
                    j = i + 1
                    while j < len(lines):
                        l3 = lines[j]
                        t3 = l3.strip()
                        if t3.startswith("- **") and "— **Difficulty" in t3:
                            break
                        if t3.startswith("- "):
                            if not t3.lower().startswith("- **what it teaches**") and not t3.lower().startswith("- **acceptance criteria**"):
                                current["accept"].append(re.sub(r"^\s*-\s*", "", l3).strip())
                            j += 1
                            continue
                        if not t3:
                            j += 1
                            continue
                        break
                    i = j - 1
                i += 1
        i += 1

    if current is not None:
        (features_req if current["section"] == "req" else features_bonus).append(current)

    return title, features_req, features_bonus


def write_checklist(project_dir: Path, title: str, req: List[dict], bonus: List[dict]) -> None:
    out = []
    out.append(f"# Checklist — {title}")
    out.append("")

    out.append("## Implementation Order")
    for f in req:
        out.append(f"- [ ] {f['title']} ({f['difficulty']})")
    out.append("")

    out.append("## Tasks")
    out.append("")
    for f in req:
        out.append(f"- [ ] {f['title']} ({f['difficulty']})")
        for acc in f.get("accept", []):
            out.append(f"  - [ ] {acc}")
        out.append("")

    if bonus:
        out.append("## Bonus")
        out.append("")
        for f in bonus:
            out.append(f"- [ ] {f['title']} ({f['difficulty']})")
            for acc in f.get("accept", []):
                out.append(f"  - [ ] {acc}")
            out.append("")

    (project_dir / "CHECKLIST.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    for level_dir in LEVEL_DIRS:
        projects = sorted([p for p in level_dir.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)])
        for pdir in projects:
            spec = pdir / "SPEC.md"
            if not spec.exists():
                continue
            title, req, bonus = parse_spec(spec)
            write_checklist(pdir, title, req, bonus)
            print(f"Wrote checklist: {pdir.relative_to(ROOT)}/CHECKLIST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
