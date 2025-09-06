# Checklist — 03-consensus-prototype

## Implementation Order
- [ ] R1. Leader election & terms (4/5)
- [ ] R2. Log replication & commit index (4/5)
- [ ] R3. Snapshot/installSnapshot (4/5)
- [ ] R4. Fault injection tests (4/5)

## Tasks

- [ ] R1. Leader election & terms (4/5)
  - [ ] Single leader emerges; re‑election on leader crash.

- [ ] R2. Log replication & commit index (4/5)
  - [ ] Writes acknowledged after majority commit; followers converge.

- [ ] R3. Snapshot/installSnapshot (4/5)
  - [ ] Followers catch up via snapshots; memory bounded under churn.

- [ ] R4. Fault injection tests (4/5)
  - [ ] Linearizable command sequence verified on a Jepsen‑style harness.

## Bonus

- [ ] B1. Joint consensus membership changes (4/5)

- [ ] B2. Pre‑vote optimization (3/5)

- [ ] B3. Log compaction policy (3/5)
