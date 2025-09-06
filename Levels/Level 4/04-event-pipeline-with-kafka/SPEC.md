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
