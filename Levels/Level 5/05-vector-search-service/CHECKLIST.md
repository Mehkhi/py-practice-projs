# Checklist — 05-vector-search-service

## Implementation Order
- [ ] R1. Embedding pipeline & batching (3/5)
- [ ] R2. ANN index (IVF/HNSW) (3/5)
- [ ] R3. Query API & filters (3/5)
- [ ] R4. Evaluation (recall@k & SLOs) (3/5)

## Tasks

- [ ] R1. Embedding pipeline & batching (3/5)
  - [ ] Throughput and latency documented; deterministic embeddings across runs.

- [ ] R2. ANN index (IVF/HNSW) (3/5)
  - [ ] Build time and memory measured; recall target configured.

- [ ] R3. Query API & filters (3/5)
  - [ ] API returns top‑k with scores and metadata; filters reduce candidates.

- [ ] R4. Evaluation (recall@k & SLOs) (3/5)
  - [ ] Meets recall@k ≥ target and p95 latency ≤ budget.

## Bonus

- [ ] B1. Hybrid BM25 + vector rerank (4/5)

- [ ] B2. Streaming upserts (3/5)

- [ ] B3. Multi‑tenant isolation (3/5)
