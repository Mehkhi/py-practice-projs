### 6) File Upload Service
**What you’re building:** Upload files safely and serve them securely.
**Core skills:** Streaming uploads, MIME checks, secure storage, presigned URLs.

#### Required Features
- **R1. Upload form & streaming** — **Difficulty 2/5**
  - **What it teaches:** Streaming file reads, temp file handling, size limits.
  - **Acceptance criteria:** Large file upload succeeds without OOM; size cap enforced.

- **R2. MIME validation & safe filenames** — **Difficulty 2/5**
  - **What it teaches:** Server‑side content sniffing; path traversal prevention.
  - **Acceptance criteria:** Disallowed types rejected; filenames sanitized.

- **R3. Secure serving** — **Difficulty 2/5**
  - **What it teaches:** Authorization checks, short‑lived URLs, cache headers.
  - **Acceptance criteria:** Private files require auth; `Cache-Control` configured.

- **R4. Virus scan hook** — **Difficulty 2/5**
  - **What it teaches:** Pluggable validation step; quarantine flow.
  - **Acceptance criteria:** Suspicious files held; users notified with next steps.

#### Bonus Features
- **B1. Presigned URL (local emulation)** — **Difficulty 3/5**
  - **Teaches:** Signed URLs, expiry, tamper detection.
  - **Acceptance:** Invalid/expired signatures rejected.

- **B2. Chunked uploads + resume** — **Difficulty 4/5**
  - **Teaches:** Multipart state tracking; idempotent chunk handling.
  - **Acceptance:** Interrupted uploads resume; hash verified on completion.

- **B3. Range requests** — **Difficulty 3/5**
  - **Teaches:** HTTP `Range`/`206 Partial Content` semantics.
  - **Acceptance:** Video scrubbing works; correct headers set.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
