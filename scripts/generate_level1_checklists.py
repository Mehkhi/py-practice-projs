#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[1]
LEVEL1_DIR = ROOT / "Levels" / "Level 1"

RE_FEATURE = re.compile(r"^- \*\*(?P<title>.+?)\*\*\s+—\s+\*\*Difficulty\s+(?P<diff>\d+/5)\*\*\s*$")
RE_SUBHEAD_REQ = re.compile(r"^###\s+Required Features")
RE_SUBHEAD_BONUS = re.compile(r"^###\s+Bonus Features")
RE_TOP_HEADING = re.compile(r"^##\s+\d+\.")


def parse_spec(spec_path: Path) -> Tuple[str, List[dict], List[dict]]:
    title = spec_path.parent.name
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    section = None  # None|"req"|"bonus"
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
                break  # Only take the first Required Features block
            section = "req"
            found_req = True
            i += 1
            continue
        if RE_SUBHEAD_BONUS.match(line):
            if found_bonus:
                break  # Only take the first Bonus Features block
            section = "bonus"
            found_bonus = True
            i += 1
            continue
        # Stop parsing once we move to the next top-level numbered section after capturing some features
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
            # scan following bullet points for Acceptance criteria block
            i += 1
            while i < len(lines):
                l2 = lines[i]
                if RE_FEATURE.match(l2) or RE_SUBHEAD_REQ.match(l2) or RE_SUBHEAD_BONUS.match(l2):
                    i -= 1  # step back one so outer loop re-processes this heading
                    break
                if l2.strip().startswith("- **Acceptance criteria:**"):
                    # collect subsequent indented list items starting with "- "
                    j = i + 1
                    while j < len(lines):
                        l3 = lines[j]
                        t3 = l3.strip()
                        # stop if we hit another feature-looking bullet (even if indented)
                        if t3.startswith("- **") and "— **Difficulty" in t3:
                            break
                        if t3.startswith("- "):
                            # only keep acceptance bullets, skip headings like "**What it teaches:**"
                            if not t3.lower().startswith("- **what it teaches**") and not t3.lower().startswith("- **acceptance criteria**"):
                                current["accept"].append(re.sub(r"^\s*-\s*", "", l3).strip())
                            j += 1
                            continue
                        if not l3.strip():
                            j += 1
                            continue
                        # stop at next non-list line
                        break
                    i = j - 1
                i += 1
        i += 1

    if current is not None:
        (features_req if current["section"] == "req" else features_bonus).append(current)

    return title, features_req, features_bonus


def infer_impl_status_project1(project_dir: Path, features: List[dict]) -> dict:
    """Return mapping of feature title -> status ('done'|'todo'|'partial') based on super-calc.py."""
    status = {f["title"].lower(): "todo" for f in features}
    code = (project_dir / "super-calc.py").read_text(encoding="utf-8") if (project_dir / "super-calc.py").exists() else ""

    def has(pattern: str) -> bool:
        return re.search(pattern, code) is not None

    # Heuristics
    if has(r"def\s+read_number\(\w+\):") and has(r"while\s+True:") and has(r"float\("):
        status["parse and validate numeric input"] = "done"

    if has(r"\ba\s*\+\s*b\b") and has(r"\ba\s*-\s*b\b") and has(r"\ba\s*\*\s*b\b") and has(r"\ba\s*/\s*b\b"):
        status["core operations: add, subtract, multiply, divide"] = "done"

    if has(r"if\s+b\s*!=\s*0") and has(r"division by zero"):
        status["division by zero handling"] = "done"

    if has(r"ALIASES\s*=\s*\{") and has(r"def\s+normalize_command\("):
        # present but not wired into CLI
        status["command normalization and aliases"] = "partial"

    return status


def write_checklist(project_dir: Path, title: str, req: List[dict], bonus: List[dict], impl_status: dict | None) -> None:
    out = []
    out.append(f"# Checklist — {title}")
    out.append("")
    # Implementation order: unimplemented required first, then partial, then done, then bonus
    def order_key(f: dict) -> Tuple[int, str]:
        key = f["title"].lower()
        st = impl_status.get(key, "todo") if impl_status else "todo"
        rank = {"todo": 0, "partial": 1, "done": 2}.get(st, 0)
        return (rank, key)

    ordered_req = sorted(req, key=order_key)

    out.append("## Implementation Order")
    for f in ordered_req:
        key = f["title"].lower()
        st = impl_status.get(key, "todo") if impl_status else "todo"
        prefix = {"done": "[x]", "partial": "[-]", "todo": "[ ]"}[st]
        out.append(f"- {prefix} {f['title']} ({f['difficulty']})")
    out.append("")

    out.append("## Tasks")
    out.append("")
    for f in ordered_req:
        key = f["title"].lower()
        st = impl_status.get(key, "todo") if impl_status else "todo"
        prefix = {"done": "[x]", "partial": "[-]", "todo": "[ ]"}[st]
        out.append(f"- {prefix} {f['title']} ({f['difficulty']})")
        for acc in f.get("accept", []):
            sub_prefix = "[x]" if st == "done" else "[ ]"
            out.append(f"  - {sub_prefix} {acc}")
        out.append("")

    if bonus:
        out.append("## Bonus")
        out.append("")
        for f in bonus:
            out.append(f"- [ ] {f['title']} ({f['difficulty']})")
            for acc in f.get("accept", []):
                out.append(f"  - [ ] {acc}")
            out.append("")

    checklist_path = project_dir / "CHECKLIST.md"
    checklist_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    projects = sorted([p for p in LEVEL1_DIR.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)])
    for pdir in projects:
        spec = pdir / "SPEC.md"
        if not spec.exists():
            continue
        title, req, bonus = parse_spec(spec)
        impl_status = None
        if pdir.name.startswith("01-"):
            impl_status = infer_impl_status_project1(pdir, req)
        write_checklist(pdir, title, req, bonus, impl_status)
        print(f"Wrote checklist: {pdir.relative_to(ROOT)}/CHECKLIST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


