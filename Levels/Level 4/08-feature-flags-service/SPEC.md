### 8) Feature Flags Service
**What you’re building:** Targeted feature toggles with caching and audit.
**Core skills:** RBAC, Redis caching, evaluation rules.

#### Required Features
- **R1. Flag model & API** — **Difficulty 2/5**
  - **Teaches:** Flag states, targeting rules, constraints.
  - **Acceptance:** CRUD for flags; JSON schema documented.
- **R2. Evaluation engine** — **Difficulty 3/5**
  - **Teaches:** Rule evaluation, percentage rollouts, bucketing by user ID.
  - **Acceptance:** Deterministic results for same user; tests for edge cases.
- **R3. Caching & invalidation** — **Difficulty 2/5**
  - **Teaches:** Redis cache; ETags; per‑tenant separation.
  - **Acceptance:** Changes propagate within TTL; metrics on hits/misses.
- **R4. Audit log** — **Difficulty 2/5**
  - **Teaches:** Who/what/when logging; compliance.
  - **Acceptance:** All changes recorded with actor and diff.

#### Bonus Features
- **B1. Targeting DSL** — **Difficulty 4/5**
  - **Teaches:** Expression parser; safe evaluation.
  - **Acceptance:** Complex rules parsed and evaluated predictably.
- **B2. SDKs for clients** — **Difficulty 3/5**
  - **Teaches:** Cached polling; bootstrapping.
  - **Acceptance:** Example app uses SDK; startup fetch cached.
- **B3. Admin UI** — **Difficulty 3/5**
  - **Teaches:** Simple UI for flag edits and audit view.
  - **Acceptance:** Role‑gated UI changes flags and logs events.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
