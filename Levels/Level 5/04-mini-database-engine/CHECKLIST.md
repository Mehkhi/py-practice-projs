# Checklist — 04-mini-database-engine

## Implementation Order
- [ ] R1. Append‑only heap + WAL (4/5)
- [ ] R2. B‑Tree index (unique & non‑unique) (4/5)
- [ ] R3. Transactions & isolation (4/5)
- [ ] R4. SQL subset executor (3/5)

## Tasks

- [ ] R1. Append‑only heap + WAL (4/5)
  - [ ] Crash tests show committed records recover; torn writes handled.

- [ ] R2. B‑Tree index (unique & non‑unique) (4/5)
  - [ ] Index validates against heap scan for correctness.

- [ ] R3. Transactions & isolation (4/5)
  - [ ] Concurrent transactions preserve serializable (or documented) semantics.

- [ ] R4. SQL subset executor (3/5)
  - [ ] Queries return correct rows; updates use index where available.

## Bonus

- [ ] B1. Cost‑based planner (lite) (4/5)

- [ ] B2. MVCC snapshots (4/5)

- [ ] B3. Background compaction (3/5)
