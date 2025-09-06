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
