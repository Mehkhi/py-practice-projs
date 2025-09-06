# Agent Handoff: Python Practice Projects Workspace

This document summarizes the structure, scripts, and generated artifacts so a future AI agent (for another language) can reproduce the same workflow.

## What We Did

- Split master spec sheets into per‑project folders with a `SPEC.md` for each project across Levels 1–5.
- Appended detailed spec sections to Level 2–5 top‑level `CHECKLIST.md` files (source-of-truth specs remain in each project’s `SPEC.md`).
- Generated actionable per‑project `CHECKLIST.md` files from each `SPEC.md`:
  - Level 1 checklists include inferred implementation status for Project 1 based on `super-calc.py`.
  - Levels 2–5 checklists list required features and acceptance sub‑tasks in a consistent format.
- Committed all outputs and added repeatable scripts for re‑generation.

## Repository Layout (relevant parts)

```
Levels/
  Level 1/
    01-hello-world-super-calculator/
      SPEC.md
      CHECKLIST.md
      super-calc.py
    02-guess-the-number/
      SPEC.md
      CHECKLIST.md
    ... (through 26)
    CHECKLIST.md                # original Level 1 checklist
    Level1-Checklist-Spec-Sheets-v2.md

  Level 2/ ... Level 5/
    <NN-project-name>/
      SPEC.md
      CHECKLIST.md
    CHECKLIST.md                # Level’s overview with appended detailed specs

scripts/
  split_level1_specs.py         # Split Level 1 master spec into per-project SPEC.md files
  split_level2_specs.py         # Split Level 2 appended detailed specs into per-project SPEC.md files
  split_level3_specs.py         # Split Level 3 appended detailed specs into per-project SPEC.md files
  split_level4_specs.py         # Split Level 4 appended detailed specs into per-project SPEC.md files
  split_level5_specs.py         # Split Level 5 appended detailed specs into per-project SPEC.md files
  generate_level1_checklists.py # Build Level 1 per-project CHECKLIST.md; infers status for Project 1
  generate_checklists_levels_2_to_5.py # Build Levels 2–5 per-project CHECKLIST.md
```

## Scripts and Usage

All scripts are idempotent and overwrite generated files. Run from repo root.

### 1) Split master specs into per‑project SPEC.md

Level 1 (from `Level1-Checklist-Spec-Sheets-v2.md`):
```
python3 scripts/split_level1_specs.py
```

Levels 2–5 (from appended detailed sections in each level’s `CHECKLIST.md`):
```
python3 scripts/split_level2_specs.py
python3 scripts/split_level3_specs.py
python3 scripts/split_level4_specs.py
python3 scripts/split_level5_specs.py
```

### 2) Generate per‑project CHECKLIST.md from SPEC.md

Level 1 (with simple implementation inference for Project 1):
```
python3 scripts/generate_level1_checklists.py
```

Levels 2–5:
```
python3 scripts/generate_checklists_levels_2_to_5.py
```

## Implementation Inference (Level 1 / Project 1)

For `Levels/Level 1/01-hello-world-super-calculator/super-calc.py`, we heuristically detected:
- Parse and validate numeric input — done (loop with `float()` and retry)
- Core operations (add, subtract, multiply, divide) — done
- Division by zero handling — done
- Command normalization and aliases — partial (functions and `ALIASES` exist but not yet wired into CLI flow)

The generated `CHECKLIST.md` reflects this status with `[x]` done, `[-]` partial, `[ ]` todo, and includes acceptance criteria as sub‑tasks.

## Conventions

- Project directories are prefixed with zero‑padded numbers: `NN-project-name`.
- Each project has a `SPEC.md` (source spec) and a generated `CHECKLIST.md` (tasks + acceptance criteria).
- Specs structure is normalized to detect:
  - "Required Features" and "Bonus Features" sections
  - Feature lines like: `- **Title** — **Difficulty X/5**`
  - Acceptance criteria listed as `-` bullet points beneath `- **Acceptance criteria:**`

## What To Do Next (for another language)

1) Port the split and generation scripts or mirror their behavior in your new tooling.
2) Place the new language’s master specs or per‑level appended specs in an analogous layout.
3) Reuse the generation logic to emit `CHECKLIST.md` for each project, mapping acceptance criteria to tasks.
4) Optionally add language‑specific inference to auto‑mark implemented items.

## Notes & Edge Cases

- Heading variations: Levels 2–5 specs use `### N) Title`; the parsers handle both `###` and `####` subheadings for features.
- The generators intentionally stop at the next project section to avoid cross‑project bleed‑through.
- Regeneration overwrites existing generated checklists; commit before regeneration if you want history.

## Quick Reproduce

```
# Split per-level specs (if needed)
python3 scripts/split_level1_specs.py
python3 scripts/split_level2_specs.py
python3 scripts/split_level3_specs.py
python3 scripts/split_level4_specs.py
python3 scripts/split_level5_specs.py

# Generate checklists
python3 scripts/generate_level1_checklists.py
python3 scripts/generate_checklists_levels_2_to_5.py
```

All done — the workspace now has per‑project specs and checklists across Levels 1–5.


