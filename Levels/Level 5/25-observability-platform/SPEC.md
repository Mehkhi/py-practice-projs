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
