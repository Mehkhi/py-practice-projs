# Checklist — 08-feature-store-for-ml

## Implementation Order
- [ ] R1. Feature registry & schemas (3/5)
- [ ] R2. Point‑in‑time join (4/5)
- [ ] R3. Materialization jobs (batch/stream) (3/5)
- [ ] R4. Serving API + lineage (3/5)

## Tasks

- [ ] R1. Feature registry & schemas (3/5)
  - [ ] Registry validated; schema evolution tested.

- [ ] R2. Point‑in‑time join (4/5)
  - [ ] Training sets pass leakage checks; unit tests verify PIT logic.

- [ ] R3. Materialization jobs (batch/stream) (3/5)
  - [ ] Online values within freshness SLA; lag metric exported.

- [ ] R4. Serving API + lineage (3/5)
  - [ ] p95 latency ≤ target; lineage query returns producers/consumers.

## Bonus

- [ ] B1. Streaming features (4/5)

- [ ] B2. Drift detection (3/5)

- [ ] B3. Access control per feature (3/5)
