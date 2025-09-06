### 10) Data Lineage & Governance
**What you’re building:** Track datasets, jobs, and dependencies.
**Core skills:** Graph modeling, metadata store, hooks, impact analysis.

#### Required Features
- **R1. Graph model & APIs** — **Difficulty 3/5**
  - **What it teaches:**
    - Datasets, jobs, runs, edges, ownership.
  - **Acceptance criteria:**
    - CRUD works; referential integrity enforced.

- **R2. Ingestion hooks** — **Difficulty 3/5**
  - **What it teaches:**
    - Capturing lineage from pipelines and apps (OpenLineage‑style).
  - **Acceptance criteria:**
    - At least two producers instrumented; lineage visible end‑to‑end.

- **R3. Impact analysis & SLAs** — **Difficulty 3/5**
  - **What it teaches:**
    - Traversals; blast radius estimation; SLA ownership.
  - **Acceptance criteria:**
    - Report shows impacted downstream assets with owners.

- **R4. UI/reporting** — **Difficulty 2/5**
  - **What it teaches:**
    - Graph visualizations; export.
  - **Acceptance criteria:**
    - Web UI renders lineage; CSV/JSON export.

#### Bonus Features
- **B1. Policy checks** — **Difficulty 3/5**
  - **Teaches:** Required owners/tags; PII policies.
  - **Acceptance:** Violations flagged and blocked in CI.
- **B2. OpenLineage integration** — **Difficulty 2/5**
  - **Teaches:** Spec compliance.
  - **Acceptance:** Emits/ingests OL events.
- **B3. Ownership workflows** — **Difficulty 2/5**
  - **Teaches:** Approvals & assignments.
  - **Acceptance:** Ownership gaps resolved via workflow.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
