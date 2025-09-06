### 6) Image Organizer
**What you’re building:** Sort photos into folders by EXIF date.
**Core skills:** Pillow, `pathlib`, `shutil`, metadata handling.

#### Required Features
- **R1. Read EXIF and derive capture date** — **Difficulty 2/5**
  - **What it teaches:** Robust EXIF parsing; fallback to file mtime.
  - **Acceptance criteria:** Images without EXIF still categorized by mtime.

- **R2. Dry‑run and plan preview** — **Difficulty 1/5**
  - **What it teaches:** Safety in file operations; printing planned moves.
  - **Acceptance criteria:** `--dry-run` moves nothing; shows intended actions.

- **R3. Destination scheme (YYYY/MM/DD)** — **Difficulty 1/5**
  - **What it teaches:** Path construction and directory creation.
  - **Acceptance criteria:** Files end up in the correct dated folders.

- **R4. Duplicate detection by hash** — **Difficulty 2/5**
  - **What it teaches:** Hashing strategies and collision handling.
  - **Acceptance criteria:** Duplicates moved or skipped with a report.

#### Bonus Features
- **B1. Rename to pattern** — **Difficulty 2/5**
  - **What it teaches:** Safe renames; conflict suffixing.
  - **Acceptance criteria:** `YYYY-MM-DD_HH-MM-SS_###.jpg` naming applied.

- **B2. Concurrency (ThreadPool)** — **Difficulty 3/5**
  - **What it teaches:** IO parallelism; progress reporting.
  - **Acceptance criteria:** Speed improves on many files; no data loss.

- **B3. Sidecar JSON manifest** — **Difficulty 2/5**
  - **What it teaches:** Recording move plans for undo.
  - **Acceptance criteria:** Manifest supports rollback of last run.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
