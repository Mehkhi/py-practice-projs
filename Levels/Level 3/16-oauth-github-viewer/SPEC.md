### 16) OAuth GitHub Viewer
**What you’re building:** Login via GitHub and list repos/issues.
**Core skills:** OAuth2, sessions, pagination APIs, rate limit handling.

#### Required Features
- **R1. OAuth flow** — **Difficulty 3/5**
  - **What it teaches:** Authorization code grant, state param, CSRF protection.
  - **Acceptance criteria:** Valid callback exchanges code for token; state verified.

- **R2. List repos/issues with pagination** — **Difficulty 2/5**
  - **What it teaches:** Link headers parsing; page traversal.
  - **Acceptance criteria:** All pages visited; UI shows next/prev.

- **R3. Rate‑limit handling & caching** — **Difficulty 2/5**
  - **What it teaches:** Respecting GitHub limits; ETags; conditional requests.
  - **Acceptance criteria:** Hitting rate limit defers calls; UI messages friendly.

- **R4. Session & logout** — **Difficulty 1/5**
  - **What it teaches:** Session lifecycle; token revocation notes.
  - **Acceptance criteria:** Logout clears session; token not stored in plaintext.

#### Bonus Features
- **B1. Star/unstar UI** — **Difficulty 2/5**
  - **Teaches:** Authenticated write operations; optimistic UI.
  - **Acceptance:** Star state toggles and persists.

- **B2. Repo search** — **Difficulty 2/5**
  - **Teaches:** Query endpoints; debounced search.
  - **Acceptance:** Search results ranked; pagination preserved.

- **B3. Offline snapshot** — **Difficulty 2/5**
  - **Teaches:** Export repos/issues to JSON; read later.
  - **Acceptance:** Snapshot downloadable; timestamped.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
