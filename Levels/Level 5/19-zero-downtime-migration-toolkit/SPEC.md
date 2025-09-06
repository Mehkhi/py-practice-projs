### 19) Zero‑Downtime Migration Toolkit
**What you’re building:** Plan/apply DB schema/data changes safely.
**Core skills:** Expand‑contract, backfills, dual‑writes, rollback.

#### Required Features
- **R1. Plan generator (expand/contract)** — **Difficulty 3/5**
  - **What it teaches:**
    - Safe ordering, feature flags, shadow columns.
  - **Acceptance criteria:**
    - Plan validates against model diffs; dry‑run available.

- **R2. Backfill jobs** — **Difficulty 3/5**
  - **What it teaches:**
    - Idempotent batch backfills; throttling.
  - **Acceptance criteria:**
    - Backfills resume after failure; progress tracked.

- **R3. Dual‑write and verification** — **Difficulty 3/5**
  - **What it teaches:**
    - Writing old+new paths and comparing.
  - **Acceptance criteria:**
    - Divergence alarms; cutover only when diff=0.

- **R4. Rollback & runbooks** — **Difficulty 2/5**
  - **What it teaches:**
    - Fast rollback and kill‑switches.
  - **Acceptance criteria:**
    - Rollback rehearsed; RTO met.

#### Bonus Features
- **B1. Auto plan from ORM models** — **Difficulty 3/5**
  - **Teaches:** Model introspection.
  - **Acceptance:** Plans generated for common changes.
- **B2. Canary migrations** — **Difficulty 2/5**
  - **Teaches:** Small‑scope testing before global.
  - **Acceptance:** Canary passes gates before full deploy.
- **B3. Analyzers** — **Difficulty 2/5**
  - **Teaches:** Hot table detection; lock risk.
  - **Acceptance:** Warnings produced for risky operations.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
