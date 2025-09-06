### 5) Web Log Analyzer
**What you’re building:** Parse and summarize Apache/Nginx logs.
**Core skills:** regex parsing, datetime, aggregation, CSV export.

#### Required Features
- **R1. Parser for Common/Combined Log Format** — **Difficulty 2/5**
  - **What it teaches:** Robust regex; handling malformed lines.
  - **Acceptance criteria:** ≥99% lines parsed on sample logs; bad lines counted.

- **R2. Status and endpoint summaries** — **Difficulty 2/5**
  - **What it teaches:** Group‑by aggregations; top‑N queries.
  - **Acceptance criteria:** Tables for status code distribution and top endpoints.

- **R3. Hourly traffic chart** — **Difficulty 2/5**
  - **What it teaches:** Time bucketing; time‑zone normalization.
  - **Acceptance criteria:** CSV and ASCII chart rendered for requests/hour.

- **R4. Export report** — **Difficulty 1/5**
  - **What it teaches:** Writing CSV/JSON summaries.
  - **Acceptance criteria:** Files created; consistent schema.

#### Bonus Features
- **B1. Bot/user‑agent filters** — **Difficulty 2/5**
  - **What it teaches:** UA heuristics; whitelist/blacklist configs.
  - **Acceptance criteria:** Filtered views exclude known bots.

- **B2. Spike/anomaly detection** — **Difficulty 3/5**
  - **What it teaches:** Rolling averages and z‑score alerts.
  - **Acceptance criteria:** Spikes flagged with threshold and timestamp.

- **B3. GeoIP breakdown (if DB available)** — **Difficulty 3/5**
  - **What it teaches:** IP→country lookup and grouping.
  - **Acceptance criteria:** Country histogram produced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
