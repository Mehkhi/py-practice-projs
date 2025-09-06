### 21) Config Management
**What you’re building:** Typed settings with environment overrides.
**Core skills:** pydantic/dynaconf, secrets, profiles, validation.

#### Required Features
- **R1. Settings class** — **Difficulty 2/5**
  - **What it teaches:** `BaseSettings`, env var mapping, defaults.
  - **Acceptance criteria:** Values load from `.env` and process env.

- **R2. Profiles (dev/test/prod)** — **Difficulty 2/5**
  - **What it teaches:** Selecting profiles; override precedence.
  - **Acceptance criteria:** `APP_ENV=prod` loads prod overrides.

- **R3. Secrets handling** — **Difficulty 2/5**
  - **What it teaches:** Separate secret files; avoiding commits.
  - **Acceptance criteria:** Secrets not in VCS; missing secrets detected.

- **R4. Validation & helpful errors** — **Difficulty 2/5**
  - **What it teaches:** Custom validators; actionable messages.
  - **Acceptance criteria:** Invalid configs fail fast with clear output.

#### Bonus Features
- **B1. Dynamic reload** — **Difficulty 3/5**
  - **Teaches:** Watching files; hot‑reloading settings safely.
  - **Acceptance:** Changes applied without restart; documented caveats.

- **B2. Secret backends** — **Difficulty 3/5**
  - **Teaches:** Pluggable secret stores (env/JSON/file/OS keychain).
  - **Acceptance:** Backend switch via config only.

- **B3. Config schema export** — **Difficulty 2/5**
  - **Teaches:** Generating JSON Schema for settings.
  - **Acceptance:** Schema file generated; used for validation.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
