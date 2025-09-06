### 15) Requests Caching Layer
**What you’re building:** Transparent caching for HTTP requests.
**Core skills:** requests‑cache, cache keys, TTL, invalidation, metrics.

#### Required Features
- **R1. Cache key strategy** — **Difficulty 2/5**
  - **What it teaches:** Keys from method+URL+params+headers; Vary support.
  - **Acceptance criteria:** Distinct keys for differing query/headers.

- **R2. TTL & invalidation** — **Difficulty 2/5**
  - **What it teaches:** Expiry, manual purge, cache busting.
  - **Acceptance criteria:** Expired entries refreshed; manual invalidation works.

- **R3. Stale‑while‑revalidate** — **Difficulty 3/5**
  - **What it teaches:** Serving stale content while async refresh occurs.
  - **Acceptance criteria:** Second request serves fresh result post‑refresh.

- **R4. Metrics & logging** — **Difficulty 2/5**
  - **What it teaches:** Hit/miss rate, latency improvements.
  - **Acceptance criteria:** Metrics exported and chartable.

#### Bonus Features
- **B1. Pluggable backends (disk/Redis)** — **Difficulty 2/5**
  - **Teaches:** Backend abstractions; connection options.
  - **Acceptance:** Swapping backend requires only config change.

- **B2. Conditional requests** — **Difficulty 2/5**
  - **Teaches:** ETag/Last‑Modified; `If-None-Match`.
  - **Acceptance:** 304 responses handled; cache updated accordingly.

- **B3. Cache stampede protection** — **Difficulty 3/5**
  - **Teaches:** Single‑flight/locking around misses.
  - **Acceptance:** Under load, only one refresh occurs per key.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
