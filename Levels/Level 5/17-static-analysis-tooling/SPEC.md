### 17) Static Analysis Tooling
**What you’re building:** Analyze Python AST to enforce org rules.
**Core skills:** `ast` module, visitors, autofixes, CI.

#### Required Features
- **R1. Rule engine & config** — **Difficulty 3/5**
  - **What it teaches:**
    - Rule registration, config schema, per‑repo overrides.
  - **Acceptance criteria:**
    - Rules toggleable; config validated with helpful errors.

- **R2. AST visitors & diagnostics** — **Difficulty 3/5**
  - **What it teaches:**
    - Traversals, locations, quick fixes.
  - **Acceptance criteria:**
    - Diagnostics precise with file:line:col; autofix suggestions present.

- **R3. Autofixers** — **Difficulty 3/5**
  - **What it teaches:**
    - Safe code mods; formatting preservation.
  - **Acceptance criteria:**
    - Fixes apply cleanly; tests prevent regressions.

- **R4. CI integration & SARIF** — **Difficulty 2/5**
  - **What it teaches:**
    - PR annotations; SARIF upload for code scanning.
  - **Acceptance criteria:**
    - CI shows inline annotations; SARIF consumed by platform.

#### Bonus Features
- **B1. LSP plugin** — **Difficulty 3/5**
  - **Teaches:** Language server hooks.
  - **Acceptance:** Editor diagnostics live as you type.
- **B2. Performance (parallel)** — **Difficulty 2/5**
  - **Teaches:** File sharding; caching.
  - **Acceptance:** Speed on large repos documented.
- **B3. Suppression workflow** — **Difficulty 2/5**
  - **Teaches:** Allow‑lists and expiry.
  - **Acceptance:** Suppressions expire and re‑open issues.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
