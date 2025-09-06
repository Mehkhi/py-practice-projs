### 19) Folder Watch ETL
**What you’re building:** Watch a folder and transform new files.
**Core skills:** watchdog, pipelines, error handling, retries, metrics.

#### Required Features
- **R1. Watcher & debounce** — **Difficulty 2/5**
  - **What it teaches:** File system events; debouncing partial writes.
  - **Acceptance criteria:** Only stable files processed; duplicates avoided.

- **R2. ETL pipeline** — **Difficulty 2/5**
  - **What it teaches:** Extract→Transform→Load stages; pluggability.
  - **Acceptance criteria:** New transforms can be added without core changes.

- **R3. Error handling & quarantine** — **Difficulty 2/5**
  - **What it teaches:** Moving bad files to quarantine with reason.
  - **Acceptance criteria:** Failures logged; quarantine directory structured.

- **R4. Metrics** — **Difficulty 2/5**
  - **What it teaches:** Throughput, latency, failure counts.
  - **Acceptance criteria:** Metrics printed/exported periodically.

#### Bonus Features
- **B1. Parallel processing** — **Difficulty 3/5**
  - **Teaches:** Thread/Process pools; concurrency bugs.
  - **Acceptance:** Throughput improves without data races.

- **B2. Config file** — **Difficulty 2/5**
  - **Teaches:** YAML for pipelines; validation.
  - **Acceptance:** Changing config alters behavior at next run.

- **B3. CDC (change data capture)** — **Difficulty 3/5**
  - **Teaches:** Capturing updates instead of only new files.
  - **Acceptance:** Modified files reprocessed per policy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
