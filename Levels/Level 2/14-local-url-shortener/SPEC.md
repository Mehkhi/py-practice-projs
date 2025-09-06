### 14) Local URL Shortener
**What you’re building:** Map short codes to URLs and open them.
**Core skills:** hashing, JSON store, input validation.

#### Required Features
- **R1. Short code generation** — **Difficulty 2/5**
  - **What it teaches:** Hash→base62, collision checks.
  - **Acceptance criteria:** Codes unique within store.

- **R2. URL validation & normalization** — **Difficulty 2/5**
  - **What it teaches:** Scheme checks, punycode/IDN basics, safe redirects.
  - **Acceptance criteria:** Invalid URLs rejected with reason.

- **R3. JSON persistence** — **Difficulty 1/5**
  - **What it teaches:** Durable writes and backups.
  - **Acceptance criteria:** Store survives restarts; backup file available.

- **R4. Open in browser** — **Difficulty 1/5**
  - **What it teaches:** `webbrowser` module usage.
  - **Acceptance criteria:** `open <code>` launches default browser.

#### Bonus Features
- **B1. Custom aliases** — **Difficulty 2/5**
  - **What it teaches:** Reserved names; conflict resolution.
  - **Acceptance criteria:** User‑provided short codes accepted if available.

- **B2. Click counts & last access** — **Difficulty 2/5**
  - **What it teaches:** Analytics fundamentals.
  - **Acceptance criteria:** Stats command prints counts and recent usage.

- **B3. Tiny Flask front‑end** — **Difficulty 2/5**
  - **What it teaches:** Minimal redirect service.
  - **Acceptance criteria:** `GET /<code>` redirects; 404 on unknown codes.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
