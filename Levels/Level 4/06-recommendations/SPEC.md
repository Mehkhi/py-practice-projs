### 6) Recommendations (CF)
**What you’re building:** Collaborative filtering recommender (movies/books).
**Core skills:** Pandas, sparse matrices, cosine similarity, evaluation.

#### Required Features
- **R1. Data loading & sparsity handling** — **Difficulty 2/5**
  - **Teaches:** User‑item matrices, implicit zeros, memory.
  - **Acceptance:** Sparse format used; stats printed (density, users/items).
- **R2. Similarity & top‑N** — **Difficulty 3/5**
  - **Teaches:** Cosine sim; nearest neighbors; cold‑start policy.
  - **Acceptance:** Top‑N per user generated; cold‑start documented.
- **R3. Evaluation metrics** — **Difficulty 3/5**
  - **Teaches:** Precision@K, Recall@K, MAP, offline splits.
  - **Acceptance:** Report comparing baselines; seed reproducibility.
- **R4. Serving API** — **Difficulty 2/5**
  - **Teaches:** FastAPI endpoint for recommendations with caching.
  - **Acceptance:** p95 latency target met on sample workload.

#### Bonus Features
- **B1. Implicit feedback (ALS)** — **Difficulty 4/5**
  - **Teaches:** Alternating least squares for implicit data.
  - **Acceptance:** Offline metrics outperform cosine baseline.
- **B2. Hybrid signals** — **Difficulty 3/5**
  - **Teaches:** Content + CF blending.
  - **Acceptance:** Weighted blend improves specific segments.
- **B3. Re‑rankers** — **Difficulty 3/5**
  - **Teaches:** Business rules, diversity/novelty boosts.
  - **Acceptance:** Diversity metrics reported and tunable.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
