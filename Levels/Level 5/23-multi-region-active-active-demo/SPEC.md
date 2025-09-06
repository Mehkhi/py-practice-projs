### 23) Multi‑Region Active‑Active Demo
**What you’re building:** Two regions with conflict resolution.
**Core skills:** Replication, CRDTs, traffic routing, failover.

#### Required Features
- **R1. Replication strategy** — **Difficulty 4/5**
  - **What it teaches:**
    - Oplog streams vs CRDT types; convergence.
  - **Acceptance criteria:**
    - Regions converge after partitions; conflicts resolved deterministically.

- **R2. Traffic routing** — **Difficulty 3/5**
  - **What it teaches:**
    - Weighted/geo routing; health checks.
  - **Acceptance criteria:**
    - Traffic shifts on fail; sticky sessions handled.

- **R3. Failover drills** — **Difficulty 3/5**
  - **What it teaches:**
    - Runbooks, RTO/RPO validation.
  - **Acceptance criteria:**
    - Drills executed; RTO/RPO met; audit logged.

- **R4. Consistency docs & invariants** — **Difficulty 2/5**
  - **What it teaches:**
    - Read/write models, client expectations.
  - **Acceptance criteria:**
    - Documented invariants with examples and failure modes.

#### Bonus Features
- **B1. Partition simulations** — **Difficulty 3/5**
  - **Teaches:** Nemesis scenarios; chaos in network.
  - **Acceptance:** Outcomes recorded; learnings fed back into design.
- **B2. Vector clocks/lamport clocks** — **Difficulty 3/5**
  - **Teaches:** Causality reasoning.
  - **Acceptance:** Causal ordering shown in examples.
- **B3. Eventually consistent caches** — **Difficulty 2/5**
  - **Teaches:** TTLs, staleness windows.
  - **Acceptance:** Client cache policy documented and tested.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
