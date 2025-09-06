### 7) Rate Limiter Service
**What you’re building:** Distributed token bucket and sliding window limits.
**Core skills:** Redis Lua/atomics, fairness, headers, skew.

#### Required Features
- **R1. Token bucket per key** — **Difficulty 3/5**
  - **What it teaches:**
    - Atomic refill/consume with Lua; burst capacity.
  - **Acceptance criteria:**
    - Correct headers returned (`X‑RateLimit‑Remaining`, `Reset`).

- **R2. Sliding window approximation** — **Difficulty 3/5**
  - **What it teaches:**
    - Fixed vs sliding window; memory/time trade‑offs.
  - **Acceptance criteria:**
    - Dropped/allowed decisions match model within tolerance.

- **R3. Global + per‑key limits** — **Difficulty 3/5**
  - **What it teaches:**
    - Coordinating multiple limiters; fairness across tenants.
  - **Acceptance criteria:**
    - No single key can starve others; global cap enforced.

- **R4. Skew & audits** — **Difficulty 2/5**
  - **What it teaches:**
    - NTP skew handling; audit logging.
  - **Acceptance criteria:**
    - Skew tolerance documented; audit entries persisted.

#### Bonus Features
- **B1. Adaptive limits (error budgets)** — **Difficulty 4/5**
  - **Teaches:** Burn‑rate feedback to adjust limits.
  - **Acceptance:** Limits tighten/relax based on SLO burn.
- **B2. Distributed fairness** — **Difficulty 3/5**
  - **Teaches:** DRR/weighted fairness.
  - **Acceptance:** Weighted tenants get proportional share.
- **B3. Client SDK** — **Difficulty 2/5**
  - **Teaches:** Client‑side leaky buckets to smooth bursts.
  - **Acceptance:** Fewer 429s under bursty clients.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
