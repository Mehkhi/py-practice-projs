### 4) Async Web Scraper
**What you’re building:** High‑throughput crawler that stores extracted data.
**Core skills:** `asyncio`, `aiohttp`, backoff, caching, respectful crawling.

#### Required Features
- **R1. Concurrent fetching with semaphore** — **Difficulty 3/5**
  - **What it teaches:** Async session reuse, bounded concurrency, cancellation.
  - **Acceptance criteria:** Concurrency limited; graceful shutdown on Ctrl‑C.

- **R2. Politeness: robots.txt & delays** — **Difficulty 2/5**
  - **What it teaches:** Robots parsing, per‑host delays, user‑agent etiquette.
  - **Acceptance criteria:** Disallowed paths skipped; logs show delay policy.

- **R3. Retry with exponential backoff** — **Difficulty 2/5**
  - **What it teaches:** Transient failure handling; jitter to avoid sync storms.
  - **Acceptance criteria:** 429/5xx retries; final failure recorded with reason.

- **R4. Extract & persist data** — **Difficulty 2/5**
  - **What it teaches:** CSS selectors/XPath, normalization, SQLite/CSV sinks.
  - **Acceptance criteria:** Schema documented; duplicate suppression implemented.

#### Bonus Features
- **B1. On‑disk HTML cache** — **Difficulty 2/5**
  - **Teaches:** URL→filename hashing, TTL, offline replays.
  - **Acceptance:** Cached pages reused; `--no-cache` bypass works.

- **B2. Pluggable pipelines** — **Difficulty 3/5**
  - **Teaches:** Hook system for transforms (e.g., clean→validate→store).
  - **Acceptance:** Adding a new pipeline stage requires no core changes.

- **B3. Sitemap discovery** — **Difficulty 2/5**
  - **Teaches:** Using sitemaps to seed URLs; deduping.
  - **Acceptance:** If sitemap exists, it’s crawled before fallback discovery.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
