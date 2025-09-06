# Checklist — 16-retry-backoff-library

## Implementation Order
- [ ] R1. Policy config & decorators (2/5)
- [ ] R2. Error taxonomy (2/5)
- [ ] R3. Circuit breaker (3/5)
- [ ] R4. Metrics & docs (2/5)

## Tasks

- [ ] R1. Policy config & decorators (2/5)
  - [ ] Unit tests for policies; context carries attempt count.

- [ ] R2. Error taxonomy (2/5)
  - [ ] Non‑retryable errors bypass retries with clear result.

- [ ] R3. Circuit breaker (3/5)
  - [ ] Breaker trips and recovers per policy with metrics.

- [ ] R4. Metrics & docs (2/5)
  - [ ] Examples runnable; metrics exported.

## Bonus

- [ ] B1. Async support (2/5)

- [ ] B2. PyPI release & semantic versioning (2/5)

- [ ] B3. Context propagation (2/5)
