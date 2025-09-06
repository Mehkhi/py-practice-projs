### 8) Basic Web Scraper
**What you’re building:** Fetch a page and extract items (titles, links).
**Core skills:** `requests`, BeautifulSoup, CSS selectors.

#### Required Features
- **R1. Fetch and parse** — **Difficulty 1/5**
  - **What it teaches:** GET requests; HTML parsing; error handling.
  - **Acceptance criteria:** Non‑200s don’t crash; content parsed.

- **R2. Item extraction** — **Difficulty 2/5**
  - **What it teaches:** CSS selectors; normalization; deduping.
  - **Acceptance criteria:** Items listed with title + URL.

- **R3. Pagination follow** — **Difficulty 2/5**
  - **What it teaches:** Next‑page discovery; stopping criteria.
  - **Acceptance criteria:** Traverses until no next page or max limit.

- **R4. robots.txt & politeness** — **Difficulty 2/5**
  - **What it teaches:** Respectful scraping; delays; user agent setting.
  - **Acceptance criteria:** Respects disallow rules; throttle respected.

#### Bonus Features
- **B1. SQLite export** — **Difficulty 2/5**
  - **What it teaches:** Persisting items for later querying.
  - **Acceptance criteria:** Table created; duplicates avoided.

- **B2. Cache pages on disk** — **Difficulty 2/5**
  - **What it teaches:** Hashing URLs to filenames; TTL control.
  - **Acceptance criteria:** Re‑runs hit cache when fresh.

- **B3. Backoff & retry** — **Difficulty 2/5**
  - **What it teaches:** Retry policies with jitter.
  - **Acceptance criteria:** Transient failures don’t abort the crawl.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
