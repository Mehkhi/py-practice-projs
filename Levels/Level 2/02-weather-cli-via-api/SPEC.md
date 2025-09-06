### 2) Weather CLI via API
**What you’re building:** Query a public weather API for current conditions.
**Core skills:** `requests`, environment variables, HTTP error handling.

#### Required Features
- **R1. API client with env‑based API key** — **Difficulty 2/5**
  - **What it teaches:** Using `os.environ`, 401/403 handling, defensive retries on 5xx.
  - **Acceptance criteria:** Missing/invalid key yields clear error; happy path prints weather.

- **R2. Units switch (metric/imperial)** — **Difficulty 1/5**
  - **What it teaches:** Parameterizing requests and formatting output consistently.
  - **Acceptance criteria:** `--units metric|imperial` alters both request params and display.

- **R3. City lookup and validation** — **Difficulty 2/5**
  - **What it teaches:** Normalizing city input, handling ambiguous cities (name + country code), and graceful "not found" paths.
  - **Acceptance criteria:** Ambiguous or invalid cities yield friendly guidance.

- **R4. 5‑day forecast (basic)** — **Difficulty 2/5**
  - **What it teaches:** Iterating API pages or list objects; summarizing min/max/avg per day.
  - **Acceptance criteria:** Prints a table of daily highs/lows with dates.

#### Bonus Features
- **B1. On‑disk response cache** — **Difficulty 2/5**
  - **What it teaches:** Cache keys, TTL control, invalidation strategy.
  - **Acceptance criteria:** Repeated calls hit cache; `--no-cache` bypass supported.

- **B2. Retry with exponential backoff** — **Difficulty 2/5**
  - **What it teaches:** Transient error handling patterns; jitter.
  - **Acceptance criteria:** 5xx/timeout retries logged; eventual failure explained.

- **B3. Geo‑coordinates support** — **Difficulty 2/5**
  - **What it teaches:** Accepting latitude/longitude inputs; validation.
  - **Acceptance criteria:** `--lat --lon` path returns same data as by city.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
