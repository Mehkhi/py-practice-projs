### 17) Message Broker Workers
**What you’re building:** Producer/consumer with RabbitMQ/Redis and DLQs.
**Core skills:** ack/requeue, dead letters, delivery modes, idempotency.

#### Required Features
- **R1. Producer & durable queues** — **Difficulty 2/5**
  - **Teaches:** Durability, confirm selects, publisher confirms.
  - **Acceptance:** Messages persisted; confirms logged.
- **R2. Consumers & acks** — **Difficulty 2/5**
  - **Teaches:** Manual acks; redelivery; prefetch tuning.
  - **Acceptance:** Prefetch improves throughput without starvation.
- **R3. DLQ routing** — **Difficulty 2/5**
  - **Teaches:** Dead lettering on reject/ttl.
  - **Acceptance:** Poison messages route to DLQ with reason tag.
- **R4. Idempotent handlers** — **Difficulty 3/5**
  - **Teaches:** De‑dupe keys; exactly‑once illusions.
  - **Acceptance:** Retries don’t double‑process side effects.

#### Bonus Features
- **B1. Priority & delayed queues** — **Difficulty 3/5**
  - **Teaches:** Per‑message priority; delayed exchange.
  - **Acceptance:** High‑priority items drain first; delays honored.
- **B2. Retry topology** — **Difficulty 2/5**
  - **Teaches:** Retry exchanges with increasing TTLs.
  - **Acceptance:** Backoff via multiple queues works.
- **B3. Monitoring dashboard** — **Difficulty 2/5**
  - **Teaches:** Queue depth and rates.
  - **Acceptance:** Dashboard shows backlog, rates, errors.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
