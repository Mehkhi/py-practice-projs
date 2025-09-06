# Checklist — 06-streaming-log-analytics

## Implementation Order
- [ ] R1. Ingest & parse (3/5)
- [ ] R2. Time‑windowed inverted index (3/5)
- [ ] R3. Query DSL (filter/agg) (3/5)
- [ ] R4. Alerts & dashboards (2/5)

## Tasks

- [ ] R1. Ingest & parse (3/5)
  - [ ] ≥99% lines parsed; bad lines counted and reported.

- [ ] R2. Time‑windowed inverted index (3/5)
  - [ ] Queries restricted to windows; retention policy prunes old segments.

- [ ] R3. Query DSL (filter/agg) (3/5)
  - [ ] Deterministic results; syntax errors return helpful messages.

- [ ] R4. Alerts & dashboards (2/5)
  - [ ] Alerts fire once per condition window; dashboards render key charts.

## Bonus

- [ ] B1. Query optimizer (cost hints) (4/5)

- [ ] B2. Hot/cold tiers (3/5)

- [ ] B3. Sampling & rollups (3/5)
