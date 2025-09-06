# Checklist — 11-predictive-caching-layer

## Implementation Order
- [ ] R1. Baseline cache (LRU/TTL) (2/5)
- [ ] R2. Demand model (Markov/bandit) (3/5)
- [ ] R3. Online prefetcher (3/5)
- [ ] R4. Ablation & A/B (3/5)

## Tasks

- [ ] R1. Baseline cache (LRU/TTL) (2/5)
  - [ ] Baseline hit rate established with charts.

- [ ] R2. Demand model (Markov/bandit) (3/5)
  - [ ] Prefetch decisions reproducible; parameters tunable.

- [ ] R3. Online prefetcher (3/5)
  - [ ] Prefetch improves p95 latency without excess cost.

- [ ] R4. Ablation & A/B (3/5)
  - [ ] Predictive policy outperforms baseline with statistical confidence.

## Bonus

- [ ] B1. Cost‑aware decisions (3/5)

- [ ] B2. L2 (Redis) tier (2/5)

- [ ] B3. Offline trainer (3/5)
