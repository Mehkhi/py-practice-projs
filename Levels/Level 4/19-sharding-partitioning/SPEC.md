### 19) Sharding & Partitioning
**What you’re building:** Distribute data by key across partitions/DBs.
**Core skills:** Hashing, routing, rebalancing, locality vs balance.

#### Required Features
- **R1. Shard function** — **Difficulty 2/5**
  - **Teaches:** Hash mod N; consistent hashing.
  - **Acceptance:** Keys map evenly; collision tests.
- **R2. Router & connection pools** — **Difficulty 3/5**
  - **Teaches:** Routing reads/writes; pool sizing.
  - **Acceptance:** Queries routed to correct shard; failover documented.
- **R3. Rebalancing tool** — **Difficulty 3/5**
  - **Teaches:** Moving ranges/keys online.
  - **Acceptance:** Data moves without downtime in demo.
- **R4. Metrics & hot‑key detection** — **Difficulty 2/5**
  - **Teaches:** Skew detection and mitigation.
  - **Acceptance:** Hot keys identified; mitigation plan applied.

#### Bonus Features
- **B1. Range sharding** — **Difficulty 3/5**
  - **Teaches:** Range splits/merges.
  - **Acceptance:** Split/merge with routing table update.
- **B2. Read replicas** — **Difficulty 2/5**
  - **Teaches:** Replica routing; lag metrics.
  - **Acceptance:** Stale reads flagged; lag alerts.
- **B3. Global secondary index (concept)** — **Difficulty 3/5**
  - **Teaches:** Maintaining cross‑shard indexes.
  - **Acceptance:** Demo with eventual consistency.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
