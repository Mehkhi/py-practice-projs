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
