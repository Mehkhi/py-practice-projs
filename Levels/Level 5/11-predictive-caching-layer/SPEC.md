### 11) Predictive Caching Layer
**What you’re building:** Prefetch based on usage patterns with bandits/Markov.
**Core skills:** Telemetry, cache policy, modeling, evaluation.

#### Required Features
- **R1. Baseline cache (LRU/TTL)** — **Difficulty 2/5**
  - **What it teaches:**
    - Hit/miss logging; eviction metrics.
  - **Acceptance criteria:**
    - Baseline hit rate established with charts.

- **R2. Demand model (Markov/bandit)** — **Difficulty 3/5**
  - **What it teaches:**
    - Transition matrices; confidence; exploration vs exploitation.
  - **Acceptance criteria:**
    - Prefetch decisions reproducible; parameters tunable.

- **R3. Online prefetcher** — **Difficulty 3/5**
  - **What it teaches:**
    - Prefetch budget and throttling; cancelation.
  - **Acceptance criteria:**
    - Prefetch improves p95 latency without excess cost.

- **R4. Ablation & A/B** — **Difficulty 3/5**
  - **What it teaches:**
    - Controlled experiments; metrics.
  - **Acceptance criteria:**
    - Predictive policy outperforms baseline with statistical confidence.

#### Bonus Features
- **B1. Cost‑aware decisions** — **Difficulty 3/5**
  - **Teaches:** $/GB, CPU, energy in objective.
  - **Acceptance:** Cost/latency frontier plotted.
- **B2. L2 (Redis) tier** — **Difficulty 2/5**
  - **Teaches:** Multi‑tier caching.
  - **Acceptance:** L1+L2 outperforms L1 only.
- **B3. Offline trainer** — **Difficulty 3/5**
  - **Teaches:** Replay logs; hyperparameter search.
  - **Acceptance:** Trained policy shipped with metadata.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
