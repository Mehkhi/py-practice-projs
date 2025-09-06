### 2) Custom Task Queue
**What you’re building:** Celery‑like queue with reliability semantics.
**Core skills:** Broker protocol, ack/retry, visibility timeout, metrics.

#### Required Features
- **R1. Broker protocol & message format** — **Difficulty 3/5**
  - **What it teaches:**
    - Envelope (id, type, args, headers), visibility timeouts, dead lettering.
    - Durable publish and confirm semantics.
  - **Acceptance criteria:**
    - Messages survive broker restart; visibility timeout extends on heartbeat.

- **R2. Worker concurrency & dispatcher** — **Difficulty 3/5**
  - **What it teaches:**
    - Thread/Process/async workers; graceful shutdown; backpressure.
  - **Acceptance criteria:**
    - Configurable concurrency; draining on SIGTERM without loss.

- **R3. Retries with exponential backoff + jitter** — **Difficulty 3/5**
  - **What it teaches:**
    - Retryable vs non‑retryable errors; DLQ thresholds.
  - **Acceptance criteria:**
    - Retry policy enforced; DLQ populated with final failure reason.

- **R4. Idempotency & metrics** — **Difficulty 3/5**
  - **What it teaches:**
    - Idempotency keys and dedupe cache; queue depth/latency metrics.
  - **Acceptance criteria:**
    - Duplicate job submissions suppressed within TTL; dashboards show depth, inflight, p95.

#### Bonus Features
- **B1. Exactly‑once illusion** — **Difficulty 4/5**
  - **Teaches:** Outbox/inbox tables; idempotent side effects.
  - **Acceptance:** Replays do not double‑apply effects.
- **B2. Scheduling (delayed/cron)** — **Difficulty 3/5**
  - **Teaches:** Delayed queues and periodic job registration.
  - **Acceptance:** Jobs fire at intended times; misfire policy documented.
- **B3. Priority queues** — **Difficulty 2/5**
  - **Teaches:** Separate pools; starvation prevention.
  - **Acceptance:** High‑priority jobs preempt lower priority without starvation.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
