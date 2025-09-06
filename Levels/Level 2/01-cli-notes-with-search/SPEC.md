### 1) CLI Notes with Search
**What you’re building:** A notes CLI that stores JSON notes with tags and simple search.
**Core skills:** `argparse`, JSON I/O, indexing, timestamps, logging.

#### Required Features
- **R1. Create/List/View/Delete notes (JSON store)** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON schema design and forward‑compatible fields (e.g., `id`, `title`, `body`, `tags`, `created_at`, `updated_at`, `archived`).
    - Atomic writes (write temp file then rename) to avoid corruption.
    - Separation of concerns: storage layer vs CLI layer.
  - **Acceptance criteria:**
    - CRUD works with unique IDs; file remains valid JSON after interruptions.
    - `list` shows title + created time; `view` shows full note.

- **R2. Tagging and tag filters** — **Difficulty 2/5**
  - **What it teaches:**
    - Normalizing input (lowercasing tags, trimming whitespace).
    - Indexing by tags for O(1) lookups (build at load time).
    - Designing queries (AND vs OR semantics for multiple tags).
  - **Acceptance criteria:**
    - `--tag` filters include correct notes; multiple tags behave as documented.

- **R3. Full‑text search (contains match)** — **Difficulty 2/5**
  - **What it teaches:**
    - Tokenization basics and stopwords trade‑offs.
    - Precomputing a simple inverted index for titles/bodies.
    - UX: show snippets with highlighted terms.
  - **Acceptance criteria:**
    - `search "term"` returns ranked results; empty search is rejected.

- **R4. Timestamps + logging** — **Difficulty 1/5**
  - **What it teaches:**
    - `datetime.now().isoformat()` usage and consistency.
    - `logging` configuration (levels, handlers, log format).
  - **Acceptance criteria:**
    - Create/update times populate; basic INFO/ERROR logs written to file.

#### Bonus Features
- **B1. Fuzzy search (trigram / `difflib`)** — **Difficulty 3/5**
  - **What it teaches:** Similarity metrics, thresholds, and ranking UX.
  - **Acceptance criteria:** Misspellings still find likely notes with scores.

- **B2. Encryption at rest (Fernet)** — **Difficulty 3/5**
  - **What it teaches:** Key management, encrypt/decrypt boundaries, risks of losing keys.
  - **Acceptance criteria:** Encrypted file unreadable without key; CLI can decrypt transparently for the user.

- **B3. Colored output** — **Difficulty 1/5**
  - **What it teaches:** Terminal UX using `rich`/`colorama`.
  - **Acceptance criteria:** List/search/view commands render consistently with color.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
