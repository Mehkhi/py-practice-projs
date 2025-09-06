### 9) PDF Merger/Splitter
**What you’re building:** Merge/split/rotate PDFs from the CLI.
**Core skills:** `pypdf`/PyPDF2, file I/O, `argparse`.

#### Required Features
- **R1. Merge PDFs in order** — **Difficulty 1/5**
  - **What it teaches:** File iteration; output writer basics.
  - **Acceptance criteria:** Output has pages in the given order.

- **R2. Split by ranges** — **Difficulty 2/5**
  - **What it teaches:** Range parsing (e.g., `1-3,7,10-`).
  - **Acceptance criteria:** Produces multiple files with correct ranges.

- **R3. Rotate pages** — **Difficulty 1/5**
  - **What it teaches:** Page transforms in PDF libs.
  - **Acceptance criteria:** Selected pages rotate 90/180 degrees.

- **R4. Metadata copy** — **Difficulty 1/5**
  - **What it teaches:** Reading/writing document info.
  - **Acceptance criteria:** Title/author copied where possible.

#### Bonus Features
- **B1. Bookmarks/TOC** — **Difficulty 3/5**
  - **What it teaches:** Outlines and destinations.
  - **Acceptance criteria:** Top‑level bookmarks created as specified.

- **B2. Password‑protected input** — **Difficulty 2/5**
  - **What it teaches:** Decrypting with provided password.
  - **Acceptance criteria:** Fails gracefully on wrong password.

- **B3. Linearization hint** — **Difficulty 2/5** *(conceptual)*
  - **What it teaches:** Web‑optimized PDFs.
  - **Acceptance criteria:** Documented whether library supports it.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
