### 18) Distributed Locks
**What you’re building:** Protect critical sections with Redis locks.
**Core skills:** Redlock patterns, TTLs, fencing tokens, renewal.

#### Required Features
- **R1. Lock acquisition with TTL** — **Difficulty 2/5**
  - **Teaches:** Race conditions; expirations; contention.
  - **Acceptance:** Exclusive access under contention.
- **R2. Renewal/heartbeat** — **Difficulty 3/5**
  - **Teaches:** Extending TTL during long critical sections.
  - **Acceptance:** Long tasks keep lock; missed heartbeats release.
- **R3. Fencing tokens** — **Difficulty 3/5**
  - **Teaches:** Prevent stale owners after expiry.
  - **Acceptance:** Operations with stale token rejected.
- **R4. Lock contention tests** — **Difficulty 2/5**
  - **Teaches:** Load simulation; fairness.
  - **Acceptance:** Measured fairness and failure modes documented.

#### Bonus Features
- **B1. Lease‑based caches** — **Difficulty 3/5**
  - **Teaches:** Prevent dog‑pile stampede.
  - **Acceptance:** Single writer refreshes cache under load.
- **B2. Multi‑node quorum** — **Difficulty 4/5**
  - **Teaches:** Redlock across nodes; trade‑offs.
  - **Acceptance:** Quorum locks resist single‑node failure.
- **B3. Observability hooks** — **Difficulty 2/5**
  - **Teaches:** Expose lock stats.
  - **Acceptance:** Metrics show acquisition rate/failures.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
