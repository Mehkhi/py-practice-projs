### 21) Async DB Layer
**What you’re building:** Async SQLAlchemy/SQLModel with pools and resilience.
**Core skills:** Async engines, transactions, pooling, circuit breakers.

#### Required Features
- **R1. Async engine & sessions** — **Difficulty 2/5**
  - **Teaches:** Connection lifecycles; pool sizing/timeouts.
  - **Acceptance:** Queries run concurrently; pool metrics logged.
- **R2. Transactions** — **Difficulty 2/5**
  - **Teaches:** `async with` patterns; retries on deadlocks.
  - **Acceptance:** Atomicity verified under fault injection.
- **R3. Circuit breaker** — **Difficulty 3/5**
  - **Teaches:** Open/half‑open/closed states; fallback.
  - **Acceptance:** Breaker opens on failures; recovers after cooldown.
- **R4. Read/write split** — **Difficulty 3/5**
  - **Teaches:** Replica routing; consistency semantics.
  - **Acceptance:** Reads hit replicas; writes are consistent; lag monitored.

#### Bonus Features
- **B1. Statement caching** — **Difficulty 2/5**
  - **Teaches:** Prepared statement reuse.
  - **Acceptance:** Reduced latency on repeated queries.
- **B2. Tenant scoping** — **Difficulty 2/5**
  - **Teaches:** Session context for tenant IDs.
  - **Acceptance:** Queries auto‑filter by tenant context.
- **B3. Observability** — **Difficulty 2/5**
  - **Teaches:** Query traces; slow query logging.
  - **Acceptance:** p95/p99 query times charted.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
