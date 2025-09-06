### 4) SQLite Contact Manager
**What you’re building:** Manage contacts with SQLite via SQL queries.
**Core skills:** `sqlite3`, schema design, parameterized queries.

#### Required Features
- **R1. Schema and migrations** — **Difficulty 2/5**
  - **What it teaches:** Designing tables (`contacts`, `emails`, `phones`), indexes, and evolving schemas.
  - **Acceptance criteria:** Migration script upgrades DB without data loss.

- **R2. CRUD with parameterized SQL** — **Difficulty 2/5**
  - **What it teaches:** Preventing SQL injection; returning rows as dicts.
  - **Acceptance criteria:** Insert/update/delete and list/search work reliably.

- **R3. Unique constraints & de‑dup** — **Difficulty 2/5**
  - **What it teaches:** `UNIQUE` on email; conflict handling (`INSERT OR IGNORE`).
  - **Acceptance criteria:** Duplicate emails rejected gracefully.

- **R4. Pagination & sorting** — **Difficulty 1/5**
  - **What it teaches:** LIMIT/OFFSET and ORDER BY.
  - **Acceptance criteria:** Large lists page correctly; sort by name or created.

#### Bonus Features
- **B1. Phonetic search (soundex/metaphone)** — **Difficulty 3/5**
  - **What it teaches:** Fuzzy name matching; custom SQL functions.
  - **Acceptance criteria:** "Jon" finds "John"; ranked by closeness.

- **B2. Import/export CSV** — **Difficulty 2/5**
  - **What it teaches:** ETL patterns and schema validation.
  - **Acceptance criteria:** Round‑trips maintain data fidelity.

- **B3. Groups/labels** — **Difficulty 2/5**
  - **What it teaches:** Many‑to‑many relations.
  - **Acceptance criteria:** List contacts by group; add/remove groups.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
