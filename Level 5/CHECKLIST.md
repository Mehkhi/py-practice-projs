# Level 5 — Expert (Staff/Principal Engineer)

Systems design and platform work. You’ll prototype distributed systems, design for resiliency, and build reusable platforms that other teams can use. These are ambitious, multi‑week projects.

## Checklist

- [ ] 1. Event‑Sourced System (CQRS)
  - What you build: Command/write model emits events; read model projects views.
  - Skills: domain modeling, event store, projections, idempotency.
  - Milestones: Rebuild read model; snapshots; replay speed.
  - Stretch goals: Multi‑tenant streams and GDPR delete.

- [ ] 2. Custom Task Queue
  - What you build: Design a Celery‑like queue with reliability semantics.
  - Skills: broker protocol, ack/retry, visibility timeout.
  - Milestones: At‑least‑once delivery; dead letters; metrics.
  - Stretch goals: Exactly‑once with dedupe keys and idempotency.

- [ ] 3. Consensus (Raft) Prototype
  - What you build: Replicated log with leader election and log compaction.
  - Skills: state machines, RPC, timeouts, quorum.
  - Milestones: Crash/recover; partition tests; snapshots.
  - Stretch goals: Membership changes during operation.

- [ ] 4. Mini Database Engine
  - What you build: Append‑only log, B‑Tree index, simple SQL parser.
  - Skills: storage layout, indexing, MVCC basics.
  - Milestones: Transactions; WAL; crash consistency tests.
  - Stretch goals: Query planner with cost estimates.

- [ ] 5. Vector Search Service
  - What you build: Embed text and serve nearest‑neighbor queries.
  - Skills: embeddings, ANN (faiss), indexing, batching.
  - Milestones: Upserts; versioning; recall@k evaluation.
  - Stretch goals: Hybrid BM25 + vector ranking.

- [ ] 6. Streaming Log Analytics
  - What you build: Ingest logs, index, and run query DSL (mini‑Splunk).
  - Skills: parsers, inverted index, time windows.
  - Milestones: Aggregations; alerting; dashboards.
  - Stretch goals: Query optimizer and hot/cold tiers.

- [ ] 7. Rate Limiter Service
  - What you build: Distributed token bucket with sliding window algorithm.
  - Skills: Redis scripts/Lua, clock skew, fairness.
  - Milestones: Global vs per‑key limits; headers; audits.
  - Stretch goals: Adaptive limits based on error budgets.

- [ ] 8. Feature Store for ML
  - What you build: Offline/online sync of features with freshness guarantees.
  - Skills: point‑in‑time joins, materialization, TTLs.
  - Milestones: Backfills; serving API; lineage metadata.
  - Stretch goals: Streaming features and drift detection.

- [ ] 9. Distributed Scheduler
  - What you build: Cron‑like system with leader election and failover.
  - Skills: locks, heartbeats, leases, idempotent jobs.
  - Milestones: Misfire handling; jitter; pause/resume.
  - Stretch goals: Cron expression shards and priorities.

- [ ] 10. Data Lineage & Governance
  - What you build: Track datasets, jobs, and their dependencies.
  - Skills: graph modeling, metadata store, hooks.
  - Milestones: Impact analysis; ownership; SLAs.
  - Stretch goals: OpenLineage integration and UI.

- [ ] 11. Predictive Caching Layer
  - What you build: Prefetch based on patterns with reinforcement learning lite.
  - Skills: Markov models/bandits, cache policy design.
  - Milestones: Hit‑rate metrics; ablation tests.
  - Stretch goals: Cost‑aware prefetching.

- [ ] 12. Time‑Series Store
  - What you build: Write‑optimized TSDB with compression and rollups.
  - Skills: columnar storage, delta encoding, downsampling.
  - Milestones: Compaction; retention; query engine.
  - Stretch goals: Cardinality management strategies.

- [ ] 13. Ranking Experimentation Platform
  - What you build: AB testing for ranking models with metrics pipeline.
  - Skills: experiment design, metric logging, stats.
  - Milestones: Guardrails; sequential testing; dashboards.
  - Stretch goals: Switchback tests for network effects.

- [ ] 14. Rules DSL Compiler
  - What you build: Create a small DSL and compile to Python AST.
  - Skills: parsing (lark/PLY), AST, codegen, safety.
  - Milestones: Static analysis; error reporting; tests.
  - Stretch goals: JIT via numba for numeric rules.

- [ ] 15. High‑Throughput HTTP Server
  - What you build: Tune uvicorn/uvloop, pool sizes, and kernel knobs.
  - Skills: async IO, load testing, profiling.
  - Milestones: Latency/throughput graphs; flamecharts.
  - Stretch goals: Zero‑copy responses and sendfile.

- [ ] 16. Retry/Backoff Library
  - What you build: Robust retries with jitter and circuit breaker.
  - Skills: decorators, exceptions, policies, packaging.
  - Milestones: Integrations; metrics; typed API.
  - Stretch goals: Publish to PyPI and semantic releases.

- [ ] 17. Static Analysis Tooling
  - What you build: Analyze Python AST to enforce org‑wide rules.
  - Skills: ast module, visitors, autofixes.
  - Milestones: Rule config; CI integration; reports.
  - Stretch goals: Language server protocol plugin.

- [ ] 18. Schema Registry
  - What you build: Centralize pydantic/Avro schemas with versioning and codegen.
  - Skills: compatibility checks, generators, registries.
  - Milestones: Deprecations; changelogs; governance flow.
  - Stretch goals: Multi‑language client SDKs.

- [ ] 19. Zero‑Downtime Migration Toolkit
  - What you build: Plan/apply DB schema/data changes safely.
  - Skills: expand‑contract, backfills, dual‑writes.
  - Milestones: Verification jobs; rollback; metrics.
  - Stretch goals: Auto‑generated plans from models.

- [ ] 20. Security & Compliance Scanner
  - What you build: Scan repos/infrastructure for policy violations.
  - Skills: AST, regex, config parsing, reporting.
  - Milestones: Baselines; auto‑fixes; suppression workflow.
  - Stretch goals: SBOM creation and diff.

- [ ] 21. Cost‑Aware Autoscaling Simulator
  - What you build: Simulate autoscaling based on workload and budgets.
  - Skills: queueing theory, policies, plotting.
  - Milestones: SLA/Cost frontier; scenario runner.
  - Stretch goals: RL‑based policy search.

- [ ] 22. Chaos Engineering Toolkit
  - What you build: Inject faults and run resilience experiments.
  - Skills: failure modes, experiments, observability.
  - Milestones: Steady‑state checks; blast radius limits.
  - Stretch goals: Automatic hypothesis generation.

- [ ] 23. Multi‑Region Active‑Active Demo
  - What you build: Run two regions with conflict resolution.
  - Skills: replication, CRDTs, traffic routing.
  - Milestones: Failover drills; consistency docs.
  - Stretch goals: Geo‑based routing and partition tests.

- [ ] 24. Privacy‑Preserving Analytics
  - What you build: Aggregate metrics with differential privacy noise.
  - Skills: DP basics, sensitivity, epsilon accounting.
  - Milestones: Utility vs privacy tradeoff plots.
  - Stretch goals: Federated learning simulation.

- [ ] 25. Observability Platform
  - What you build: Unified pipelines for logs/metrics/traces with SLOs.
  - Skills: OTEL collectors, exporters, SLO math.
  - Milestones: Error budget burn alerts; runbooks.
  - Stretch goals: Auto‑instrumentation playbooks.

- [ ] 26. Platform Starter Kits
  - What you build: Create cookiecutters/templates for teams to bootstrap apps.
  - Skills: cookiecutter, templates, docs, DX design.
  - Milestones: Secure defaults; CI/CD included; examples.
  - Stretch goals: Internal portal that scaffolds projects via UI.
