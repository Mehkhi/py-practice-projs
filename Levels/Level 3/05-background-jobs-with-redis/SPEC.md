### 5) Background Jobs with Redis
**What you’re building:** Job queue with workers, retries, and status tracking.
**Core skills:** Redis (RQ/ARQ), idempotency, retry, dead‑letter queues.

#### Required Features
- **R1. Enqueue & worker process** — **Difficulty 2/5**
  - **What it teaches:** Producer/consumer model, serialization of job args.
  - **Acceptance criteria:** Jobs enqueued and executed by worker; failures visible.

- **R2. Retries & backoff** — **Difficulty 2/5**
  - **What it teaches:** Retry policies, max attempts, jitter.
  - **Acceptance criteria:** Retryable errors retried N times; non‑retryable go straight to DLQ.

- **R3. Idempotency keys** — **Difficulty 3/5**
  - **What it teaches:** De‑duplication of logically identical jobs.
  - **Acceptance criteria:** Same key within TTL enqueues once; others rejected/logged.

- **R4. Status & DLQ** — **Difficulty 2/5**
  - **What it teaches:** Job lifecycle, querying status, DLQ inspection tools.
  - **Acceptance criteria:** Status endpoints/CLI show queued/running/failed; DLQ export works.

#### Bonus Features
- **B1. Scheduled/delayed jobs** — **Difficulty 2/5**
  - **Teaches:** Time‑based enqueues; cron‑like scheduling basics.
  - **Acceptance:** Jobs fire at scheduled time; missed jobs policy documented.

- **B2. Priority queues** — **Difficulty 2/5**
  - **Teaches:** Separate queues and worker pools per priority.
  - **Acceptance:** High‑priority jobs preempt lower priority.

- **B3. Web dashboard** — **Difficulty 3/5**
  - **Teaches:** Minimal admin UI for queue stats and job details.
  - **Acceptance:** Dashboard shows counts, recent failures, retry actions.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
