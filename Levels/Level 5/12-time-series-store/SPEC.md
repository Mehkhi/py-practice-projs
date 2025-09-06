### 12) Time‑Series Store
**What you’re building:** Write‑optimized TSDB with compression and rollups.
**Core skills:** Columnar storage, delta encoding, downsampling, query engine.

#### Required Features
- **R1. Write path & segments** — **Difficulty 3/5**
  - **What it teaches:**
    - Segment files, indexes, compression (delta‑of‑delta).
  - **Acceptance criteria:**
    - Ingest meets throughput target; segments closed per policy.

- **R2. Downsampling & retention** — **Difficulty 3/5**
  - **What it teaches:**
    - Aggregate rollups; TTL deletion.
  - **Acceptance criteria:**
    - Queries transparently hit rolled‑up data; retention enforced.

- **R3. Query engine (range/agg)** — **Difficulty 3/5**
  - **What it teaches:**
    - Range scans; tag filters; group‑by.
  - **Acceptance criteria:**
    - p95 query latency ≤ budget on N series.

- **R4. Cardinality guard** — **Difficulty 3/5**
  - **What it teaches:**
    - Label cardinality control; quotas.
  - **Acceptance criteria:**
    - High‑cardinality write blocked with clear error.

#### Bonus Features
- **B1. Bitmap/roaring indexes** — **Difficulty 3/5**
  - **Teaches:** Fast set ops for tag filters.
  - **Acceptance:** Query speedup vs naive indexes.
- **B2. Compaction scheduler** — **Difficulty 3/5**
  - **Teaches:** Background merges; throttling.
  - **Acceptance:** Jittered compactions; minimal read amplification.
- **B3. Sparse storage for NaNs** — **Difficulty 3/5**
  - **Teaches:** Memory savings for sparse series.
  - **Acceptance:** Memory profile improved on sparse datasets.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
