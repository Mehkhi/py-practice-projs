### 3) Currency Converter (API)
**What you’re building:** Convert currencies using live rates.
**Core skills:** `requests`, JSON parsing, `Decimal` for money.

#### Required Features
- **R1. Live rates fetch + `Decimal` math** — **Difficulty 2/5**
  - **What it teaches:** Avoiding float rounding errors; validating currency codes.
  - **Acceptance criteria:** Known rate pairs compute accurately within tolerance.

- **R2. Historical rates** — **Difficulty 2/5**
  - **What it teaches:** Date parameters, time‑series handling, and formatting.
  - **Acceptance criteria:** `--date YYYY-MM-DD` uses that day’s rates.

- **R3. Offline fallback** — **Difficulty 2/5**
  - **What it teaches:** Caching last good snapshot; stale data warnings.
  - **Acceptance criteria:** No network still converts using last snapshot with banner.

- **R4. Validation & UX** — **Difficulty 1/5**
  - **What it teaches:** ISO codes, helpful errors, and examples in `--help`.
  - **Acceptance criteria:** Invalid codes rejected with suggestions.

#### Bonus Features
- **B1. Plot conversion history** — **Difficulty 2/5**
  - **What it teaches:** `matplotlib` line chart, date ticks, moving averages.
  - **Acceptance criteria:** Saves PNG with legend and units.

- **B2. Multi‑currency table** — **Difficulty 2/5**
  - **What it teaches:** Batch queries and table formatting.
  - **Acceptance criteria:** Base → many quote currencies table exported to CSV.

- **B3. Alerts on threshold** — **Difficulty 2/5**
  - **What it teaches:** Simple rules engine; notifications.
  - **Acceptance criteria:** Prints/plays alert when crossing a configured rate.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
