### 10) CSV Cleaner
**What you’re building:** Load a CSV, clean it, and write a standardized output.
**Core skills:** pandas basics, dtype handling, CSV writing.

#### Required Features
- **R1. Column normalization** — **Difficulty 2/5**
  - **What it teaches:** Renaming, trimming, and consistent casing.
  - **Acceptance criteria:** Mapping config applied; unknown columns logged.

- **R2. Missing values strategy** — **Difficulty 2/5**
  - **What it teaches:** Imputation rules (mean/median/const); per‑column policy.
  - **Acceptance criteria:** Null counts before/after reported.

- **R3. Dtype coercion** — **Difficulty 2/5**
  - **What it teaches:** `astype` conversions; error handling.
  - **Acceptance criteria:** Invalid rows reported; schema documented.

- **R4. Summary report** — **Difficulty 1/5**
  - **What it teaches:** Descriptives (min/max/mean); outlier flags.
  - **Acceptance criteria:** Writes a human‑readable summary file.

#### Bonus Features
- **B1. YAML data quality rules** — **Difficulty 3/5**
  - **What it teaches:** Declarative validation; schema checks.
  - **Acceptance criteria:** Violations listed per rule with counts.

- **B2. Outlier detection** — **Difficulty 2/5**
  - **What it teaches:** Z‑score/IQR basics.
  - **Acceptance criteria:** Rows flagged with reasons.

- **B3. Row‑level error CSV** — **Difficulty 2/5**
  - **What it teaches:** Issue tracking per row.
  - **Acceptance criteria:** Separate CSV of rejected rows produced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
