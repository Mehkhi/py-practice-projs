# Checklist — 23-multi-region-active-active-demo

## Implementation Order
- [ ] R1. Replication strategy (4/5)
- [ ] R2. Traffic routing (3/5)
- [ ] R3. Failover drills (3/5)
- [ ] R4. Consistency docs & invariants (2/5)

## Tasks

- [ ] R1. Replication strategy (4/5)
  - [ ] Regions converge after partitions; conflicts resolved deterministically.

- [ ] R2. Traffic routing (3/5)
  - [ ] Traffic shifts on fail; sticky sessions handled.

- [ ] R3. Failover drills (3/5)
  - [ ] Drills executed; RTO/RPO met; audit logged.

- [ ] R4. Consistency docs & invariants (2/5)
  - [ ] Documented invariants with examples and failure modes.

## Bonus

- [ ] B1. Partition simulations (3/5)

- [ ] B2. Vector clocks/lamport clocks (3/5)

- [ ] B3. Eventually consistent caches (2/5)
