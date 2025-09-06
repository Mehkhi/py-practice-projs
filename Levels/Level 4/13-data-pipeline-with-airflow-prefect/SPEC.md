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
