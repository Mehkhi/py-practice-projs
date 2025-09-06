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

---

## Detailed Spec Sheets — Level 5 (Expert)

This section expands each Level‑5 checklist item into an implementation spec with **required features** and **bonus features**. Every feature includes a **difficulty rating**, an **extensive breakdown of what it teaches**, and **acceptance criteria** you can self‑verify.

### Difficulty Legend
- **1** = Very easy (few lines, minimal edge cases)
- **2** = Easy (simple logic, basic edge cases)
- **3** = Moderate (multiple components, careful handling)
- **4** = Hard (non‑trivial algorithms/design, extensive testing)
- **5** = Very hard (complex algorithms or architecture)

### Common Requirements for Project Completion
- All **required features** implemented and demonstrated.
- At least **12–15 tests** per project, including **unit + integration**, plus **load/failure tests** where applicable.
- Clear **README** with architecture diagram, run steps (dev/prod), SLAs/SLOs, and operational runbooks (deploy, rollback, backups).
- Code formatted with **black** and linted with **ruff/flake8**; imports via **isort**.
- Public APIs and key modules include **type hints**; `mypy`/`pyright` passes or exceptions are documented.
- **Observability**: structured logs, metrics counters, and traces across critical paths.
- **Security**: secret handling, least‑privilege, input validation, dependency scans, and threat model doc.
- **Resilience**: graceful degradation, retries/backoff, timeouts, and circuit breakers where relevant.

> Tip: Track each feature as a GitHub issue. Label with `difficulty/x`, `type/required` or `type/bonus`.

---

### 1) Event‑Sourced System (CQRS)
**What you’re building:** Command/write model emits events; read model projects queryable views.
**Core skills:** Domain modeling, event stores, projections, idempotency, snapshots.

#### Required Features
- **R1. Append‑only event store API** — **Difficulty 4/5**
  - **What it teaches:**
    - Stream IDs, optimistic concurrency (`expected_version`), global ordering.
    - Idempotency keys and dedupe on retry.
    - Serialization/versioning of event payloads.
  - **Acceptance criteria:**
    - Concurrent appends detect version conflicts; retries with idempotency key do not duplicate.
    - Event schema versions tracked; upcasters supported.

- **R2. Command handlers & aggregates** — **Difficulty 4/5**
  - **What it teaches:**
    - Aggregate invariants, precondition checks, pure decision logic.
    - Separating command → events from applying events to state.
  - **Acceptance criteria:**
    - Invariant‑violating commands rejected with domain errors.
    - Aggregate state rebuilt from events deterministically.

- **R3. Projections & read models** — **Difficulty 3/5**
  - **What it teaches:**
    - At‑least‑once projection runners, idempotent handlers, checkpointing.
    - Handling out‑of‑order or duplicate events.
  - **Acceptance criteria:**
    - Full rebuild from empty DB produces consistent read model.
    - Projection lag metric exported; resume works after crash.

- **R4. Snapshots & replay performance** — **Difficulty 3/5**
  - **What it teaches:**
    - Snapshot intervals, compaction, and trade‑offs.
    - Replay time budgeting and profiling.
  - **Acceptance criteria:**
    - Rebuild within target (e.g., < N seconds for M events) with snapshots enabled.
    - Snapshot integrity verified by checksum or schema version.

#### Bonus Features
- **B1. Multi‑tenant streams** — **Difficulty 3/5**
  - **Teaches:** Tenant isolation (prefixes/DBs), quota limits.
  - **Acceptance:** Cross‑tenant reads/writes blocked; quotas enforced.
- **B2. GDPR deletion/redaction** — **Difficulty 4/5**
  - **Teaches:** Redaction events, rewrite strategies, audit trails.
  - **Acceptance:** PII removed from projections and future rebuilds; audit entry created.
- **B3. Outbox + subscriptions** — **Difficulty 3/5**
  - **Teaches:** Transactional outbox pattern for integration events.
  - **Acceptance:** Downstream receives each event once; retries are idempotent.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 2) Custom Task Queue
**What you’re building:** Celery‑like queue with reliability semantics.
**Core skills:** Broker protocol, ack/retry, visibility timeout, metrics.

#### Required Features
- **R1. Broker protocol & message format** — **Difficulty 3/5**
  - **What it teaches:**
    - Envelope (id, type, args, headers), visibility timeouts, dead lettering.
    - Durable publish and confirm semantics.
  - **Acceptance criteria:**
    - Messages survive broker restart; visibility timeout extends on heartbeat.

- **R2. Worker concurrency & dispatcher** — **Difficulty 3/5**
  - **What it teaches:**
    - Thread/Process/async workers; graceful shutdown; backpressure.
  - **Acceptance criteria:**
    - Configurable concurrency; draining on SIGTERM without loss.

- **R3. Retries with exponential backoff + jitter** — **Difficulty 3/5**
  - **What it teaches:**
    - Retryable vs non‑retryable errors; DLQ thresholds.
  - **Acceptance criteria:**
    - Retry policy enforced; DLQ populated with final failure reason.

- **R4. Idempotency & metrics** — **Difficulty 3/5**
  - **What it teaches:**
    - Idempotency keys and dedupe cache; queue depth/latency metrics.
  - **Acceptance criteria:**
    - Duplicate job submissions suppressed within TTL; dashboards show depth, inflight, p95.

#### Bonus Features
- **B1. Exactly‑once illusion** — **Difficulty 4/5**
  - **Teaches:** Outbox/inbox tables; idempotent side effects.
  - **Acceptance:** Replays do not double‑apply effects.
- **B2. Scheduling (delayed/cron)** — **Difficulty 3/5**
  - **Teaches:** Delayed queues and periodic job registration.
  - **Acceptance:** Jobs fire at intended times; misfire policy documented.
- **B3. Priority queues** — **Difficulty 2/5**
  - **Teaches:** Separate pools; starvation prevention.
  - **Acceptance:** High‑priority jobs preempt lower priority without starvation.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 3) Consensus (Raft) Prototype
**What you’re building:** Replicated log with leader election and compaction.
**Core skills:** State machines, RPC, timeouts, quorum.

#### Required Features
- **R1. Leader election & terms** — **Difficulty 4/5**
  - **What it teaches:**
    - Election timeouts, randomized backoff, majority quorum.
  - **Acceptance criteria:**
    - Single leader emerges; re‑election on leader crash.

- **R2. Log replication & commit index** — **Difficulty 4/5**
  - **What it teaches:**
    - AppendEntries RPC, log matching property, commit rules.
  - **Acceptance criteria:**
    - Writes acknowledged after majority commit; followers converge.

- **R3. Snapshot/installSnapshot** — **Difficulty 4/5**
  - **What it teaches:**
    - Log compaction; truncated prefix; state machine snapshots.
  - **Acceptance criteria:**
    - Followers catch up via snapshots; memory bounded under churn.

- **R4. Fault injection tests** — **Difficulty 4/5**
  - **What it teaches:**
    - Partition, reordering, duplication; safety/liveness checks.
  - **Acceptance criteria:**
    - Linearizable command sequence verified on a Jepsen‑style harness.

#### Bonus Features
- **B1. Joint consensus membership changes** — **Difficulty 4/5**
  - **Teaches:** Safe config changes.
  - **Acceptance:** Add/remove node without availability loss.
- **B2. Pre‑vote optimization** — **Difficulty 3/5**
  - **Teaches:** Avoiding disruptive elections.
  - **Acceptance:** Fewer term bumps during partitions.
- **B3. Log compaction policy** — **Difficulty 3/5**
  - **Teaches:** Snapshot intervals vs throughput.
  - **Acceptance:** Tunable trade‑off documented with benchmarks.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 4) Mini Database Engine
**What you’re building:** Append‑only storage, B‑Tree index, simple SQL executor.
**Core skills:** Storage layout, indexing, transactions, WAL/crash‑consistency.

#### Required Features
- **R1. Append‑only heap + WAL** — **Difficulty 4/5**
  - **What it teaches:**
    - Page layout, record headers, checksum, write‑ahead logging.
  - **Acceptance criteria:**
    - Crash tests show committed records recover; torn writes handled.

- **R2. B‑Tree index (unique & non‑unique)** — **Difficulty 4/5**
  - **What it teaches:**
    - Search/insert/split/merge; key comparators.
  - **Acceptance criteria:**
    - Index validates against heap scan for correctness.

- **R3. Transactions & isolation** — **Difficulty 4/5**
  - **What it teaches:**
    - Basic 2PL or MVCC; locks/versions; deadlock detection.
  - **Acceptance criteria:**
    - Concurrent transactions preserve serializable (or documented) semantics.

- **R4. SQL subset executor** — **Difficulty 3/5**
  - **What it teaches:**
    - Parse `SELECT/INSERT/UPDATE/DELETE`, simple planner and executor.
  - **Acceptance criteria:**
    - Queries return correct rows; updates use index where available.

#### Bonus Features
- **B1. Cost‑based planner (lite)** — **Difficulty 4/5**
  - **Teaches:** Cardinality estimates; plan selection.
  - **Acceptance:** Plans chosen improve runtime on benchmarks.
- **B2. MVCC snapshots** — **Difficulty 4/5**
  - **Teaches:** Snapshot reads; vacuum.
  - **Acceptance:** Readers don’t block writers; space reclaimed.
- **B3. Background compaction** — **Difficulty 3/5**
  - **Teaches:** Vacuum/defrag; throttling.
  - **Acceptance:** Steady performance under write load.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 5) Vector Search Service
**What you’re building:** Embed text and serve nearest‑neighbor queries.
**Core skills:** Embeddings, FAISS/ANN, indexing, evaluation, batching.

#### Required Features
- **R1. Embedding pipeline & batching** — **Difficulty 3/5**
  - **What it teaches:**
    - Model selection, normalization, batching for throughput.
  - **Acceptance criteria:**
    - Throughput and latency documented; deterministic embeddings across runs.

- **R2. ANN index (IVF/HNSW)** — **Difficulty 3/5**
  - **What it teaches:**
    - Index choice trade‑offs; M (graph degree), efSearch tuning.
  - **Acceptance criteria:**
    - Build time and memory measured; recall target configured.

- **R3. Query API & filters** — **Difficulty 3/5**
  - **What it teaches:**
    - kNN search, metadata filtering, distance metrics.
  - **Acceptance criteria:**
    - API returns top‑k with scores and metadata; filters reduce candidates.

- **R4. Evaluation (recall@k & SLOs)** — **Difficulty 3/5**
  - **What it teaches:**
    - Gold set creation; recall/speed trade‑offs.
  - **Acceptance criteria:**
    - Meets recall@k ≥ target and p95 latency ≤ budget.

#### Bonus Features
- **B1. Hybrid BM25 + vector rerank** — **Difficulty 4/5**
  - **Teaches:** Hybrid retrieval; score blending/reranking.
  - **Acceptance:** Hybrid beats either alone on eval set.
- **B2. Streaming upserts** — **Difficulty 3/5**
  - **Teaches:** Background index updates; tombstones.
  - **Acceptance:** Fresh docs searchable within SLA; no query stalls.
- **B3. Multi‑tenant isolation** — **Difficulty 3/5**
  - **Teaches:** Per‑tenant spaces/shards; quotas.
  - **Acceptance:** Tenants cannot access others’ vectors.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 6) Streaming Log Analytics
**What you’re building:** Ingest logs, index, and query with a mini DSL.
**Core skills:** Parsers, inverted index, time windows, alerting.

#### Required Features
- **R1. Ingest & parse** — **Difficulty 3/5**
  - **What it teaches:**
    - Common/JSON log formats; timestamp extraction; time zones.
  - **Acceptance criteria:**
    - ≥99% lines parsed; bad lines counted and reported.

- **R2. Time‑windowed inverted index** — **Difficulty 3/5**
  - **What it teaches:**
    - Sharded segments, retention, compaction.
  - **Acceptance criteria:**
    - Queries restricted to windows; retention policy prunes old segments.

- **R3. Query DSL (filter/agg)** — **Difficulty 3/5**
  - **What it teaches:**
    - Filters, regex, group‑by, top‑k.
  - **Acceptance criteria:**
    - Deterministic results; syntax errors return helpful messages.

- **R4. Alerts & dashboards** — **Difficulty 2/5**
  - **What it teaches:**
    - Threshold rules, z‑score spikes; templated dashboards.
  - **Acceptance criteria:**
    - Alerts fire once per condition window; dashboards render key charts.

#### Bonus Features
- **B1. Query optimizer (cost hints)** — **Difficulty 4/5**
  - **Teaches:** Predicate pushdown; index selection.
  - **Acceptance:** Optimized queries measurably faster.
- **B2. Hot/cold tiers** — **Difficulty 3/5**
  - **Teaches:** Storage costs vs latency.
  - **Acceptance:** Hot tier hit ratio tracked; cold scans documented.
- **B3. Sampling & rollups** — **Difficulty 3/5**
  - **Teaches:** Approximate answers; rollup tables.
  - **Acceptance:** Error bounds documented; faster queries under load.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 7) Rate Limiter Service
**What you’re building:** Distributed token bucket and sliding window limits.
**Core skills:** Redis Lua/atomics, fairness, headers, skew.

#### Required Features
- **R1. Token bucket per key** — **Difficulty 3/5**
  - **What it teaches:**
    - Atomic refill/consume with Lua; burst capacity.
  - **Acceptance criteria:**
    - Correct headers returned (`X‑RateLimit‑Remaining`, `Reset`).

- **R2. Sliding window approximation** — **Difficulty 3/5**
  - **What it teaches:**
    - Fixed vs sliding window; memory/time trade‑offs.
  - **Acceptance criteria:**
    - Dropped/allowed decisions match model within tolerance.

- **R3. Global + per‑key limits** — **Difficulty 3/5**
  - **What it teaches:**
    - Coordinating multiple limiters; fairness across tenants.
  - **Acceptance criteria:**
    - No single key can starve others; global cap enforced.

- **R4. Skew & audits** — **Difficulty 2/5**
  - **What it teaches:**
    - NTP skew handling; audit logging.
  - **Acceptance criteria:**
    - Skew tolerance documented; audit entries persisted.

#### Bonus Features
- **B1. Adaptive limits (error budgets)** — **Difficulty 4/5**
  - **Teaches:** Burn‑rate feedback to adjust limits.
  - **Acceptance:** Limits tighten/relax based on SLO burn.
- **B2. Distributed fairness** — **Difficulty 3/5**
  - **Teaches:** DRR/weighted fairness.
  - **Acceptance:** Weighted tenants get proportional share.
- **B3. Client SDK** — **Difficulty 2/5**
  - **Teaches:** Client‑side leaky buckets to smooth bursts.
  - **Acceptance:** Fewer 429s under bursty clients.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 8) Feature Store for ML
**What you’re building:** Offline/online features with freshness guarantees.
**Core skills:** Point‑in‑time joins, materialization, TTLs, lineage.

#### Required Features
- **R1. Feature registry & schemas** — **Difficulty 3/5**
  - **What it teaches:**
    - Declaring entities, features, sources, ownership.
  - **Acceptance criteria:**
    - Registry validated; schema evolution tested.

- **R2. Point‑in‑time join** — **Difficulty 4/5**
  - **What it teaches:**
    - Preventing leakage; time travel; late‑arriving data.
  - **Acceptance criteria:**
    - Training sets pass leakage checks; unit tests verify PIT logic.

- **R3. Materialization jobs (batch/stream)** — **Difficulty 3/5**
  - **What it teaches:**
    - Backfills, TTL, online store sync.
  - **Acceptance criteria:**
    - Online values within freshness SLA; lag metric exported.

- **R4. Serving API + lineage** — **Difficulty 3/5**
  - **What it teaches:**
    - Low‑latency reads; lineage metadata for audits.
  - **Acceptance criteria:**
    - p95 latency ≤ target; lineage query returns producers/consumers.

#### Bonus Features
- **B1. Streaming features** — **Difficulty 4/5**
  - **Teaches:** Incremental updates; upsert semantics.
  - **Acceptance:** Streamed features update online store in seconds.
- **B2. Drift detection** — **Difficulty 3/5**
  - **Teaches:** PSI/KS tests; alerts.
  - **Acceptance:** Drifts above threshold trigger alerts.
- **B3. Access control per feature** — **Difficulty 3/5**
  - **Teaches:** Row/column‑level ACLs.
  - **Acceptance:** Unauthorized access denied; audited.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 9) Distributed Scheduler
**What you’re building:** Cron‑like system with leader election and failover.
**Core skills:** Locks, heartbeats, leases, idempotent jobs.

#### Required Features
- **R1. Leader election & lease** — **Difficulty 3/5**
  - **What it teaches:**
    - Lease durations, renewal, fencing tokens.
  - **Acceptance criteria:**
    - Single active leader; takeover on failure within SLA.

- **R2. Cron parser & registry** — **Difficulty 3/5**
  - **What it teaches:**
    - Cron expressions, calendars, time zones.
  - **Acceptance criteria:**
    - Next‑run times match reference; edge cases (DST) tested.

- **R3. Idempotent job execution** — **Difficulty 3/5**
  - **What it teaches:**
    - Dedup keys, retries, misfire policies, jitter.
  - **Acceptance criteria:**
    - No duplicate effects under retries; misfires handled per policy.

- **R4. Pause/resume & monitoring** — **Difficulty 2/5**
  - **What it teaches:**
    - Operational controls; status APIs.
  - **Acceptance criteria:**
    - Jobs listable/filterable; pause/resume persists.

#### Bonus Features
- **B1. Sharded schedulers** — **Difficulty 3/5**
  - **Teaches:** Distributing cron across nodes.
  - **Acceptance:** Shards balance; hot shard detection present.
- **B2. Priority scheduling** — **Difficulty 2/5**
  - **Teaches:** Priority queues.
  - **Acceptance:** High priority moves earlier within window.
- **B3. History retention & audit** — **Difficulty 2/5**
  - **Teaches:** Job history and outcomes.
  - **Acceptance:** Query by date/status; export CSV.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 10) Data Lineage & Governance
**What you’re building:** Track datasets, jobs, and dependencies.
**Core skills:** Graph modeling, metadata store, hooks, impact analysis.

#### Required Features
- **R1. Graph model & APIs** — **Difficulty 3/5**
  - **What it teaches:**
    - Datasets, jobs, runs, edges, ownership.
  - **Acceptance criteria:**
    - CRUD works; referential integrity enforced.

- **R2. Ingestion hooks** — **Difficulty 3/5**
  - **What it teaches:**
    - Capturing lineage from pipelines and apps (OpenLineage‑style).
  - **Acceptance criteria:**
    - At least two producers instrumented; lineage visible end‑to‑end.

- **R3. Impact analysis & SLAs** — **Difficulty 3/5**
  - **What it teaches:**
    - Traversals; blast radius estimation; SLA ownership.
  - **Acceptance criteria:**
    - Report shows impacted downstream assets with owners.

- **R4. UI/reporting** — **Difficulty 2/5**
  - **What it teaches:**
    - Graph visualizations; export.
  - **Acceptance criteria:**
    - Web UI renders lineage; CSV/JSON export.

#### Bonus Features
- **B1. Policy checks** — **Difficulty 3/5**
  - **Teaches:** Required owners/tags; PII policies.
  - **Acceptance:** Violations flagged and blocked in CI.
- **B2. OpenLineage integration** — **Difficulty 2/5**
  - **Teaches:** Spec compliance.
  - **Acceptance:** Emits/ingests OL events.
- **B3. Ownership workflows** — **Difficulty 2/5**
  - **Teaches:** Approvals & assignments.
  - **Acceptance:** Ownership gaps resolved via workflow.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 11) Predictive Caching Layer
**What you’re building:** Prefetch based on usage patterns with bandits/Markov.
**Core skills:** Telemetry, cache policy, modeling, evaluation.

#### Required Features
- **R1. Baseline cache (LRU/TTL)** — **Difficulty 2/5**
  - **What it teaches:**
    - Hit/miss logging; eviction metrics.
  - **Acceptance criteria:**
    - Baseline hit rate established with charts.

- **R2. Demand model (Markov/bandit)** — **Difficulty 3/5**
  - **What it teaches:**
    - Transition matrices; confidence; exploration vs exploitation.
  - **Acceptance criteria:**
    - Prefetch decisions reproducible; parameters tunable.

- **R3. Online prefetcher** — **Difficulty 3/5**
  - **What it teaches:**
    - Prefetch budget and throttling; cancelation.
  - **Acceptance criteria:**
    - Prefetch improves p95 latency without excess cost.

- **R4. Ablation & A/B** — **Difficulty 3/5**
  - **What it teaches:**
    - Controlled experiments; metrics.
  - **Acceptance criteria:**
    - Predictive policy outperforms baseline with statistical confidence.

#### Bonus Features
- **B1. Cost‑aware decisions** — **Difficulty 3/5**
  - **Teaches:** $/GB, CPU, energy in objective.
  - **Acceptance:** Cost/latency frontier plotted.
- **B2. L2 (Redis) tier** — **Difficulty 2/5**
  - **Teaches:** Multi‑tier caching.
  - **Acceptance:** L1+L2 outperforms L1 only.
- **B3. Offline trainer** — **Difficulty 3/5**
  - **Teaches:** Replay logs; hyperparameter search.
  - **Acceptance:** Trained policy shipped with metadata.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 12) Time‑Series Store
**What you’re building:** Write‑optimized TSDB with compression and rollups.
**Core skills:** Columnar storage, delta encoding, downsampling, query engine.

#### Required Features
- **R1. Write path & segments** — **Difficulty 3/5**
  - **What it teaches:**
    - Segment files, indexes, compression (delta‑of‑delta).
  - **Acceptance criteria:**
    - Ingest meets throughput target; segments closed per policy.

- **R2. Downsampling & retention** — **Difficulty 3/5**
  - **What it teaches:**
    - Aggregate rollups; TTL deletion.
  - **Acceptance criteria:**
    - Queries transparently hit rolled‑up data; retention enforced.

- **R3. Query engine (range/agg)** — **Difficulty 3/5**
  - **What it teaches:**
    - Range scans; tag filters; group‑by.
  - **Acceptance criteria:**
    - p95 query latency ≤ budget on N series.

- **R4. Cardinality guard** — **Difficulty 3/5**
  - **What it teaches:**
    - Label cardinality control; quotas.
  - **Acceptance criteria:**
    - High‑cardinality write blocked with clear error.

#### Bonus Features
- **B1. Bitmap/roaring indexes** — **Difficulty 3/5**
  - **Teaches:** Fast set ops for tag filters.
  - **Acceptance:** Query speedup vs naive indexes.
- **B2. Compaction scheduler** — **Difficulty 3/5**
  - **Teaches:** Background merges; throttling.
  - **Acceptance:** Jittered compactions; minimal read amplification.
- **B3. Sparse storage for NaNs** — **Difficulty 3/5**
  - **Teaches:** Memory savings for sparse series.
  - **Acceptance:** Memory profile improved on sparse datasets.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 13) Ranking Experimentation Platform
**What you’re building:** A/B testing for ranking models with metrics pipeline.
**Core skills:** Experiment design, metric logging, stats, guardrails.

#### Required Features
- **R1. Assignment & bucketing** — **Difficulty 3/5**
  - **What it teaches:**
    - Hash‑based stable bucketing; exposure logs.
  - **Acceptance criteria:**
    - No cross‑test contamination; balanced arms.

- **R2. Metrics pipeline** — **Difficulty 3/5**
  - **What it teaches:**
    - Event schema; at‑least‑once ingestion; dedup.
  - **Acceptance criteria:**
    - Metrics computed reproducibly; late events handled.

- **R3. Statistical analysis** — **Difficulty 3/5**
  - **What it teaches:**
    - CUPED/stratification; sequential tests; guardrails.
  - **Acceptance criteria:**
    - Significance and power reported; stop rules implemented.

- **R4. Dashboard & audit** — **Difficulty 2/5**
  - **What it teaches:**
    - Results visualization; approvals.
  - **Acceptance criteria:**
    - Experiment lifecycle tracked with approvals.

#### Bonus Features
- **B1. Switchback tests** — **Difficulty 3/5**
  - **Teaches:** Temporal alternation to reduce network effects.
  - **Acceptance:** Design and analysis documented; used on at least one test.
- **B2. Heterogeneity analysis** — **Difficulty 2/5**
  - **Teaches:** Segment‑level effects.
  - **Acceptance:** Lift by segment charted.
- **B3. Counterfactual evaluation** — **Difficulty 3/5**
  - **Teaches:** IPS/DR estimators.
  - **Acceptance:** Offline estimates compare with online results.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 14) Rules DSL Compiler
**What you’re building:** Small DSL that compiles to safe Python AST.
**Core skills:** Parsing (lark/PLY), AST, codegen, safety.

#### Required Features
- **R1. Grammar & parser** — **Difficulty 3/5**
  - **What it teaches:**
    - Grammar design; error recovery; helpful messages.
  - **Acceptance criteria:**
    - Invalid syntax yields line/column with caret.

- **R2. AST + type checking** — **Difficulty 3/5**
  - **What it teaches:**
    - Static checks (types, arity, undefined names).
  - **Acceptance criteria:**
    - Type errors reported before codegen.

- **R3. Codegen to Python AST** — **Difficulty 3/5**
  - **What it teaches:**
    - AST transforms; sandboxing builtins; resource limits.
  - **Acceptance criteria:**
    - Generated code passes tests and adheres to safety sandbox.

- **R4. Static analysis & lints** — **Difficulty 3/5**
  - **What it teaches:**
    - Complexity limits; recursion depth; constant folding.
  - **Acceptance criteria:**
    - Programs exceeding limits are rejected with guidance.

#### Bonus Features
- **B1. JIT with numba (numeric rules)** — **Difficulty 4/5**
  - **Teaches:** JIT trade‑offs; performance vs flexibility.
  - **Acceptance:** Speedup demonstrated on numeric workloads.
- **B2. REPL + debugger** — **Difficulty 3/5**
  - **Teaches:** Interactive shell; stepping through AST.
  - **Acceptance:** Users can eval and inspect rule execution.
- **B3. Source maps** — **Difficulty 3/5**
  - **Teaches:** Map DSL nodes to Python lines.
  - **Acceptance:** Errors reference original DSL spans.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 15) High‑Throughput HTTP Server
**What you’re building:** Tune uvicorn/uvloop, pools, and kernel for throughput.
**Core skills:** Async IO, load testing, profiling, kernel tuning.

#### Required Features
- **R1. Baseline & SLOs** — **Difficulty 2/5**
  - **What it teaches:**
    - Defining p50/p95/p99 targets; capacity planning.
  - **Acceptance criteria:**
    - Baseline charts saved; SLOs documented.

- **R2. Load tests & flamecharts** — **Difficulty 3/5**
  - **What it teaches:**
    - `wrk`/`hey`/`k6` runs; py‑spy/eBPF profiles.
  - **Acceptance criteria:**
    - Flamegraphs identify top bottlenecks; regressions tracked.

- **R3. Optimizations** — **Difficulty 3/5**
  - **What it teaches:**
    - Keepalive tuning, threadpools, zero‑copy (`sendfile`).
  - **Acceptance criteria:**
    - Throughput improved ≥ X%; tail latency reduced.

- **R4. Backpressure & overload protection** — **Difficulty 3/5**
  - **What it teaches:**
    - Queue limits, 503s, shed load, circuit breakers.
  - **Acceptance criteria:**
    - Under overload, system stays responsive with bounded latency.

#### Bonus Features
- **B1. TLS optimization** — **Difficulty 3/5**
  - **Teaches:** HTTP/2, ciphers, session resumption.
  - **Acceptance:** TLS adds minimal overhead; documented.
- **B2. Kernel tuning** — **Difficulty 3/5**
  - **Teaches:** SOMAXCONN, rmem/wmem, TCP knobs.
  - **Acceptance:** Bench vs defaults; wins recorded.
- **B3. eBPF profiling** — **Difficulty 3/5**
  - **Teaches:** System‑wide visibility.
  - **Acceptance:** Profiles correlate app ↔ kernel time.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 16) Retry/Backoff Library
**What you’re building:** Robust retries with jitter and circuit breaking.
**Core skills:** Decorators, exceptions, policies, packaging.

#### Required Features
- **R1. Policy config & decorators** — **Difficulty 2/5**
  - **What it teaches:**
    - Retry strategies (const/expo/jitter), max attempts, timeouts.
  - **Acceptance criteria:**
    - Unit tests for policies; context carries attempt count.

- **R2. Error taxonomy** — **Difficulty 2/5**
  - **What it teaches:**
    - Retryable/non‑retryable classes; predicates.
  - **Acceptance criteria:**
    - Non‑retryable errors bypass retries with clear result.

- **R3. Circuit breaker** — **Difficulty 3/5**
  - **What it teaches:**
    - Open/half‑open/closed states; success thresholds.
  - **Acceptance criteria:**
    - Breaker trips and recovers per policy with metrics.

- **R4. Metrics & docs** — **Difficulty 2/5**
  - **What it teaches:**
    - Built‑in logging/metrics; README examples.
  - **Acceptance criteria:**
    - Examples runnable; metrics exported.

#### Bonus Features
- **B1. Async support** — **Difficulty 2/5**
  - **Teaches:** Async decorators; cancellation safety.
  - **Acceptance:** Works with async call sites.
- **B2. PyPI release & semantic versioning** — **Difficulty 2/5**
  - **Teaches:** Build/publish; release automation.
  - **Acceptance:** Package installable; releases tagged.
- **B3. Context propagation** — **Difficulty 2/5**
  - **Teaches:** Passing correlation IDs.
  - **Acceptance:** Logs include request IDs through retries.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 17) Static Analysis Tooling
**What you’re building:** Analyze Python AST to enforce org rules.
**Core skills:** `ast` module, visitors, autofixes, CI.

#### Required Features
- **R1. Rule engine & config** — **Difficulty 3/5**
  - **What it teaches:**
    - Rule registration, config schema, per‑repo overrides.
  - **Acceptance criteria:**
    - Rules toggleable; config validated with helpful errors.

- **R2. AST visitors & diagnostics** — **Difficulty 3/5**
  - **What it teaches:**
    - Traversals, locations, quick fixes.
  - **Acceptance criteria:**
    - Diagnostics precise with file:line:col; autofix suggestions present.

- **R3. Autofixers** — **Difficulty 3/5**
  - **What it teaches:**
    - Safe code mods; formatting preservation.
  - **Acceptance criteria:**
    - Fixes apply cleanly; tests prevent regressions.

- **R4. CI integration & SARIF** — **Difficulty 2/5**
  - **What it teaches:**
    - PR annotations; SARIF upload for code scanning.
  - **Acceptance criteria:**
    - CI shows inline annotations; SARIF consumed by platform.

#### Bonus Features
- **B1. LSP plugin** — **Difficulty 3/5**
  - **Teaches:** Language server hooks.
  - **Acceptance:** Editor diagnostics live as you type.
- **B2. Performance (parallel)** — **Difficulty 2/5**
  - **Teaches:** File sharding; caching.
  - **Acceptance:** Speed on large repos documented.
- **B3. Suppression workflow** — **Difficulty 2/5**
  - **Teaches:** Allow‑lists and expiry.
  - **Acceptance:** Suppressions expire and re‑open issues.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 18) Schema Registry
**What you’re building:** Centralize schemas with versioning and codegen.
**Core skills:** Compatibility checks, generators, registries.

#### Required Features
- **R1. Schema storage & versioning** — **Difficulty 3/5**
  - **What it teaches:**
    - Semantic/compat levels; deprecation policy.
  - **Acceptance criteria:**
    - Breaking changes rejected; changelog maintained.

- **R2. Codegen clients** — **Difficulty 3/5**
  - **What it teaches:**
    - Template generation for languages; package layout.
  - **Acceptance criteria:**
    - Client compiles and serializes/deserializes correctly.

- **R3. Governance flow** — **Difficulty 3/5**
  - **What it teaches:**
    - Review/approve/publish with owners.
  - **Acceptance criteria:**
    - Audit trail and approvals recorded.

- **R4. Access control** — **Difficulty 2/5**
  - **What it teaches:**
    - RBAC per schema/namespace.
  - **Acceptance criteria:**
    - Unauthorized access blocked; logs show attempts.

#### Bonus Features
- **B1. Multi‑language SDKs** — **Difficulty 3/5**
  - **Teaches:** Polyglot client generation.
  - **Acceptance:** At least two languages supported.
- **B2. Client caching & ETags** — **Difficulty 2/5**
  - **Teaches:** Conditional fetch; cache busting.
  - **Acceptance:** Fewer network requests; correct refresh on change.
- **B3. Schema graph** — **Difficulty 2/5**
  - **Teaches:** Dependencies and references.
  - **Acceptance:** Graph visualized and queryable.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 19) Zero‑Downtime Migration Toolkit
**What you’re building:** Plan/apply DB schema/data changes safely.
**Core skills:** Expand‑contract, backfills, dual‑writes, rollback.

#### Required Features
- **R1. Plan generator (expand/contract)** — **Difficulty 3/5**
  - **What it teaches:**
    - Safe ordering, feature flags, shadow columns.
  - **Acceptance criteria:**
    - Plan validates against model diffs; dry‑run available.

- **R2. Backfill jobs** — **Difficulty 3/5**
  - **What it teaches:**
    - Idempotent batch backfills; throttling.
  - **Acceptance criteria:**
    - Backfills resume after failure; progress tracked.

- **R3. Dual‑write and verification** — **Difficulty 3/5**
  - **What it teaches:**
    - Writing old+new paths and comparing.
  - **Acceptance criteria:**
    - Divergence alarms; cutover only when diff=0.

- **R4. Rollback & runbooks** — **Difficulty 2/5**
  - **What it teaches:**
    - Fast rollback and kill‑switches.
  - **Acceptance criteria:**
    - Rollback rehearsed; RTO met.

#### Bonus Features
- **B1. Auto plan from ORM models** — **Difficulty 3/5**
  - **Teaches:** Model introspection.
  - **Acceptance:** Plans generated for common changes.
- **B2. Canary migrations** — **Difficulty 2/5**
  - **Teaches:** Small‑scope testing before global.
  - **Acceptance:** Canary passes gates before full deploy.
- **B3. Analyzers** — **Difficulty 2/5**
  - **Teaches:** Hot table detection; lock risk.
  - **Acceptance:** Warnings produced for risky operations.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 20) Security & Compliance Scanner
**What you’re building:** Scan repos/infra for policy violations.
**Core skills:** AST/regex, config parsing, reporting, SBOM.

#### Required Features
- **R1. Rules engine** — **Difficulty 3/5**
  - **What it teaches:**
    - Rule DSL; severity levels; suppression policy.
  - **Acceptance criteria:**
    - Rules loaded from config; helpful messages.

- **R2. Repo + IaC scanning** — **Difficulty 3/5**
  - **What it teaches:**
    - AST for code; HCL/YAML for IaC; secret detection.
  - **Acceptance criteria:**
    - Findings categorized; false‑positive controls documented.

- **R3. Baselines & suppressions** — **Difficulty 2/5**
  - **What it teaches:**
    - Managing existing debt safely.
  - **Acceptance criteria:**
    - Baseline mode reduces noise; suppressions expire.

- **R4. Reports & SBOM** — **Difficulty 2/5**
  - **What it teaches:**
    - SARIF/JSON/HTML outputs; SBOM generation.
  - **Acceptance criteria:**
    - CI uploads reports; SBOM includes dependencies/versions.

#### Bonus Features
- **B1. Auto‑fix PR bot** — **Difficulty 3/5**
  - **Teaches:** Patch generation and PR creation.
  - **Acceptance:** Bot submits fixes; reviewers approve.
- **B2. DAST stub** — **Difficulty 3/5**
  - **Teaches:** Runtime checks; OWASP top‑10 probes.
  - **Acceptance:** Sample web app scanned with findings.
- **B3. Policy exceptions workflow** — **Difficulty 2/5**
  - **Teaches:** Approval/expiry.
  - **Acceptance:** Exceptions tracked and reviewed.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 21) Cost‑Aware Autoscaling Simulator
**What you’re building:** Simulate autoscaling under budgets and workloads.
**Core skills:** Queueing theory, scaling policies, plotting.

#### Required Features
- **R1. Workload & service model** — **Difficulty 3/5**
  - **What it teaches:**
    - Arrival processes, service times, queues.
  - **Acceptance criteria:**
    - Sim matches analytical expectations on simple M/M/1 cases.

- **R2. Scaling policies** — **Difficulty 3/5**
  - **What it teaches:**
    - Threshold/predictive scaling; cooldown; min/max bounds.
  - **Acceptance criteria:**
    - Policies configurable; stability under oscillation.

- **R3. Cost model** — **Difficulty 2/5**
  - **What it teaches:**
    - Instance/hour, egress, storage; energy (optional).
  - **Acceptance criteria:**
    - Cost tracked per scenario; plotted with SLA.

- **R4. SLA vs cost frontier** — **Difficulty 2/5**
  - **What it teaches:**
    - Pareto frontier visualization.
  - **Acceptance criteria:**
    - Frontier chart produced; scenario runner outputs CSV.

#### Bonus Features
- **B1. RL policy search** — **Difficulty 4/5**
  - **Teaches:** Bandits/RL for scaling.
  - **Acceptance:** Outperforms heuristics on synthetic workloads.
- **B2. Multi‑tier microservices** — **Difficulty 3/5**
  - **Teaches:** Cascading queues; bottlenecks.
  - **Acceptance:** Upstream/downstream interactions captured.
- **B3. Spot/preemptible economics** — **Difficulty 3/5**
  - **Teaches:** Interrupted instances; checkpointing.
  - **Acceptance:** Cost savings vs reliability charted.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 22) Chaos Engineering Toolkit
**What you’re building:** Inject faults and run resilience experiments.
**Core skills:** Failure modes, experiments, observability.

#### Required Features
- **R1. Fault injectors** — **Difficulty 3/5**
  - **What it teaches:**
    - CPU/memory pressure, kill, latency, packet loss.
  - **Acceptance criteria:**
    - Faults scoped by target with TTL; revert cleanly.

- **R2. Steady‑state checks** — **Difficulty 2/5**
  - **What it teaches:**
    - Defining measurable steady state and abort conditions.
  - **Acceptance criteria:**
    - Experiment aborts on SLO breach; logs/metrics captured.

- **R3. Blast radius & safety** — **Difficulty 2/5**
  - **What it teaches:**
    - Guardrails, allow‑lists, scheduling windows.
  - **Acceptance criteria:**
    - No experiments outside allowed scope/time.

- **R4. Reporting** — **Difficulty 2/5**
  - **What it teaches:**
    - Experiment results, learnings, action items.
  - **Acceptance criteria:**
    - Markdown/HTML report generated with outcomes.

#### Bonus Features
- **B1. Hypothesis generator** — **Difficulty 3/5**
  - **Teaches:** Suggesting likely weak points.
  - **Acceptance:** Hypotheses formulated from SLOs/topology.
- **B2. Real‑time guardrails** — **Difficulty 3/5**
  - **Teaches:** Pause/rollback on metrics symptoms.
  - **Acceptance:** Auto‑abort triggers verified in tests.
- **B3. Orchestrator integration** — **Difficulty 3/5**
  - **Teaches:** Kubernetes/Compose hooks.
  - **Acceptance:** Run chaos as a job with RBAC.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 23) Multi‑Region Active‑Active Demo
**What you’re building:** Two regions with conflict resolution.
**Core skills:** Replication, CRDTs, traffic routing, failover.

#### Required Features
- **R1. Replication strategy** — **Difficulty 4/5**
  - **What it teaches:**
    - Oplog streams vs CRDT types; convergence.
  - **Acceptance criteria:**
    - Regions converge after partitions; conflicts resolved deterministically.

- **R2. Traffic routing** — **Difficulty 3/5**
  - **What it teaches:**
    - Weighted/geo routing; health checks.
  - **Acceptance criteria:**
    - Traffic shifts on fail; sticky sessions handled.

- **R3. Failover drills** — **Difficulty 3/5**
  - **What it teaches:**
    - Runbooks, RTO/RPO validation.
  - **Acceptance criteria:**
    - Drills executed; RTO/RPO met; audit logged.

- **R4. Consistency docs & invariants** — **Difficulty 2/5**
  - **What it teaches:**
    - Read/write models, client expectations.
  - **Acceptance criteria:**
    - Documented invariants with examples and failure modes.

#### Bonus Features
- **B1. Partition simulations** — **Difficulty 3/5**
  - **Teaches:** Nemesis scenarios; chaos in network.
  - **Acceptance:** Outcomes recorded; learnings fed back into design.
- **B2. Vector clocks/lamport clocks** — **Difficulty 3/5**
  - **Teaches:** Causality reasoning.
  - **Acceptance:** Causal ordering shown in examples.
- **B3. Eventually consistent caches** — **Difficulty 2/5**
  - **Teaches:** TTLs, staleness windows.
  - **Acceptance:** Client cache policy documented and tested.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 24) Privacy‑Preserving Analytics
**What you’re building:** Aggregate metrics with differential privacy.
**Core skills:** DP mechanisms, sensitivity, epsilon accounting.

#### Required Features
- **R1. Mechanism (Laplace/Gaussian)** — **Difficulty 3/5**
  - **What it teaches:**
    - Sensitivity bounds; noise calibration.
  - **Acceptance criteria:**
    - Tests validate privacy budget vs error trade‑off.

- **R2. Composition/accounting** — **Difficulty 3/5**
  - **What it teaches:**
    - Budget tracking across queries; advanced composition.
  - **Acceptance criteria:**
    - Budgets enforced per user/session with audit trail.

- **R3. DP query API** — **Difficulty 3/5**
  - **What it teaches:**
    - Enforcing privacy at API; denial on exhausted budget.
  - **Acceptance criteria:**
    - API refuses over‑budget requests; returns calibrated results otherwise.

- **R4. Utility vs privacy plots** — **Difficulty 2/5**
  - **What it teaches:**
    - MSE vs epsilon curves; policy selection.
  - **Acceptance criteria:**
    - Plots generated and explained in README.

#### Bonus Features
- **B1. Federated learning sim** — **Difficulty 4/5**
  - **Teaches:** FedAvg; secure aggregation.
  - **Acceptance:** Round‑based training with DP noise; convergence shown.
- **B2. Membership inference tests** — **Difficulty 3/5**
  - **Teaches:** Attacks; mitigation evaluation.
  - **Acceptance:** Attack success rate reduced with DP.
- **B3. K‑anonymity lints** — **Difficulty 2/5**
  - **Teaches:** Static checks before DP.
  - **Acceptance:** Risky columns flagged with guidance.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 25) Observability Platform
**What you’re building:** Unified pipelines for logs/metrics/traces with SLOs.
**Core skills:** OTEL collectors, exporters, SLO math, runbooks.

#### Required Features
- **R1. Collectors & pipelines** — **Difficulty 3/5**
  - **What it teaches:**
    - OTEL config for receivers/processors/exporters.
  - **Acceptance criteria:**
    - Data flows end‑to‑end; dropped spans/metrics < threshold.

- **R2. Logs/metrics/traces unification** — **Difficulty 3/5**
  - **What it teaches:**
    - Correlation via trace IDs; exemplars.
  - **Acceptance criteria:**
    - From a log you can jump to a trace and related metrics.

- **R3. SLOs & burn‑rate alerts** — **Difficulty 3/5**
  - **What it teaches:**
    - Error budget math; multi‑window multi‑burn rules.
  - **Acceptance criteria:**
    - Alerts fire appropriately in test; runbook linked.

- **R4. Dashboards & runbooks** — **Difficulty 2/5**
  - **What it teaches:**
    - Golden signals dashboards; incident docs.
  - **Acceptance criteria:**
    - Dashboards cover latency, error rate, saturation; runbooks reviewed.

#### Bonus Features
- **B1. Auto‑instrumentation playbooks** — **Difficulty 2/5**
  - **Teaches:** Language‑specific guidance.
  - **Acceptance:** Two sample apps instrumented via playbook.
- **B2. Ingestion gateway** — **Difficulty 3/5**
  - **Teaches:** Rate limits, tenants, auth on ingest.
  - **Acceptance:** Gateway protects backends; per‑tenant quotas visible.
- **B3. Cardinality controls** — **Difficulty 3/5**
  - **Teaches:** Label whitelists; top‑k.
  - **Acceptance:** Cardinality alerts prevent backend overload.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 26) Platform Starter Kits
**What you’re building:** Cookiecutters/templates for teams to bootstrap secure apps.
**Core skills:** Cookiecutter, templates, docs, DX design.

#### Required Features
- **R1. Templates with secure defaults** — **Difficulty 2/5**
  - **What it teaches:**
    - App skeletons with logging, metrics, health checks, security headers.
  - **Acceptance criteria:**
    - New app passes lint/tests/security scans out of the box.

- **R2. CI/CD included** — **Difficulty 2/5**
  - **What it teaches:**
    - GH Actions with tests, lint, build, release.
  - **Acceptance criteria:**
    - Generated repo has working CI on first push.

- **R3. DX & docs** — **Difficulty 2/5**
  - **What it teaches:**
    - READMEs, issue templates, pre‑commit, contribution guide.
  - **Acceptance criteria:**
    - New devs can ship a feature in < 1 day following docs.

- **R4. Update mechanism** — **Difficulty 2/5**
  - **What it teaches:**
    - Template versioning and upgrade commands.
  - **Acceptance criteria:**
    - Existing projects can pull template updates with minimal conflicts.

#### Bonus Features
- **B1. Internal portal UI** — **Difficulty 3/5**
  - **Teaches:** Self‑service scaffolding with RBAC.
  - **Acceptance:** Portal provisions repos with correct settings.
- **B2. Telemetry & governance** — **Difficulty 2/5**
  - **Teaches:** Template usage metrics; policy checks.
  - **Acceptance:** Reports show adoption; non‑compliant repos flagged.
- **B3. Plugin architecture** — **Difficulty 3/5**
  - **Teaches:** Extensible generators via entry points.
  - **Acceptance:** Teams add plugins without forking template.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
