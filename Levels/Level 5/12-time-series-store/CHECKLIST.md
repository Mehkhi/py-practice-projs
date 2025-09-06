# Checklist — 12-time-series-store

## Implementation Order
- [ ] R1. Write path & segments (3/5)
- [ ] R2. Downsampling & retention (3/5)
- [ ] R3. Query engine (range/agg) (3/5)
- [ ] R4. Cardinality guard (3/5)

## Tasks

- [ ] R1. Write path & segments (3/5)
  - [ ] Ingest meets throughput target; segments closed per policy.

- [ ] R2. Downsampling & retention (3/5)
  - [ ] Queries transparently hit rolled‑up data; retention enforced.

- [ ] R3. Query engine (range/agg) (3/5)
  - [ ] p95 query latency ≤ budget on N series.

- [ ] R4. Cardinality guard (3/5)
  - [ ] High‑cardinality write blocked with clear error.

## Bonus

- [ ] B1. Bitmap/roaring indexes (3/5)

- [ ] B2. Compaction scheduler (3/5)

- [ ] B3. Sparse storage for NaNs (3/5)
