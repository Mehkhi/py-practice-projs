# Checklist — 01-event-sourced-system

## Implementation Order
- [ ] R1. Append‑only event store API (4/5)
- [ ] R2. Command handlers & aggregates (4/5)
- [ ] R3. Projections & read models (3/5)
- [ ] R4. Snapshots & replay performance (3/5)

## Tasks

- [ ] R1. Append‑only event store API (4/5)
  - [ ] Concurrent appends detect version conflicts; retries with idempotency key do not duplicate.
  - [ ] Event schema versions tracked; upcasters supported.

- [ ] R2. Command handlers & aggregates (4/5)
  - [ ] Invariant‑violating commands rejected with domain errors.
  - [ ] Aggregate state rebuilt from events deterministically.

- [ ] R3. Projections & read models (3/5)
  - [ ] Full rebuild from empty DB produces consistent read model.
  - [ ] Projection lag metric exported; resume works after crash.

- [ ] R4. Snapshots & replay performance (3/5)
  - [ ] Rebuild within target (e.g., < N seconds for M events) with snapshots enabled.
  - [ ] Snapshot integrity verified by checksum or schema version.

## Bonus

- [ ] B1. Multi‑tenant streams (3/5)

- [ ] B2. GDPR deletion/redaction (4/5)

- [ ] B3. Outbox + subscriptions (3/5)
