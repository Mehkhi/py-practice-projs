### 16) Retry/Backoff Library
**What you’re building:** Robust retries with jitter and circuit breaking.
**Core skills:** Decorators, exceptions, policies, packaging.

#### Required Features
- **R1. Policy config & decorators** — **Difficulty 2/5**
  - **What it teaches:**
    - Retry strategies (const/expo/jitter), max attempts, timeouts.
  - **Acceptance criteria:**
    - Unit tests for policies; context carries attempt count.

- **R2. Error taxonomy** — **Difficulty 2/5**
  - **What it teaches:**
    - Retryable/non‑retryable classes; predicates.
  - **Acceptance criteria:**
    - Non‑retryable errors bypass retries with clear result.

- **R3. Circuit breaker** — **Difficulty 3/5**
  - **What it teaches:**
    - Open/half‑open/closed states; success thresholds.
  - **Acceptance criteria:**
    - Breaker trips and recovers per policy with metrics.

- **R4. Metrics & docs** — **Difficulty 2/5**
  - **What it teaches:**
    - Built‑in logging/metrics; README examples.
  - **Acceptance criteria:**
    - Examples runnable; metrics exported.

#### Bonus Features
- **B1. Async support** — **Difficulty 2/5**
  - **Teaches:** Async decorators; cancellation safety.
  - **Acceptance:** Works with async call sites.
- **B2. PyPI release & semantic versioning** — **Difficulty 2/5**
  - **Teaches:** Build/publish; release automation.
  - **Acceptance:** Package installable; releases tagged.
- **B3. Context propagation** — **Difficulty 2/5**
  - **Teaches:** Passing correlation IDs.
  - **Acceptance:** Logs include request IDs through retries.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
