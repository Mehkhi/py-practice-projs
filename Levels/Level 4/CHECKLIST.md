# Level 4 — Advanced (Senior Engineer)

Design for scale, reliability, and performance. Multiple services, observability, security, and data pipelines. Expect Docker, clouds (local emulation), and strong testing.

## Checklist

- [ ] 1. FastAPI Production API
  - What you build: JWT auth, roles, rate limit, and versioned endpoints.
  - Skills: FastAPI, JWT/OAuth2, pydantic models, dependency injection.
  - Milestones: Pagination/filter; validation; error mapping; OpenAPI docs.
  - Stretch goals: E2E tests with httpx + pytest.

- [ ] 2. GraphQL Service
  - What you build: Expose a GraphQL schema over existing data.
  - Skills: strawberry/graphene, resolvers, batching.
  - Milestones: Schema stitching; caching; dataloaders.
  - Stretch goals: Subscriptions via WebSockets.

- [ ] 3. gRPC Microservices Pair
  - What you build: User and Order services communicating over gRPC.
  - Skills: protobuf, gRPC, contracts, backward‑compatibility.
  - Milestones: Client libs; retries; deadlines; interceptors.
  - Stretch goals: Service mesh locally (Envoy).

- [ ] 4. Event Pipeline with Kafka
  - What you build: Ingest, transform, and sink events to a DB.
  - Skills: Kafka, producers/consumers, schemas, partitions.
  - Milestones: Exactly‑once semantics (discussion + at‑least‑once impl).
  - Stretch goals: Out‑of‑order handling with watermarking.

- [ ] 5. Search Service
  - What you build: Index documents and serve ranked search results.
  - Skills: Elasticsearch/OpenSearch, analyzers, query DSL.
  - Milestones: Highlighting; synonyms; pagination.
  - Stretch goals: Relevance tuning and evaluation.

- [ ] 6. Recommendations (CF)
  - What you build: Collaborative filtering movie/book recommender.
  - Skills: pandas, sparse matrices, cosine similarity.
  - Milestones: Cold‑start strategy; evaluation metrics.
  - Stretch goals: Implicit feedback (ALS) variant.

- [ ] 7. Realtime Dashboard
  - What you build: WebSocket stream of live metrics to frontend.
  - Skills: FastAPI websockets, pub/sub, backpressure.
  - Milestones: Reconnect logic; auth; history buffer.
  - Stretch goals: Server‑sent events fallback.

- [ ] 8. Feature Flags Service
  - What you build: Toggle features per user/segment with caching.
  - Skills: RBAC, caching (Redis), evaluation rules.
  - Milestones: Audit log; percentage rollouts.
  - Stretch goals: Targeting expressions DSL.

- [ ] 9. Stripe‑like Payments (Test Mode)
  - What you build: Create checkout sessions and verify webhooks.
  - Skills: webhooks, signature verify, idempotency keys.
  - Milestones: Receipts; refunds; error simulation.
  - Stretch goals: Retry/compensation transactions.

- [ ] 10. Multi‑Tenant SaaS
  - What you build: Isolate tenants in one DB (RLS or schema‑per‑tenant).
  - Skills: SQLAlchemy, tenancy models, security.
  - Milestones: Billing per tenant; quotas; audit trails.
  - Stretch goals: Tenant migrations automation.

- [ ] 11. Infra as Code (Pulumi/Terraform)
  - What you build: Provision app infra via code, reproducibly.
  - Skills: Pulumi/Terraform basics, state mgmt, modules.
  - Milestones: Dev/prod stacks; secrets; outputs.
  - Stretch goals: Policy as code checks.

- [ ] 12. Observability Stack
  - What you build: Logging, metrics, traces with OpenTelemetry.
  - Skills: Prometheus client, OTEL, context propagation.
  - Milestones: Dashboards; alert rules; SLO definitions.
  - Stretch goals: Trace‑based sampling strategies.

- [ ] 13. Data Pipeline with Airflow/Prefect
  - What you build: ETL DAG that moves and transforms data daily.
  - Skills: operators, retries, scheduling, XCom/artifacts.
  - Milestones: Backfills; parameterized runs.
  - Stretch goals: Data quality checks with Great Expectations.

- [ ] 14. ML Model Serving
  - What you build: Serve a versioned ML model behind an API.
  - Skills: FastAPI, model registry, pydantic, AB testing.
  - Milestones: Shadow traffic; metrics; drift alerts.
  - Stretch goals: Canary deploys with rollback.

- [ ] 15. Image Processing Pipeline
  - What you build: Transform images: resize, filters, OCR.
  - Skills: Pillow/OpenCV, queues, throughput tuning.
  - Milestones: Parallel workers; retries; metrics.
  - Stretch goals: GPU acceleration exploration.

- [ ] 16. Geospatial Routing
  - What you build: Shortest path between coordinates on a road graph.
  - Skills: osmnx, networkx, heuristics (A*).
  - Milestones: Avoid tolls; elevation cost; plotting routes.
  - Stretch goals: Turn‑by‑turn instruction generator.

- [ ] 17. Message Broker Workers
  - What you build: Producer/consumer system with RabbitMQ/Redis.
  - Skills: ack/requeue, dead letters, delivery modes.
  - Milestones: Exactly‑once illusions (idempotency).
  - Stretch goals: Priority queues and delayed messages.

- [ ] 18. Distributed Locks
  - What you build: Protect critical sections with Redis locks.
  - Skills: Redlock patterns, TTLs, fencing tokens.
  - Milestones: Renewal; lock contention tests.
  - Stretch goals: Lease‑based caches.

- [ ] 19. Sharding & Partitioning
  - What you build: Split data by key across DBs/partitions.
  - Skills: hashing, routing, rebalancing.
  - Milestones: Locality vs balance tradeoffs; metrics.
  - Stretch goals: Resharding without downtime (demo).

- [ ] 20. Cython Acceleration
  - What you build: Speed up a hot loop with Cython extension.
  - Skills: profiling, Cython types, build toolchain.
  - Milestones: 10x speedup; correctness tests.
  - Stretch goals: Compare PyPy/Numba variants.

- [ ] 21. Async DB Layer
  - What you build: Use async SQLAlchemy/SQLModel with connection pools.
  - Skills: async engines, transactions, pooling.
  - Milestones: Timeouts; retry; circuit breaker.
  - Stretch goals: Read replicas / write master split.

- [ ] 22. Security Hardening
  - What you build: Secrets mgmt, dependency scanning, input validation.
  - Skills: Bandit, pip‑audit, pydantic validators.
  - Milestones: CSP headers; secure cookies; CSRF tokens.
  - Stretch goals: Signed requests between services.

- [ ] 23. Caching Strategies
  - What you build: Local and Redis cache with invalidation rules.
  - Skills: TTL, LRU, cache stampede prevention.
  - Milestones: Write‑through vs write‑back; metrics.
  - Stretch goals: Hierarchical cache (L1/L2).

- [ ] 24. Blue/Green Deploy (Compose)
  - What you build: Switch traffic between two app versions safely.
  - Skills: nginx routing, healthchecks, rollback.
  - Milestones: Smoke tests; drain connections.
  - Stretch goals: Canary with percentage rollout.

- [ ] 25. Data Lake to Parquet + DuckDB
  - What you build: Ingest CSV→Parquet and query fast with DuckDB.
  - Skills: pandas, pyarrow, partitioning, SQL queries.
  - Milestones: Partition by date; statistics; manifest.
  - Stretch goals: Delta/iceberg style table basics (concept).

---

## Detailed Spec Sheets — Level 4 (Advanced)

This section expands each Level‑4 checklist item into an implementation spec with **required features** and **bonus features**. Every feature includes a **difficulty rating**, an **extensive breakdown of what it teaches**, and **acceptance criteria** you can self‑verify.

### Difficulty Legend
- **1** = Very easy (few lines, minimal edge cases)
- **2** = Easy (simple logic, basic edge cases)
- **3** = Moderate (multiple components, careful handling)
- **4** = Hard (non‑trivial algorithms/design, extensive testing)
- **5** = Very hard (complex algorithms or architecture)

### Common Requirements for Project Completion
- All **required features** implemented and demonstrated.
- At least **10 tests** per project, including **unit + integration**; add **load tests** when applicable.
- Clear **README** with architecture diagram, run steps (dev/prod), and operational runbooks.
- Code formatted with **black** and linted with **ruff/flake8**; imports via **isort**.
- Public APIs and key modules include **type hints**; `mypy` (or `pyright`) passes or exceptions are documented.
- **Observability**: structured logs, metrics counters, and at least one trace for a key path.
- **Security**: secret handling, least privilege, input validation, and dependency scans documented.

> Tip: Track each feature as a GitHub issue. Label with `difficulty/x`, `type/required` or `type/bonus`.

---

### 1) FastAPI Production API
**What you’re building:** JWT‑secured API with roles, rate limit, and versioned endpoints.
**Core skills:** FastAPI, OAuth2/JWT, DI, pydantic, error mapping.

#### Required Features
- **R1. Auth & roles (JWT/OAuth2)** — **Difficulty 3/5**
  - **Teaches:** Token issuance/verification, scopes, refresh vs short‑lived tokens.
  - **Acceptance:** Protected endpoints require valid JWT; role‑gated routes enforced; token expiry honored.
- **R2. Validation & error mapping** — **Difficulty 2/5**
  - **Teaches:** Pydantic models/validators; converting exceptions to JSON errors.
  - **Acceptance:** 4xx/5xx payloads follow a consistent schema; field errors show paths.
- **R3. Pagination/filter/sort** — **Difficulty 2/5**
  - **Teaches:** Stable ordering, limits/offsets, defensive defaults.
  - **Acceptance:** `?limit&offset&sort` work; out‑of‑range values clamped; responses include paging hints.
- **R4. Versioned API & rate limiting** — **Difficulty 3/5**
  - **Teaches:** `/v1` vs `/v2` routing, deprecation headers; client throttling.
  - **Acceptance:** Separate routers for versions; 429 returned on limit with `Retry‑After`.

#### Bonus Features
- **B1. E2E tests with httpx + pytest** — **Difficulty 2/5**
  - **Teaches:** Test client, fixtures, token generation, happy/error paths.
  - **Acceptance:** CI runs green; coverage includes auth + pagination.
- **B2. Request/response logging & correlation IDs** — **Difficulty 2/5**
  - **Teaches:** Middleware for IDs; log context propagation.
  - **Acceptance:** Logs show ID across request lifecycle; sample trace linked.
- **B3. OpenAPI enhancements** — **Difficulty 2/5**
  - **Teaches:** Examples, error schemas, doc tags.
  - **Acceptance:** `/docs` shows examples; clients can be generated.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 2) GraphQL Service
**What you’re building:** GraphQL schema over existing data/services.
**Core skills:** Strawberry/Graphene, resolvers, batching, caching.

#### Required Features
- **R1. Schema design & types** — **Difficulty 3/5**
  - **Teaches:** Object types, connections, pagination patterns.
  - **Acceptance:** SDL rendered; non‑null where appropriate; docs strings present.
- **R2. Resolvers & dataloaders** — **Difficulty 3/5**
  - **Teaches:** N+1 mitigation via batching/caching.
  - **Acceptance:** N+1 reduced vs naive; verified by logs/metrics.
- **R3. Authorization & query limits** — **Difficulty 3/5**
  - **Teaches:** Field‑level auth; complexity/depth limits.
  - **Acceptance:** Unauthorized fields hidden; deep/expensive queries blocked politely.
- **R4. Error handling & extensions** — **Difficulty 2/5**
  - **Teaches:** Returning partial data with errors; tracing extensions.
  - **Acceptance:** Errors surfaced in `errors[]`; tracing metadata present.

#### Bonus Features
- **B1. Schema stitching/federation** — **Difficulty 4/5**
  - **Teaches:** Composing schemas across services.
  - **Acceptance:** Queries span two sources with proper ownership.
- **B2. Caching of resolvers** — **Difficulty 2/5**
  - **Teaches:** TTL/per‑user cache keys; invalidation signals.
  - **Acceptance:** Hit/miss metrics improve latency.
- **B3. Subscriptions** — **Difficulty 3/5**
  - **Teaches:** WebSockets; pub/sub patterns.
  - **Acceptance:** Clients receive live updates; reconnect logic tested.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 3) gRPC Microservices Pair
**What you’re building:** User and Order services communicating over gRPC.
**Core skills:** Protobuf contracts, gRPC servers/clients, compatibility.

#### Required Features
- **R1. Protos & codegen** — **Difficulty 2/5**
  - **Teaches:** Service/Message design; reserved fields; backward compatibility.
  - **Acceptance:** `protoc`/`grpclib` generate clients/servers; versions documented.
- **R2. Server stubs & interceptors** — **Difficulty 3/5**
  - **Teaches:** Auth interceptors, deadlines, metadata.
  - **Acceptance:** Deadline exceeded handled; auth metadata required.
- **R3. Retries & idempotency** — **Difficulty 3/5**
  - **Teaches:** Retryable vs non‑retryable codes; idempotent method design.
  - **Acceptance:** Policies enforced; retries visible in logs.
- **R4. Client libraries** — **Difficulty 2/5**
  - **Teaches:** Packaging clients; timeouts; connection reuse.
  - **Acceptance:** Example app consumes both services with timeouts set.

#### Bonus Features
- **B1. Contract tests** — **Difficulty 3/5**
  - **Teaches:** Provider/consumer tests; golden responses.
  - **Acceptance:** Breaking proto changes caught in CI.
- **B2. Load testing** — **Difficulty 2/5**
  - **Teaches:** ghz/vegeta scenarios; latency SLOs.
  - **Acceptance:** Report with p95/p99 and throughput.
- **B3. Local mesh (Envoy)** — **Difficulty 4/5**
  - **Teaches:** mTLS, retries at proxy, circuit breaking.
  - **Acceptance:** Requests succeed through Envoy with policies applied.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 4) Event Pipeline with Kafka
**What you’re building:** Ingest → transform → sink events reliably.
**Core skills:** Kafka producers/consumers, schemas, partitions.

#### Required Features
- **R1. Producer & schema** — **Difficulty 3/5**
  - **Teaches:** Avro/JSON schemas; keys vs values; partition strategy.
  - **Acceptance:** Validated messages published; partitions balanced by key.
- **R2. Consumer with backoff** — **Difficulty 3/5**
  - **Teaches:** Commit strategies; retries; poison queue handling.
  - **Acceptance:** At‑least‑once semantics; DLQ on repeated failures.
- **R3. Transform & sink** — **Difficulty 2/5**
  - **Teaches:** Stateless transform; idempotent upserts to DB.
  - **Acceptance:** Duplicate events don’t create dup rows.
- **R4. Replay & backfill** — **Difficulty 3/5**
  - **Teaches:** Offsets, reprocessing windows, exactly‑once illusions.
  - **Acceptance:** Backfill job replays safely; metrics emitted.

#### Bonus Features
- **B1. Schema registry + compat checks** — **Difficulty 3/5**
  - **Teaches:** Backward/forward compatibility; schema evolution.
  - **Acceptance:** Incompatible schema fails CI; migration plan documented.
- **B2. Out‑of‑order handling** — **Difficulty 4/5**
  - **Teaches:** Watermarks; event time vs processing time.
  - **Acceptance:** Late events merged according to policy.
- **B3. Exactly‑once (concept → demo)** — **Difficulty 4/5**
  - **Teaches:** Transactions; idempotent producers; sinks.
  - **Acceptance:** Demo shows no duplicates under failures.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 5) Search Service
**What you’re building:** Index documents and serve ranked results.
**Core skills:** Elasticsearch/OpenSearch, analyzers, queries, ranking.

#### Required Features
- **R1. Index design & analyzers** — **Difficulty 3/5**
  - **Teaches:** Tokenizers, filters, language analyzers, mappings.
  - **Acceptance:** Index created with appropriate mappings; reindex script exists.
- **R2. Ingest pipeline** — **Difficulty 2/5**
  - **Teaches:** Normalization, stemming, enrichment.
  - **Acceptance:** Docs ingested with IDs; updates merge correctly.
- **R3. Query DSL & pagination** — **Difficulty 3/5**
  - **Teaches:** bool queries, filters vs queries, highlights.
  - **Acceptance:** Queries return highlights; consistent sort; pages stable.
- **R4. Relevance evaluation** — **Difficulty 3/5**
  - **Teaches:** Judgments, offline metrics, A/B hooks.
  - **Acceptance:** Report with NDCG/MRR for a labeled set.

#### Bonus Features
- **B1. Synonyms & spell correction** — **Difficulty 3/5**
  - **Teaches:** Synonym filters; fuzzy matching.
  - **Acceptance:** Misspellings still retrieve relevant docs.
- **B2. Field boosts** — **Difficulty 2/5**
  - **Teaches:** Title boosts; recency boosting.
  - **Acceptance:** Boosts measurably improve quality on eval set.
- **B3. Index lifecycle mgmt** — **Difficulty 3/5**
  - **Teaches:** Hot/warm/cold tiers; rollover.
  - **Acceptance:** Index rollover and retention policy tested.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 6) Recommendations (CF)
**What you’re building:** Collaborative filtering recommender (movies/books).
**Core skills:** Pandas, sparse matrices, cosine similarity, evaluation.

#### Required Features
- **R1. Data loading & sparsity handling** — **Difficulty 2/5**
  - **Teaches:** User‑item matrices, implicit zeros, memory.
  - **Acceptance:** Sparse format used; stats printed (density, users/items).
- **R2. Similarity & top‑N** — **Difficulty 3/5**
  - **Teaches:** Cosine sim; nearest neighbors; cold‑start policy.
  - **Acceptance:** Top‑N per user generated; cold‑start documented.
- **R3. Evaluation metrics** — **Difficulty 3/5**
  - **Teaches:** Precision@K, Recall@K, MAP, offline splits.
  - **Acceptance:** Report comparing baselines; seed reproducibility.
- **R4. Serving API** — **Difficulty 2/5**
  - **Teaches:** FastAPI endpoint for recommendations with caching.
  - **Acceptance:** p95 latency target met on sample workload.

#### Bonus Features
- **B1. Implicit feedback (ALS)** — **Difficulty 4/5**
  - **Teaches:** Alternating least squares for implicit data.
  - **Acceptance:** Offline metrics outperform cosine baseline.
- **B2. Hybrid signals** — **Difficulty 3/5**
  - **Teaches:** Content + CF blending.
  - **Acceptance:** Weighted blend improves specific segments.
- **B3. Re‑rankers** — **Difficulty 3/5**
  - **Teaches:** Business rules, diversity/novelty boosts.
  - **Acceptance:** Diversity metrics reported and tunable.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 7) Realtime Dashboard
**What you’re building:** Live metrics to frontend via WebSockets.
**Core skills:** FastAPI WebSockets, pub/sub, backpressure.

#### Required Features
- **R1. WebSocket server & auth** — **Difficulty 3/5**
  - **Teaches:** Connection lifecycle, token auth, origin checks.
  - **Acceptance:** Unauthorized connections denied; ping/pong keep‑alive.
- **R2. Pub/sub bridge** — **Difficulty 3/5**
  - **Teaches:** Channel fan‑out; topic subscriptions.
  - **Acceptance:** Clients receive only subscribed topics.
- **R3. Backpressure & rate limits** — **Difficulty 3/5**
  - **Teaches:** Drop/queue policies; slow consumer handling.
  - **Acceptance:** Slow clients don’t degrade server; metrics prove it.
- **R4. History buffer** — **Difficulty 2/5**
  - **Teaches:** Ring buffers; replay on connect.
  - **Acceptance:** New client receives last N events per topic.

#### Bonus Features
- **B1. SSE fallback** — **Difficulty 2/5**
  - **Teaches:** Server‑sent events as alternative.
  - **Acceptance:** Older browsers receive updates via SSE.
- **B2. Compression & batching** — **Difficulty 2/5**
  - **Teaches:** Message packing; trade‑offs.
  - **Acceptance:** Reduced bandwidth with acceptable latency.
- **B3. Frontend sample app** — **Difficulty 2/5**
  - **Teaches:** Minimal client; reconnect logic.
  - **Acceptance:** Demo shows charts updating live.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 8) Feature Flags Service
**What you’re building:** Targeted feature toggles with caching and audit.
**Core skills:** RBAC, Redis caching, evaluation rules.

#### Required Features
- **R1. Flag model & API** — **Difficulty 2/5**
  - **Teaches:** Flag states, targeting rules, constraints.
  - **Acceptance:** CRUD for flags; JSON schema documented.
- **R2. Evaluation engine** — **Difficulty 3/5**
  - **Teaches:** Rule evaluation, percentage rollouts, bucketing by user ID.
  - **Acceptance:** Deterministic results for same user; tests for edge cases.
- **R3. Caching & invalidation** — **Difficulty 2/5**
  - **Teaches:** Redis cache; ETags; per‑tenant separation.
  - **Acceptance:** Changes propagate within TTL; metrics on hits/misses.
- **R4. Audit log** — **Difficulty 2/5**
  - **Teaches:** Who/what/when logging; compliance.
  - **Acceptance:** All changes recorded with actor and diff.

#### Bonus Features
- **B1. Targeting DSL** — **Difficulty 4/5**
  - **Teaches:** Expression parser; safe evaluation.
  - **Acceptance:** Complex rules parsed and evaluated predictably.
- **B2. SDKs for clients** — **Difficulty 3/5**
  - **Teaches:** Cached polling; bootstrapping.
  - **Acceptance:** Example app uses SDK; startup fetch cached.
- **B3. Admin UI** — **Difficulty 3/5**
  - **Teaches:** Simple UI for flag edits and audit view.
  - **Acceptance:** Role‑gated UI changes flags and logs events.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 9) Stripe‑like Payments (Test Mode)
**What you’re building:** Test‑mode checkout sessions with webhook verification.
**Core skills:** Webhooks, signature verification, idempotency.

#### Required Features
- **R1. Checkout session & redirect** — **Difficulty 2/5**
  - **Teaches:** Creating sessions, returning success/cancel URLs.
  - **Acceptance:** Users reach hosted checkout and return to app with state.
- **R2. Webhook verification** — **Difficulty 3/5**
  - **Teaches:** Signing secrets, replay attack prevention.
  - **Acceptance:** Invalid signatures rejected; webhook retries handled.
- **R3. Idempotent operations** — **Difficulty 3/5**
  - **Teaches:** Idempotency keys; dedup of retries.
  - **Acceptance:** Replayed webhooks do not duplicate charges/orders.
- **R4. Receipts/refunds** — **Difficulty 2/5**
  - **Teaches:** Post‑payment flows; refund records.
  - **Acceptance:** Receipts stored; refunds update state and audit.

#### Bonus Features
- **B1. Error simulation** — **Difficulty 2/5**
  - **Teaches:** Simulating failures/timeouts to test resiliency.
  - **Acceptance:** Scenarios documented; system recovers as expected.
- **B2. Test cards catalog** — **Difficulty 1/5**
  - **Teaches:** QA coverage for payment cases.
  - **Acceptance:** List of test numbers and outcomes shown.
- **B3. Compensation transactions** — **Difficulty 3/5**
  - **Teaches:** Saga design for partial failures.
  - **Acceptance:** Failed steps compensated in order; idempotent.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 10) Multi‑Tenant SaaS
**What you’re building:** Single app hosting multiple tenants safely.
**Core skills:** SQLAlchemy, tenancy models, security boundaries.

#### Required Features
- **R1. Tenant isolation model** — **Difficulty 3/5**
  - **Teaches:** RLS (row‑level security) or schema‑per‑tenant; pros/cons.
  - **Acceptance:** Cross‑tenant data access prevented; tests enforce isolation.
- **R2. Tenant onboarding & quotas** — **Difficulty 2/5**
  - **Teaches:** Provisioning flows; per‑tenant limits.
  - **Acceptance:** Quotas enforced; errors explain limits.
- **R3. Billing hooks** — **Difficulty 2/5**
  - **Teaches:** Usage metering; invoicing hooks.
  - **Acceptance:** Usage recorded per tenant; monthly reports.
- **R4. Audit trails** — **Difficulty 2/5**
  - **Teaches:** Per‑tenant audit logs with actors.
  - **Acceptance:** Readable trail for sensitive actions.

#### Bonus Features
- **B1. Tenant migrations automation** — **Difficulty 3/5**
  - **Teaches:** Rolling schema updates tenant‑by‑tenant.
  - **Acceptance:** Progress logged; rollback procedure verified.
- **B2. Custom domains** — **Difficulty 2/5**
  - **Teaches:** Domain verification; SSL certs.
  - **Acceptance:** Tenant’s domain serves app securely.
- **B3. Data export/import** — **Difficulty 2/5**
  - **Teaches:** Per‑tenant backups; portability.
  - **Acceptance:** Tenant can export/import their data.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 11) Infra as Code (Pulumi/Terraform)
**What you’re building:** Reproducible infra stacks as code.
**Core skills:** State mgmt, modules, secrets, environments.

#### Required Features
- **R1. Module structure** — **Difficulty 2/5**
  - **Teaches:** Reusable modules and inputs/outputs.
  - **Acceptance:** Stacks compose modules; outputs documented.
- **R2. State & backends** — **Difficulty 2/5**
  - **Teaches:** Remote state storage; locking.
  - **Acceptance:** State stored remotely; locked during apply.
- **R3. Secrets mgmt** — **Difficulty 2/5**
  - **Teaches:** Encrypted variables; no secrets in VCS.
  - **Acceptance:** `terraform validate`/`pulumi config` secure.
- **R4. Dev/prod stacks** — **Difficulty 2/5**
  - **Teaches:** Per‑env configs; drift detection.
  - **Acceptance:** `plan` shows clean diffs; prod locked from accidental destroys.

#### Bonus Features
- **B1. Policy as code** — **Difficulty 3/5**
  - **Teaches:** OPA/Conftest checks.
  - **Acceptance:** CI fails on policy violations.
- **B2. Blueprints/templates** — **Difficulty 2/5**
  - **Teaches:** Starter stacks for common services.
  - **Acceptance:** New proj bootstraps in minutes.
- **B3. Cost estimates** — **Difficulty 2/5**
  - **Teaches:** Infracost integration.
  - **Acceptance:** PRs show cost delta.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 12) Observability Stack
**What you’re building:** Logs, metrics, traces with OTEL.
**Core skills:** Prometheus client, OpenTelemetry, dashboards, SLOs.

#### Required Features
- **R1. Structured logs & sampling** — **Difficulty 2/5**
  - **Teaches:** JSON logs, sampling noisy events.
  - **Acceptance:** Logs parse in ELK; sampling reduces volume.
- **R2. Metrics & alerts** — **Difficulty 3/5**
  - **Teaches:** Counters/gauges/histograms; alert rules.
  - **Acceptance:** Dashboards show rates/latencies; alert fires in test.
- **R3. Tracing & context propagation** — **Difficulty 3/5**
  - **Teaches:** Span attributes, baggage, cross‑service context.
  - **Acceptance:** End‑to‑end trace visualized across two services.
- **R4. SLOs** — **Difficulty 3/5**
  - **Teaches:** Error budgets; burn‑rate alerts.
  - **Acceptance:** SLO doc + alerts for fast/slow burn.

#### Bonus Features
- **B1. Trace‑based sampling** — **Difficulty 3/5**
  - **Teaches:** Tail sampling; keeping interesting traces.
  - **Acceptance:** Policy retains slow/outlier traces.
- **B2. Logs→traces correlation** — **Difficulty 2/5**
  - **Teaches:** Trace IDs in logs; clickable links.
  - **Acceptance:** Jump from log to trace in UI.
- **B3. Synthetic probes** — **Difficulty 2/5**
  - **Teaches:** Black‑box checks for key endpoints.
  - **Acceptance:** Synthetic monitors charted; alerts hooked.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 13) Data Pipeline with Airflow/Prefect
**What you’re building:** ETL DAG that runs daily with retries and backfills.
**Core skills:** Operators, scheduling, XCom/artifacts, parametrization.

#### Required Features
- **R1. DAG with tasks & retries** — **Difficulty 2/5**
  - **Teaches:** Idempotent tasks; exponential backoff.
  - **Acceptance:** Failures retried per policy; alerts on final failure.
- **R2. Parameterized runs** — **Difficulty 2/5**
  - **Teaches:** Templated params; date windows.
  - **Acceptance:** CLI/UI can run for arbitrary dates.
- **R3. Backfills** — **Difficulty 2/5**
  - **Teaches:** Historical reprocessing with guards.
  - **Acceptance:** Backfill job completes without duplicate loads.
- **R4. Artifacts & lineage** — **Difficulty 2/5**
  - **Teaches:** Persisting outputs; metadata for lineage.
  - **Acceptance:** Artifacts visible; lineage graph generated.

#### Bonus Features
- **B1. Data quality checks (GE)** — **Difficulty 3/5**
  - **Teaches:** Expectations, failing gates.
  - **Acceptance:** Failing checks stop pipeline with report.
- **B2. SLAs & alerts** — **Difficulty 2/5**
  - **Teaches:** Task SLAs and alert routing.
  - **Acceptance:** SLA misses alert on channel.
- **B3. Dynamic task mapping** — **Difficulty 3/5**
  - **Teaches:** Fan‑out per partition/file.
  - **Acceptance:** Scale with N partitions; results collated.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 14) ML Model Serving
**What you’re building:** Serve a versioned ML model behind an API.
**Core skills:** FastAPI, model registry, A/B testing, drift alerts.

#### Required Features
- **R1. Model registry & versioning** — **Difficulty 3/5**
  - **Teaches:** Semantic versions; metadata; staging/prod.
  - **Acceptance:** Endpoint loads specific versions; fallback on load failure.
- **R2. Inference API** — **Difficulty 2/5**
  - **Teaches:** Typed request/response; timeouts.
  - **Acceptance:** p95 latency SLO met; errors mapped.
- **R3. A/B/Shadow traffic** — **Difficulty 3/5**
  - **Teaches:** Traffic splits; offline vs online eval.
  - **Acceptance:** Shadow requests don’t affect user; logs compare outputs.
- **R4. Drift detection** — **Difficulty 3/5**
  - **Teaches:** Feature/label drift, alerts.
  - **Acceptance:** Drift beyond threshold triggers alert.

#### Bonus Features
- **B1. Canary deploy + rollback** — **Difficulty 3/5**
  - **Teaches:** Gradual rollout with health metrics.
  - **Acceptance:** Rollback on regression; audit log updated.
- **B2. Batch inference job** — **Difficulty 2/5**
  - **Teaches:** Offline scoring at scale.
  - **Acceptance:** Job writes outputs with version tags.
- **B3. Explainability stub** — **Difficulty 2/5**
  - **Teaches:** Feature attributions (SHAP/LIME basics).
  - **Acceptance:** Endpoint returns simple attribution summary.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 15) Image Processing Pipeline
**What you’re building:** Transform images at throughput with queues and retries.
**Core skills:** Pillow/OpenCV, workers, throughput tuning, metrics.

#### Required Features
- **R1. Worker pool & queue** — **Difficulty 3/5**
  - **Teaches:** Producer/consumer, backpressure, visibility timeouts.
  - **Acceptance:** Throughput charted; no unbounded queue growth.
- **R2. Transform chain** — **Difficulty 2/5**
  - **Teaches:** Resize/filter/OCR steps; idempotence.
  - **Acceptance:** Failed step retried; partial results quarantined.
- **R3. Error handling & retries** — **Difficulty 2/5**
  - **Teaches:** Retry policies; poison queue.
  - **Acceptance:** Persistent failures end up in DLQ with reason.
- **R4. Metrics & dashboards** — **Difficulty 2/5**
  - **Teaches:** Latency histograms; per‑stage rates; alarms.
  - **Acceptance:** Dashboards show bottlenecks; alert on backlog.

#### Bonus Features
- **B1. GPU acceleration (explore)** — **Difficulty 3/5**
  - **Teaches:** OpenCV/CUDA or PyTorch for ops.
  - **Acceptance:** Benchmarks show speedup or documented trade‑offs.
- **B2. Dedup via perceptual hash** — **Difficulty 3/5**
  - **Teaches:** pHash; near‑duplicate detection.
  - **Acceptance:** Duplicates skipped; stats reported.
- **B3. Content moderation stub** — **Difficulty 2/5**
  - **Teaches:** Simple classifiers/heuristics.
  - **Acceptance:** Flagged images routed differently.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 16) Geospatial Routing
**What you’re building:** Shortest routes on a road graph.
**Core skills:** osmnx import, networkx, heuristics (A*), plotting.

#### Required Features
- **R1. Graph build from OSM** — **Difficulty 2/5**
  - **Teaches:** Bounding box import; cleaning; weights (distance/time).
  - **Acceptance:** Graph stats printed; edges weighted.
- **R2. Dijkstra/A*** — **Difficulty 3/5**
  - **Teaches:** Priority queues; heuristics; admissibility.
  - **Acceptance:** A* ≤ Dijkstra expansions; paths valid.
- **R3. Constraints (avoid tolls/elevation)** — **Difficulty 3/5**
  - **Teaches:** Multi‑criteria costs; penalties.
  - **Acceptance:** Options change chosen path; tests verify.
- **R4. Map rendering** — **Difficulty 2/5**
  - **Teaches:** Plot routes; export images/GeoJSON.
  - **Acceptance:** Output renders path clearly with legend.

#### Bonus Features
- **B1. Turn‑by‑turn instructions** — **Difficulty 3/5**
  - **Teaches:** Segment names, bearings, instruction synthesis.
  - **Acceptance:** Human‑readable steps exported.
- **B2. Isochrones** — **Difficulty 3/5**
  - **Teaches:** Reachable area computation by time.
  - **Acceptance:** Polygons generated for N minutes.
- **B3. Traffic simulation (static)** — **Difficulty 3/5**
  - **Teaches:** Time‑dependent weights.
  - **Acceptance:** Scenario report comparing routes.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 17) Message Broker Workers
**What you’re building:** Producer/consumer with RabbitMQ/Redis and DLQs.
**Core skills:** ack/requeue, dead letters, delivery modes, idempotency.

#### Required Features
- **R1. Producer & durable queues** — **Difficulty 2/5**
  - **Teaches:** Durability, confirm selects, publisher confirms.
  - **Acceptance:** Messages persisted; confirms logged.
- **R2. Consumers & acks** — **Difficulty 2/5**
  - **Teaches:** Manual acks; redelivery; prefetch tuning.
  - **Acceptance:** Prefetch improves throughput without starvation.
- **R3. DLQ routing** — **Difficulty 2/5**
  - **Teaches:** Dead lettering on reject/ttl.
  - **Acceptance:** Poison messages route to DLQ with reason tag.
- **R4. Idempotent handlers** — **Difficulty 3/5**
  - **Teaches:** De‑dupe keys; exactly‑once illusions.
  - **Acceptance:** Retries don’t double‑process side effects.

#### Bonus Features
- **B1. Priority & delayed queues** — **Difficulty 3/5**
  - **Teaches:** Per‑message priority; delayed exchange.
  - **Acceptance:** High‑priority items drain first; delays honored.
- **B2. Retry topology** — **Difficulty 2/5**
  - **Teaches:** Retry exchanges with increasing TTLs.
  - **Acceptance:** Backoff via multiple queues works.
- **B3. Monitoring dashboard** — **Difficulty 2/5**
  - **Teaches:** Queue depth and rates.
  - **Acceptance:** Dashboard shows backlog, rates, errors.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 18) Distributed Locks
**What you’re building:** Protect critical sections with Redis locks.
**Core skills:** Redlock patterns, TTLs, fencing tokens, renewal.

#### Required Features
- **R1. Lock acquisition with TTL** — **Difficulty 2/5**
  - **Teaches:** Race conditions; expirations; contention.
  - **Acceptance:** Exclusive access under contention.
- **R2. Renewal/heartbeat** — **Difficulty 3/5**
  - **Teaches:** Extending TTL during long critical sections.
  - **Acceptance:** Long tasks keep lock; missed heartbeats release.
- **R3. Fencing tokens** — **Difficulty 3/5**
  - **Teaches:** Prevent stale owners after expiry.
  - **Acceptance:** Operations with stale token rejected.
- **R4. Lock contention tests** — **Difficulty 2/5**
  - **Teaches:** Load simulation; fairness.
  - **Acceptance:** Measured fairness and failure modes documented.

#### Bonus Features
- **B1. Lease‑based caches** — **Difficulty 3/5**
  - **Teaches:** Prevent dog‑pile stampede.
  - **Acceptance:** Single writer refreshes cache under load.
- **B2. Multi‑node quorum** — **Difficulty 4/5**
  - **Teaches:** Redlock across nodes; trade‑offs.
  - **Acceptance:** Quorum locks resist single‑node failure.
- **B3. Observability hooks** — **Difficulty 2/5**
  - **Teaches:** Expose lock stats.
  - **Acceptance:** Metrics show acquisition rate/failures.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 19) Sharding & Partitioning
**What you’re building:** Distribute data by key across partitions/DBs.
**Core skills:** Hashing, routing, rebalancing, locality vs balance.

#### Required Features
- **R1. Shard function** — **Difficulty 2/5**
  - **Teaches:** Hash mod N; consistent hashing.
  - **Acceptance:** Keys map evenly; collision tests.
- **R2. Router & connection pools** — **Difficulty 3/5**
  - **Teaches:** Routing reads/writes; pool sizing.
  - **Acceptance:** Queries routed to correct shard; failover documented.
- **R3. Rebalancing tool** — **Difficulty 3/5**
  - **Teaches:** Moving ranges/keys online.
  - **Acceptance:** Data moves without downtime in demo.
- **R4. Metrics & hot‑key detection** — **Difficulty 2/5**
  - **Teaches:** Skew detection and mitigation.
  - **Acceptance:** Hot keys identified; mitigation plan applied.

#### Bonus Features
- **B1. Range sharding** — **Difficulty 3/5**
  - **Teaches:** Range splits/merges.
  - **Acceptance:** Split/merge with routing table update.
- **B2. Read replicas** — **Difficulty 2/5**
  - **Teaches:** Replica routing; lag metrics.
  - **Acceptance:** Stale reads flagged; lag alerts.
- **B3. Global secondary index (concept)** — **Difficulty 3/5**
  - **Teaches:** Maintaining cross‑shard indexes.
  - **Acceptance:** Demo with eventual consistency.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 20) Cython Acceleration
**What you’re building:** Speed up a hot loop with a Cython extension.
**Core skills:** Profiling, Cython types, compilation toolchain.

#### Required Features
- **R1. Find hotspots** — **Difficulty 2/5**
  - **Teaches:** cProfile, line_profiler, flamegraphs.
  - **Acceptance:** Baseline timings captured; hotspots identified.
- **R2. Cythonize loop** — **Difficulty 3/5**
  - **Teaches:** `cdef` types, boundscheck/nonecheck controls.
  - **Acceptance:** ≥10x speedup or documented limits.
- **R3. Correctness tests** — **Difficulty 2/5**
  - **Teaches:** Numeric accuracy vs speed.
  - **Acceptance:** Results match Python version across cases.
- **R4. Build & package** — **Difficulty 2/5**
  - **Teaches:** Setup/pyproject config; wheels.
  - **Acceptance:** Wheel builds on CI; import works.

#### Bonus Features
- **B1. Compare PyPy/Numba** — **Difficulty 2/5**
  - **Teaches:** Alternative runtimes/JIT.
  - **Acceptance:** Report with pros/cons and timings.
- **B2. SIMD/vectorization** — **Difficulty 3/5**
  - **Teaches:** `numpy`/C‑level loops.
  - **Acceptance:** Additional speedup demonstrated.
- **B3. Multi‑threading (GIL release)** — **Difficulty 3/5**
  - **Teaches:** `with nogil`; thread pools.
  - **Acceptance:** Scales with cores on CPU‑bound work.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 21) Async DB Layer
**What you’re building:** Async SQLAlchemy/SQLModel with pools and resilience.
**Core skills:** Async engines, transactions, pooling, circuit breakers.

#### Required Features
- **R1. Async engine & sessions** — **Difficulty 2/5**
  - **Teaches:** Connection lifecycles; pool sizing/timeouts.
  - **Acceptance:** Queries run concurrently; pool metrics logged.
- **R2. Transactions** — **Difficulty 2/5**
  - **Teaches:** `async with` patterns; retries on deadlocks.
  - **Acceptance:** Atomicity verified under fault injection.
- **R3. Circuit breaker** — **Difficulty 3/5**
  - **Teaches:** Open/half‑open/closed states; fallback.
  - **Acceptance:** Breaker opens on failures; recovers after cooldown.
- **R4. Read/write split** — **Difficulty 3/5**
  - **Teaches:** Replica routing; consistency semantics.
  - **Acceptance:** Reads hit replicas; writes are consistent; lag monitored.

#### Bonus Features
- **B1. Statement caching** — **Difficulty 2/5**
  - **Teaches:** Prepared statement reuse.
  - **Acceptance:** Reduced latency on repeated queries.
- **B2. Tenant scoping** — **Difficulty 2/5**
  - **Teaches:** Session context for tenant IDs.
  - **Acceptance:** Queries auto‑filter by tenant context.
- **B3. Observability** — **Difficulty 2/5**
  - **Teaches:** Query traces; slow query logging.
  - **Acceptance:** p95/p99 query times charted.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 22) Security Hardening
**What you’re building:** Secure defaults across services and code.
**Core skills:** Bandit, pip‑audit, input validation, headers, cookies.

#### Required Features
- **R1. Dependency scanning** — **Difficulty 1/5**
  - **Teaches:** `pip‑audit`/`pip‑tools`, CVE handling.
  - **Acceptance:** No high‑severity vulns; remediations tracked.
- **R2. Static analysis** — **Difficulty 2/5**
  - **Teaches:** Bandit rules; custom plugins for org standards.
  - **Acceptance:** Violations triaged or fixed.
- **R3. Web security headers** — **Difficulty 2/5**
  - **Teaches:** CSP, HSTS, XFO, XSS‑Protection.
  - **Acceptance:** Headers present; CSP reports configured.
- **R4. Input validation** — **Difficulty 2/5**
  - **Teaches:** Pydantic validators; deny lists; canonicalization.
  - **Acceptance:** Fuzz tests for critical endpoints pass.

#### Bonus Features
- **B1. Signed service requests** — **Difficulty 3/5**
  - **Teaches:** HMAC signatures; replay prevention.
  - **Acceptance:** Signature verified; skew handled.
- **B2. Secrets rotation** — **Difficulty 2/5**
  - **Teaches:** Rotating keys with zero downtime.
  - **Acceptance:** Plan/runbook; rotation test completes.
- **B3. Threat modeling doc** — **Difficulty 2/5**
  - **Teaches:** STRIDE/LINDDUN basics.
  - **Acceptance:** Document with mitigations and owners.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 23) Caching Strategies
**What you’re building:** Local+Redis caches with robust invalidation.
**Core skills:** TTL, LRU, stampede prevention, metrics.

#### Required Features
- **R1. Local (in‑proc) cache** — **Difficulty 2/5**
  - **Teaches:** LRU/TTL; thread safety.
  - **Acceptance:** Cache hit/miss metrics; eviction works.
- **R2. Redis cache** — **Difficulty 2/5**
  - **Teaches:** Serialization formats; memory sizing.
  - **Acceptance:** Keys expire; memory use monitored.
- **R3. Invalidation policies** — **Difficulty 3/5**
  - **Teaches:** Write‑through/back; explicit/implicit busting.
  - **Acceptance:** Cache coherence demonstrated under updates.
- **R4. Stampede prevention** — **Difficulty 3/5**
  - **Teaches:** Single‑flight; soft TTL; jitter.
  - **Acceptance:** Under load, single refresh per key.

#### Bonus Features
- **B1. Hierarchical L1/L2** — **Difficulty 3/5**
  - **Teaches:** Local vs remote trade‑offs.
  - **Acceptance:** Lower latency without stale spikes.
- **B2. Near‑cache for clients** — **Difficulty 2/5**
  - **Teaches:** Client caching with invalidation channel.
  - **Acceptance:** Invalidation messages clear near caches.
- **B3. Metrics & dashboards** — **Difficulty 2/5**
  - **Teaches:** Cache hit rate, age, memory.
  - **Acceptance:** Dashboard shows improvement over baseline.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 24) Blue/Green Deploy (Compose)
**What you’re building:** Switch traffic between two app versions safely.
**Core skills:** Nginx routing, healthchecks, rollback, smoke tests.

#### Required Features
- **R1. Two versions running** — **Difficulty 2/5**
  - **Teaches:** Compose overrides; side‑by‑side deployments.
  - **Acceptance:** Both `blue` and `green` are reachable; status endpoint OK.
- **R2. Router config** — **Difficulty 2/5**
  - **Teaches:** Nginx upstreams; health checks; stickiness.
  - **Acceptance:** Switch controlled by one flag/env; logs confirm.
- **R3. Smoke & health checks** — **Difficulty 2/5**
  - **Teaches:** Health endpoints; automated smoke tests.
  - **Acceptance:** Bad `green` blocks cutover; logs show failure.
- **R4. Drain connections & rollback** — **Difficulty 2/5**
  - **Teaches:** Graceful shutdown; quick rollback.
  - **Acceptance:** Cutover has no dropped requests; rollback succeeds.

#### Bonus Features
- **B1. Canary percent rollout** — **Difficulty 3/5**
  - **Teaches:** Weighted routing.
  - **Acceptance:** 5%→100% rollout with metrics gating.
- **B2. Database migration toggle** — **Difficulty 3/5**
  - **Teaches:** Expand/contract migrations.
  - **Acceptance:** Double‑write period documented; no data loss.
- **B3. Release notes automation** — **Difficulty 1/5**
  - **Teaches:** CI step to compile changes.
  - **Acceptance:** Artifact attached to deploy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 25) Data Lake to Parquet + DuckDB
**What you’re building:** Ingest CSV→Parquet and query with DuckDB.
**Core skills:** Pandas, PyArrow, partitioning, SQL queries, manifests.

#### Required Features
- **R1. CSV→Parquet batch** — **Difficulty 2/5**
  - **Teaches:** Schema inference; column types; compression.
  - **Acceptance:** Parquet files written with correct dtypes and compression.
- **R2. Partitioning by date** — **Difficulty 2/5**
  - **Teaches:** Directory layout; prune with predicates.
  - **Acceptance:** Queries only scan needed partitions (observed via EXPLAIN).
- **R3. Statistics & manifest** — **Difficulty 2/5**
  - **Teaches:** Min/max stats; manifest for discovery.
  - **Acceptance:** Manifest lists files; EXPLAIN shows stats usage.
- **R4. DuckDB queries** — **Difficulty 2/5**
  - **Teaches:** External table reads; performance.
  - **Acceptance:** Queries meet latency targets on sample sizes.

#### Bonus Features
- **B1. Delta/Iceberg concepts** — **Difficulty 2/5** *(concept demo)*
  - **Teaches:** ACID tables; metadata layers.
  - **Acceptance:** Document pros/cons; simple append demo.
- **B2. Z‑order/clustered writes** — **Difficulty 3/5**
  - **Teaches:** Data layout impacts on queries.
  - **Acceptance:** Benchmarks show improved locality.
- **B3. Compression tuning** — **Difficulty 2/5**
  - **Teaches:** ZSTD/Snappy trade‑offs.
  - **Acceptance:** Size vs speed comparison documented.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
