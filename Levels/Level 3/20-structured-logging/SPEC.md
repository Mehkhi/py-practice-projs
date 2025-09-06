### 20) Structured Logging
**What you’re building:** JSON logs with correlation IDs and rotation.
**Core skills:** logging config, filters, RotatingFileHandler, log sampling.

#### Required Features
- **R1. JSON log format** — **Difficulty 2/5**
  - **What it teaches:** Custom `Formatter` or libs; field design.
  - **Acceptance criteria:** Logs are valid JSON with timestamp, level, msg, context.

- **R2. Correlation/trace IDs** — **Difficulty 2/5**
  - **What it teaches:** Context vars; middleware to inject IDs.
  - **Acceptance criteria:** ID persists across request lifecycle.

- **R3. Rotation & retention** — **Difficulty 2/5**
  - **What it teaches:** File size/time rotation; retention policy.
  - **Acceptance criteria:** Old logs archived and pruned as configured.

- **R4. Log levels & sampling** — **Difficulty 2/5**
  - **What it teaches:** Verbosity control; sample noisy events.
  - **Acceptance criteria:** Level filtering works; sampling reduces volume.

#### Bonus Features
- **B1. Ship to Elasticsearch (local)** — **Difficulty 3/5**
  - **Teaches:** Log shipping, index templates, Kibana dashboards.
  - **Acceptance:** Logs visible in Kibana; fields indexed.

- **B2. OpenTelemetry attributes** — **Difficulty 2/5**
  - **Teaches:** Trace context in logs.
  - **Acceptance:** Span IDs appear; cross‑links enabled.

- **B3. PII redaction** — **Difficulty 2/5**
  - **Teaches:** Filters to mask sensitive data.
  - **Acceptance:** Emails/SSNs redacted per policy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
