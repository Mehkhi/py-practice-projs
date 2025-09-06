### 24) Image Thumbnailer
**What you’re building:** Create thumbnails and preserve aspect ratio.
**Core skills:** Pillow resize, `pathlib` glob, error handling.

#### Required Features
- **R1. Discover images** — **Difficulty 1/5**
  - **What it teaches:** Glob patterns and extension filters.
  - **Acceptance criteria:** Prints count and sample of discovered files.

- **R2. Resize with aspect** — **Difficulty 2/5**
  - **What it teaches:** Thumbnail vs resize; fit vs fill.
  - **Acceptance criteria:** Output within max bounds; no distortion.

- **R3. Quality settings** — **Difficulty 1/5**
  - **What it teaches:** JPEG quality; PNG optimization.
  - **Acceptance criteria:** Quality flag affects output size visibly.

- **R4. Skip already processed** — **Difficulty 2/5**
  - **What it teaches:** Idempotency via hash/mtime markers.
  - **Acceptance criteria:** Re‑run avoids duplicate work.

#### Bonus Features
- **B1. ThreadPool concurrency** — **Difficulty 3/5**
  - **What it teaches:** IO parallelism and CPU limits.
  - **Acceptance criteria:** Large sets process faster with same results.

- **B2. Respect EXIF orientation** — **Difficulty 2/5**
  - **What it teaches:** Correcting rotation based on metadata.
  - **Acceptance criteria:** Portrait/landscape render correctly.

- **B3. Progressive JPEGs** — **Difficulty 2/5**
  - **What it teaches:** Web‑friendly image encodings.
  - **Acceptance criteria:** Progressive flag produces incremental load.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
