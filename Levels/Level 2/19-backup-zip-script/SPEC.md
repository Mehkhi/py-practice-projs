### 19) Backup & Zip Script
**What you’re building:** Zip important folders on a schedule and rotate.
**Core skills:** `zipfile`, `pathlib`, cron docs, logging.

#### Required Features
- **R1. Include/exclude patterns** — **Difficulty 2/5**
  - **What it teaches:** Glob patterns; ignore files; safety.
  - **Acceptance criteria:** Patterns applied; dry‑run prints result set.

- **R2. Create archive** — **Difficulty 1/5**
  - **What it teaches:** Zipping folder trees; compression level.
  - **Acceptance criteria:** Resulting archive opens and matches files.

- **R3. Retention policy** — **Difficulty 2/5**
  - **What it teaches:** Keeping last N or last N days; deletion safety.
  - **Acceptance criteria:** Old archives pruned as configured.

- **R4. Checksums & logs** — **Difficulty 2/5**
  - **What it teaches:** `hashlib` and operation logs for audits.
  - **Acceptance criteria:** Checksums file emitted; run log saved.

#### Bonus Features
- **B1. Incremental backups** — **Difficulty 3/5**
  - **What it teaches:** mtime comparisons; changed files only.
  - **Acceptance criteria:** Deltas computed; full backup on schedule.

- **B2. Email report** — **Difficulty 2/5**
  - **What it teaches:** SMTP integration; success/failure summary.
  - **Acceptance criteria:** Report delivered on completion.

- **B3. Parallel compression** — **Difficulty 3/5**
  - **What it teaches:** Threading; CPU vs IO trade‑offs.
  - **Acceptance criteria:** Large backups run measurably faster.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
