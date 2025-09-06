### 5) Vector Search Service
**What you’re building:** Embed text and serve nearest‑neighbor queries.
**Core skills:** Embeddings, FAISS/ANN, indexing, evaluation, batching.

#### Required Features
- **R1. Embedding pipeline & batching** — **Difficulty 3/5**
  - **What it teaches:**
    - Model selection, normalization, batching for throughput.
  - **Acceptance criteria:**
    - Throughput and latency documented; deterministic embeddings across runs.

- **R2. ANN index (IVF/HNSW)** — **Difficulty 3/5**
  - **What it teaches:**
    - Index choice trade‑offs; M (graph degree), efSearch tuning.
  - **Acceptance criteria:**
    - Build time and memory measured; recall target configured.

- **R3. Query API & filters** — **Difficulty 3/5**
  - **What it teaches:**
    - kNN search, metadata filtering, distance metrics.
  - **Acceptance criteria:**
    - API returns top‑k with scores and metadata; filters reduce candidates.

- **R4. Evaluation (recall@k & SLOs)** — **Difficulty 3/5**
  - **What it teaches:**
    - Gold set creation; recall/speed trade‑offs.
  - **Acceptance criteria:**
    - Meets recall@k ≥ target and p95 latency ≤ budget.

#### Bonus Features
- **B1. Hybrid BM25 + vector rerank** — **Difficulty 4/5**
  - **Teaches:** Hybrid retrieval; score blending/reranking.
  - **Acceptance:** Hybrid beats either alone on eval set.
- **B2. Streaming upserts** — **Difficulty 3/5**
  - **Teaches:** Background index updates; tombstones.
  - **Acceptance:** Fresh docs searchable within SLA; no query stalls.
- **B3. Multi‑tenant isolation** — **Difficulty 3/5**
  - **Teaches:** Per‑tenant spaces/shards; quotas.
  - **Acceptance:** Tenants cannot access others’ vectors.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
