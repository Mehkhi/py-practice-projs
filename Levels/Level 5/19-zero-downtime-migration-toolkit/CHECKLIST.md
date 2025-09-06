# Checklist — 19-zero-downtime-migration-toolkit

## Implementation Order
- [ ] R1. Plan generator (expand/contract) (3/5)
- [ ] R2. Backfill jobs (3/5)
- [ ] R3. Dual‑write and verification (3/5)
- [ ] R4. Rollback & runbooks (2/5)

## Tasks

- [ ] R1. Plan generator (expand/contract) (3/5)
  - [ ] Plan validates against model diffs; dry‑run available.

- [ ] R2. Backfill jobs (3/5)
  - [ ] Backfills resume after failure; progress tracked.

- [ ] R3. Dual‑write and verification (3/5)
  - [ ] Divergence alarms; cutover only when diff=0.

- [ ] R4. Rollback & runbooks (2/5)
  - [ ] Rollback rehearsed; RTO met.

## Bonus

- [ ] B1. Auto plan from ORM models (3/5)

- [ ] B2. Canary migrations (2/5)

- [ ] B3. Analyzers (2/5)
