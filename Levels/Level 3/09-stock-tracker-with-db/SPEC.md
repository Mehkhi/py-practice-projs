### 9) Stock Tracker with DB
**What you’re building:** Daily price ingester with analysis and charting.
**Core skills:** Scheduling, HTTP APIs, pandas, matplotlib, Dockerization.

#### Required Features
- **R1. Daily fetch & store** — **Difficulty 2/5**
  - **What it teaches:** Cron/`schedule` lib, idempotent inserts, API hygiene.
  - **Acceptance criteria:** Duplicate days do not create duplicate rows.

- **R2. Technical indicators** — **Difficulty 2/5**
  - **What it teaches:** Moving averages, RSI basics, rolling windows.
  - **Acceptance criteria:** Indicator columns correct for sample data.

- **R3. Alerts** — **Difficulty 2/5**
  - **What it teaches:** Threshold rules; notification channels.
  - **Acceptance criteria:** Alerts fire once per crossing; deduped.

- **R4. Charts & export** — **Difficulty 2/5**
  - **What it teaches:** Plotting with date axes; PNG/CSV outputs.
  - **Acceptance criteria:** Chart saved with legend; data export consistent.

#### Bonus Features
- **B1. Dockerized service** — **Difficulty 2/5**
  - **Teaches:** Container healthcheck; env configs.
  - **Acceptance:** `docker compose up` runs end‑to‑end.

- **B2. Backtesting (simple)** — **Difficulty 3/5**
  - **Teaches:** Strategy loops; performance metrics.
  - **Acceptance:** Equity curve and stats (CAGR, max drawdown) produced.

- **B3. Caching & rate‑limit handling** — **Difficulty 2/5**
  - **Teaches:** ETags/If‑Modified‑Since; backoff on 429.
  - **Acceptance:** Reduces API calls; compliant with provider rules.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
