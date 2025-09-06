#!/usr/bin/env python3
"""
Split Level 5 detailed spec sections (appended to Levels/Level 5/CHECKLIST.md)
into per-project SPEC.md files and create corresponding project folders.

Assumptions:
- Sections start with headings like: "### <num>) <Title>"
- Capture content from that heading until the next matching heading or EOF.
- Output path: Levels/Level 5/<num-padded>-<slug>/SPEC.md

Idempotent: SPEC.md files are overwritten.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


RE_SECTION = re.compile(r"^###\s*(?P<num>\d{1,2})\)\s*(?P<title>.+?)\s*$")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\u2012\u2013\u2014\u2212]", "-", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def split_specs(src_path: Path, out_dir: Path) -> int:
    lines = src_path.read_text(encoding="utf-8").splitlines()

    sections: list[tuple[str, str, list[str]]] = []
    current: tuple[str, str, list[str]] | None = None

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
        print("No Level 5 project sections found (### <num>) <Title>).")
        return 0

    wrote = 0
    for num, title, content_lines in sections:
        folder = out_dir / f"{int(num):02d}-{slugify(title)}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SPEC.md").write_text("\n".join(content_lines).rstrip() + "\n", encoding="utf-8")
        wrote += 1
    return wrote


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[1]
    src_path = root / "Levels" / "Level 5" / "CHECKLIST.md"
    if not src_path.exists():
        print(f"Source file not found: {src_path}", file=sys.stderr)
        return 1
    out_dir = src_path.parent
    count = split_specs(src_path, out_dir)
    print(f"Wrote {count} Level 5 SPEC.md files under: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


