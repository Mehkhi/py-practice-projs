### 23) Caching Strategies
**What you’re building:** Local+Redis caches with robust invalidation.
**Core skills:** TTL, LRU, stampede prevention, metrics.

#### Required Features
- **R1. Local (in‑proc) cache** — **Difficulty 2/5**
  - **Teaches:** LRU/TTL; thread safety.
  - **Acceptance:** Cache hit/miss metrics; eviction works.
- **R2. Redis cache** — **Difficulty 2/5**
  - **Teaches:** Serialization formats; memory sizing.
  - **Acceptance:** Keys expire; memory use monitored.
- **R3. Invalidation policies** — **Difficulty 3/5**
  - **Teaches:** Write‑through/back; explicit/implicit busting.
  - **Acceptance:** Cache coherence demonstrated under updates.
- **R4. Stampede prevention** — **Difficulty 3/5**
  - **Teaches:** Single‑flight; soft TTL; jitter.
  - **Acceptance:** Under load, single refresh per key.

#### Bonus Features
- **B1. Hierarchical L1/L2** — **Difficulty 3/5**
  - **Teaches:** Local vs remote trade‑offs.
  - **Acceptance:** Lower latency without stale spikes.
- **B2. Near‑cache for clients** — **Difficulty 2/5**
  - **Teaches:** Client caching with invalidation channel.
  - **Acceptance:** Invalidation messages clear near caches.
- **B3. Metrics & dashboards** — **Difficulty 2/5**
  - **Teaches:** Cache hit rate, age, memory.
  - **Acceptance:** Dashboard shows improvement over baseline.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
