### 25) CLI Address Autocomplete
**What you’re building:** Local fuzzy search over addresses using a trigram index.
**Core skills:** text normalization, sets, lightweight indexing.

#### Required Features
- **R1. Normalization** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, stripping punctuation, diacritics removal.
  - **Acceptance criteria:** "São Paulo" and "Sao Paulo" normalize identically.

- **R2. Trigram index build** — **Difficulty 3/5**
  - **What it teaches:** N‑gram tokenization; posting lists; memory trade‑offs.
  - **Acceptance criteria:** Index built once; persistent on disk (compact format).

- **R3. Ranking & pagination** — **Difficulty 2/5**
  - **What it teaches:** Scoring by trigram overlap; tie‑breakers; paging.
  - **Acceptance criteria:** Top‑k results stable; `--page` and `--limit` work.

- **R4. CLI query path** — **Difficulty 1/5**
  - **What it teaches:** `argparse` UX; quoting; fast path for exact matches.
  - **Acceptance criteria:** Exact match returns position 1; invalid queries explained.

#### Bonus Features
- **B1. Incremental indexing** — **Difficulty 3/5**
  - **What it teaches:** Append‑only segments and merges.
  - **Acceptance criteria:** New addresses added without full rebuild.

- **B2. Memory‑mapped index** — **Difficulty 3/5**
  - **What it teaches:** `mmap` for fast reads; zero‑copy slices.
  - **Acceptance criteria:** Start‑up time reduced vs in‑RAM index.

- **B3. Interactive TUI** — **Difficulty 2/5**
  - **What it teaches:** Type‑ahead with `prompt_toolkit`/`textual`.
  - **Acceptance criteria:** Live filtering as you type.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

```
