### 15) Password Strength Checker
**What you’re building:** Score passwords by entropy and rules.
**Core skills:** regex, `math.log2`, common password lists.

#### Required Features
- **R1. Entropy estimation** — **Difficulty 2/5**
  - **What it teaches:** Character set sizes; length impact; bits of entropy.
  - **Acceptance criteria:** Entropy printed with rationale.

- **R2. Rule checks** — **Difficulty 2/5**
  - **What it teaches:** Minimum length, classes, repeated sequences.
  - **Acceptance criteria:** Violations listed with suggestions.

- **R3. Common password detection** — **Difficulty 2/5**
  - **What it teaches:** Large list lookup; memory considerations.
  - **Acceptance criteria:** Known bad passwords flagged instantly.

- **R4. Feedback summary** — **Difficulty 1/5**
  - **What it teaches:** Clear UX messaging; prioritizing recommendations.
  - **Acceptance criteria:** Ranked suggestions output.

#### Bonus Features
- **B1. Leetspeak variants** — **Difficulty 2/5**
  - **What it teaches:** Transformations; expanding match space.
  - **Acceptance criteria:** `p@ssw0rd` detected as weak.

- **B2. Offline Bloom filter** — **Difficulty 3/5**
  - **What it teaches:** Probabilistic data structures; false positives.
  - **Acceptance criteria:** Large dataset fit in memory with acceptable FP rate.

- **B3. zxcvbn‑style scoring (lite)** — **Difficulty 3/5**
  - **What it teaches:** Pattern finding; dictionary + keyboard walks.
  - **Acceptance criteria:** Composite score more correlated with actual strength.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
