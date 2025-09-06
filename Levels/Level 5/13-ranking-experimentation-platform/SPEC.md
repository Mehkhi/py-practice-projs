### 13) Ranking Experimentation Platform
**What you’re building:** A/B testing for ranking models with metrics pipeline.
**Core skills:** Experiment design, metric logging, stats, guardrails.

#### Required Features
- **R1. Assignment & bucketing** — **Difficulty 3/5**
  - **What it teaches:**
    - Hash‑based stable bucketing; exposure logs.
  - **Acceptance criteria:**
    - No cross‑test contamination; balanced arms.

- **R2. Metrics pipeline** — **Difficulty 3/5**
  - **What it teaches:**
    - Event schema; at‑least‑once ingestion; dedup.
  - **Acceptance criteria:**
    - Metrics computed reproducibly; late events handled.

- **R3. Statistical analysis** — **Difficulty 3/5**
  - **What it teaches:**
    - CUPED/stratification; sequential tests; guardrails.
  - **Acceptance criteria:**
    - Significance and power reported; stop rules implemented.

- **R4. Dashboard & audit** — **Difficulty 2/5**
  - **What it teaches:**
    - Results visualization; approvals.
  - **Acceptance criteria:**
    - Experiment lifecycle tracked with approvals.

#### Bonus Features
- **B1. Switchback tests** — **Difficulty 3/5**
  - **Teaches:** Temporal alternation to reduce network effects.
  - **Acceptance:** Design and analysis documented; used on at least one test.
- **B2. Heterogeneity analysis** — **Difficulty 2/5**
  - **Teaches:** Segment‑level effects.
  - **Acceptance:** Lift by segment charted.
- **B3. Counterfactual evaluation** — **Difficulty 3/5**
  - **Teaches:** IPS/DR estimators.
  - **Acceptance:** Offline estimates compare with online results.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
