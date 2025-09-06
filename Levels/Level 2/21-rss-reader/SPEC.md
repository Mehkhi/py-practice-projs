### 21) RSS Reader (CLI)
**What you’re building:** Fetch feeds, display new items, mark as read.
**Core skills:** `feedparser`, persistence, humanized times.

#### Required Features
- **R1. Subscribe/unsubscribe** — **Difficulty 2/5**
  - **What it teaches:** Managing a feed list and validating URLs.
  - **Acceptance criteria:** Subscriptions persist; invalid feeds rejected.

- **R2. Fetch & store entries** — **Difficulty 2/5**
  - **What it teaches:** Deduplication by GUID/URL; per‑feed state.
  - **Acceptance criteria:** New vs read items tracked correctly.

- **R3. Filters and search** — **Difficulty 2/5**
  - **What it teaches:** Tag/keyword filters; date filters.
  - **Acceptance criteria:** Commands show subsets as requested.

- **R4. Notifications on new** — **Difficulty 1/5**
  - **What it teaches:** Simple polling and notifying.
  - **Acceptance criteria:** New arrivals trigger a desktop/console alert.

#### Bonus Features
- **B1. HTML digest export** — **Difficulty 2/5**
  - **What it teaches:** Templating an offline digest page.
  - **Acceptance criteria:** A dated HTML report with links rendered.

- **B2. OPML import/export** — **Difficulty 2/5**
  - **What it teaches:** Interoperability with other readers.
  - **Acceptance criteria:** Round‑trip keeps titles and URLs.

- **B3. Offline mode** — **Difficulty 2/5**
  - **What it teaches:** Caching content; read later.
  - **Acceptance criteria:** Cached items viewable without network.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
