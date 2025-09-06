# Checklist — 02-custom-task-queue

## Implementation Order
- [ ] R1. Broker protocol & message format (3/5)
- [ ] R2. Worker concurrency & dispatcher (3/5)
- [ ] R3. Retries with exponential backoff + jitter (3/5)
- [ ] R4. Idempotency & metrics (3/5)

## Tasks

- [ ] R1. Broker protocol & message format (3/5)
  - [ ] Messages survive broker restart; visibility timeout extends on heartbeat.

- [ ] R2. Worker concurrency & dispatcher (3/5)
  - [ ] Configurable concurrency; draining on SIGTERM without loss.

- [ ] R3. Retries with exponential backoff + jitter (3/5)
  - [ ] Retry policy enforced; DLQ populated with final failure reason.

- [ ] R4. Idempotency & metrics (3/5)
  - [ ] Duplicate job submissions suppressed within TTL; dashboards show depth, inflight, p95.

## Bonus

- [ ] B1. Exactly‑once illusion (4/5)

- [ ] B2. Scheduling (delayed/cron) (3/5)

- [ ] B3. Priority queues (2/5)
