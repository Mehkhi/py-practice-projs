### 1) Event‑Sourced System (CQRS)
**What you’re building:** Command/write model emits events; read model projects queryable views.
**Core skills:** Domain modeling, event stores, projections, idempotency, snapshots.

#### Required Features
- **R1. Append‑only event store API** — **Difficulty 4/5**
  - **What it teaches:**
    - Stream IDs, optimistic concurrency (`expected_version`), global ordering.
    - Idempotency keys and dedupe on retry.
    - Serialization/versioning of event payloads.
  - **Acceptance criteria:**
    - Concurrent appends detect version conflicts; retries with idempotency key do not duplicate.
    - Event schema versions tracked; upcasters supported.

- **R2. Command handlers & aggregates** — **Difficulty 4/5**
  - **What it teaches:**
    - Aggregate invariants, precondition checks, pure decision logic.
    - Separating command → events from applying events to state.
  - **Acceptance criteria:**
    - Invariant‑violating commands rejected with domain errors.
    - Aggregate state rebuilt from events deterministically.

- **R3. Projections & read models** — **Difficulty 3/5**
  - **What it teaches:**
    - At‑least‑once projection runners, idempotent handlers, checkpointing.
    - Handling out‑of‑order or duplicate events.
  - **Acceptance criteria:**
    - Full rebuild from empty DB produces consistent read model.
    - Projection lag metric exported; resume works after crash.

- **R4. Snapshots & replay performance** — **Difficulty 3/5**
  - **What it teaches:**
    - Snapshot intervals, compaction, and trade‑offs.
    - Replay time budgeting and profiling.
  - **Acceptance criteria:**
    - Rebuild within target (e.g., < N seconds for M events) with snapshots enabled.
    - Snapshot integrity verified by checksum or schema version.

#### Bonus Features
- **B1. Multi‑tenant streams** — **Difficulty 3/5**
  - **Teaches:** Tenant isolation (prefixes/DBs), quota limits.
  - **Acceptance:** Cross‑tenant reads/writes blocked; quotas enforced.
- **B2. GDPR deletion/redaction** — **Difficulty 4/5**
  - **Teaches:** Redaction events, rewrite strategies, audit trails.
  - **Acceptance:** PII removed from projections and future rebuilds; audit entry created.
- **B3. Outbox + subscriptions** — **Difficulty 3/5**
  - **Teaches:** Transactional outbox pattern for integration events.
  - **Acceptance:** Downstream receives each event once; retries are idempotent.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
