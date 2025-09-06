### 7) PDF Search (Mini Index)
**What you’re building:** Extract text and search PDFs with an inverted index.
**Core skills:** PDF text extraction, tokenization, indexing, ranking, snippets.

#### Required Features
- **R1. Text extraction** — **Difficulty 2/5**
  - **What it teaches:** `pdfminer`/`pypdf` trade‑offs; handling OCR‑less PDFs.
  - **Acceptance criteria:** Extracted text saved; pages tracked.

- **R2. Tokenization & normalization** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, stopword removal, optional stemming.
  - **Acceptance criteria:** Reproducible tokens for same input.

- **R3. Inverted index & phrase queries** — **Difficulty 3/5**
  - **What it teaches:** Posting lists, positions for phrase matching.
  - **Acceptance criteria:** `"machine learning"` phrase finds exact sequences.

- **R4. Ranking & snippets** — **Difficulty 3/5**
  - **What it teaches:** TF‑IDF/BM25 basics, windowed snippet generation.
  - **Acceptance criteria:** Results ranked deterministically; terms highlighted in snippets.

#### Bonus Features
- **B1. Boolean operators** — **Difficulty 3/5**
  - **Teaches:** AND/OR/NOT parsing and execution.
  - **Acceptance:** Complex queries return correct doc sets.

- **B2. Field weights** — **Difficulty 2/5**
  - **Teaches:** Title/heading boosts; scoring composition.
  - **Acceptance:** Title matches rank above body‑only matches.

- **B3. Persistent/compact index** — **Difficulty 3/5**
  - **Teaches:** On‑disk structures; compression; memory maps.
  - **Acceptance:** Index reloads fast; RAM usage documented.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
