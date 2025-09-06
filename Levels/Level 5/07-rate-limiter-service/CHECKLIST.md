# Checklist — 07-rate-limiter-service

## Implementation Order
- [ ] R1. Token bucket per key (3/5)
- [ ] R2. Sliding window approximation (3/5)
- [ ] R3. Global + per‑key limits (3/5)
- [ ] R4. Skew & audits (2/5)

## Tasks

- [ ] R1. Token bucket per key (3/5)
  - [ ] Correct headers returned (`X‑RateLimit‑Remaining`, `Reset`).

- [ ] R2. Sliding window approximation (3/5)
  - [ ] Dropped/allowed decisions match model within tolerance.

- [ ] R3. Global + per‑key limits (3/5)
  - [ ] No single key can starve others; global cap enforced.

- [ ] R4. Skew & audits (2/5)
  - [ ] Skew tolerance documented; audit entries persisted.

## Bonus

- [ ] B1. Adaptive limits (error budgets) (4/5)

- [ ] B2. Distributed fairness (3/5)

- [ ] B3. Client SDK (2/5)
