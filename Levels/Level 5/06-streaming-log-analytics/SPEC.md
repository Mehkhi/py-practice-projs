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
