### 10) Word‑Frequency Analyzer
**What you’re building:** Compute TF and TF‑IDF across a corpus.
**Core skills:** Tokenization, stopwords, math/logs, report generation.

#### Required Features
- **R1. Normalization pipeline** — **Difficulty 2/5**
  - **What it teaches:** Case folding; punctuation removal; Unicode handling.
  - **Acceptance criteria:** Repeatable tokens on repeated runs.

- **R2. Term frequencies (per doc & global)** — **Difficulty 2/5**
  - **What it teaches:** Counting efficiently; handling very large docs.
  - **Acceptance criteria:** Counts match small hand‑computed examples.

- **R3. TF‑IDF scoring** — **Difficulty 2/5**
  - **What it teaches:** Log weighting; smoothing; sparse representations.
  - **Acceptance criteria:** Top terms per doc exported with scores.

- **R4. Reports (CSV/Markdown)** — **Difficulty 1/5**
  - **What it teaches:** Generating human‑readable summaries.
  - **Acceptance criteria:** Per‑doc and global reports saved.

#### Bonus Features
- **B1. Stemming/Lemmatization** — **Difficulty 2/5**
  - **Teaches:** NLTK/spaCy pipelines; recall vs precision trade‑offs.
  - **Acceptance:** Provide before/after examples; configurable.

- **B2. Interactive search** — **Difficulty 2/5**
  - **Teaches:** Query over index; ranked results.
  - **Acceptance:** Query returns ranked docs; snippets included.

- **B3. Memory optimization** — **Difficulty 3/5**
  - **Teaches:** On‑disk sparse matrices; chunked processing.
  - **Acceptance:** Handles corpora larger than RAM (document limits/throughput).

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
