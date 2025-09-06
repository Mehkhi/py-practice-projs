### 8) Feature Store for ML
**What you’re building:** Offline/online features with freshness guarantees.
**Core skills:** Point‑in‑time joins, materialization, TTLs, lineage.

#### Required Features
- **R1. Feature registry & schemas** — **Difficulty 3/5**
  - **What it teaches:**
    - Declaring entities, features, sources, ownership.
  - **Acceptance criteria:**
    - Registry validated; schema evolution tested.

- **R2. Point‑in‑time join** — **Difficulty 4/5**
  - **What it teaches:**
    - Preventing leakage; time travel; late‑arriving data.
  - **Acceptance criteria:**
    - Training sets pass leakage checks; unit tests verify PIT logic.

- **R3. Materialization jobs (batch/stream)** — **Difficulty 3/5**
  - **What it teaches:**
    - Backfills, TTL, online store sync.
  - **Acceptance criteria:**
    - Online values within freshness SLA; lag metric exported.

- **R4. Serving API + lineage** — **Difficulty 3/5**
  - **What it teaches:**
    - Low‑latency reads; lineage metadata for audits.
  - **Acceptance criteria:**
    - p95 latency ≤ target; lineage query returns producers/consumers.

#### Bonus Features
- **B1. Streaming features** — **Difficulty 4/5**
  - **Teaches:** Incremental updates; upsert semantics.
  - **Acceptance:** Streamed features update online store in seconds.
- **B2. Drift detection** — **Difficulty 3/5**
  - **Teaches:** PSI/KS tests; alerts.
  - **Acceptance:** Drifts above threshold trigger alerts.
- **B3. Access control per feature** — **Difficulty 3/5**
  - **Teaches:** Row/column‑level ACLs.
  - **Acceptance:** Unauthorized access denied; audited.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
