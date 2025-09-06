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
