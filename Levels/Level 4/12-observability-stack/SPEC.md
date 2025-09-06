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
