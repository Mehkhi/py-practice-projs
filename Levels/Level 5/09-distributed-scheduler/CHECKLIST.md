# Checklist — 09-distributed-scheduler

## Implementation Order
- [ ] R1. Leader election & lease (3/5)
- [ ] R2. Cron parser & registry (3/5)
- [ ] R3. Idempotent job execution (3/5)
- [ ] R4. Pause/resume & monitoring (2/5)

## Tasks

- [ ] R1. Leader election & lease (3/5)
  - [ ] Single active leader; takeover on failure within SLA.

- [ ] R2. Cron parser & registry (3/5)
  - [ ] Next‑run times match reference; edge cases (DST) tested.

- [ ] R3. Idempotent job execution (3/5)
  - [ ] No duplicate effects under retries; misfires handled per policy.

- [ ] R4. Pause/resume & monitoring (2/5)
  - [ ] Jobs listable/filterable; pause/resume persists.

## Bonus

- [ ] B1. Sharded schedulers (3/5)

- [ ] B2. Priority scheduling (2/5)

- [ ] B3. History retention & audit (2/5)
