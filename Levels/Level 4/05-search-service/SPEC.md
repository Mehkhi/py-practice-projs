### 5) Search Service
**What you’re building:** Index documents and serve ranked results.
**Core skills:** Elasticsearch/OpenSearch, analyzers, queries, ranking.

#### Required Features
- **R1. Index design & analyzers** — **Difficulty 3/5**
  - **Teaches:** Tokenizers, filters, language analyzers, mappings.
  - **Acceptance:** Index created with appropriate mappings; reindex script exists.
- **R2. Ingest pipeline** — **Difficulty 2/5**
  - **Teaches:** Normalization, stemming, enrichment.
  - **Acceptance:** Docs ingested with IDs; updates merge correctly.
- **R3. Query DSL & pagination** — **Difficulty 3/5**
  - **Teaches:** bool queries, filters vs queries, highlights.
  - **Acceptance:** Queries return highlights; consistent sort; pages stable.
- **R4. Relevance evaluation** — **Difficulty 3/5**
  - **Teaches:** Judgments, offline metrics, A/B hooks.
  - **Acceptance:** Report with NDCG/MRR for a labeled set.

#### Bonus Features
- **B1. Synonyms & spell correction** — **Difficulty 3/5**
  - **Teaches:** Synonym filters; fuzzy matching.
  - **Acceptance:** Misspellings still retrieve relevant docs.
- **B2. Field boosts** — **Difficulty 2/5**
  - **Teaches:** Title boosts; recency boosting.
  - **Acceptance:** Boosts measurably improve quality on eval set.
- **B3. Index lifecycle mgmt** — **Difficulty 3/5**
  - **Teaches:** Hot/warm/cold tiers; rollover.
  - **Acceptance:** Index rollover and retention policy tested.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
