#!/usr/bin/env python3
"""
Split Level 1 master spec (Level1-Checklist-Spec-Sheets-v2.md) into per-project SPEC.md files
and create corresponding project folders under Level 1/ using normalized project names.

Rules:
- A project section starts at headings like: "## <seq>. <project_number>. <Project Name>"
- Capture content from that heading until the next matching heading or end of file.
- Create folder: Level 1/<project_number>-<slug>
- Write file: Level 1/<project_number>-<slug>/SPEC.md with the captured section (preserve markdown).

This script is idempotent: existing SPEC.md files will be overwritten by default.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


RE_SECTION = re.compile(r"^##\s*\d+\.\s*(?P<num>\d+)\.\s*(?P<title>.+)$")


def slugify(text: str) -> str:
    text = text.strip().lower()
    # Replace unicode dashes with hyphen
    text = re.sub(r"[\u2012\u2013\u2014\u2212]", "-", text)
    # Remove parentheses content for compact folder names
    text = re.sub(r"\([^)]*\)", "", text)
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def split_specs(spec_path: Path, level_dir: Path) -> int:
    lines = spec_path.read_text(encoding="utf-8").splitlines()

    sections: list[tuple[str, str, list[str]]] = []  # (num, title, content_lines)
    current = None

    for line in lines:
        m = RE_SECTION.match(line)
        if m:
            if current is not None:
                sections.append(current)
            num = m.group("num").strip()
            title = m.group("title").strip()
            current = (num, title, [line])
        else:
            if current is not None:
                current[2].append(line)

    if current is not None:
        sections.append(current)

    if not sections:
        print("No project sections found. Nothing to do.")
        return 0

    created = 0
    for num, title, content_lines in sections:
        folder_name = f"{int(num):02d}-{slugify(title)}"
        project_dir = level_dir / folder_name
        project_dir.mkdir(parents=True, exist_ok=True)

        spec_out = project_dir / "SPEC.md"
        spec_out.write_text("\n".join(content_lines).rstrip() + "\n", encoding="utf-8")
        created += 1

    return created


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[1]
    level_dir = root / "Level 1"
    spec_path = level_dir / "Level1-Checklist-Spec-Sheets-v2.md"

    if not spec_path.exists():
        print(f"Spec file not found: {spec_path}", file=sys.stderr)
        return 1

    count = split_specs(spec_path, level_dir)
    print(f"Wrote {count} project SPEC.md files under: {level_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


