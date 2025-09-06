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
