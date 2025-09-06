### 24) Privacy‑Preserving Analytics
**What you’re building:** Aggregate metrics with differential privacy.
**Core skills:** DP mechanisms, sensitivity, epsilon accounting.

#### Required Features
- **R1. Mechanism (Laplace/Gaussian)** — **Difficulty 3/5**
  - **What it teaches:**
    - Sensitivity bounds; noise calibration.
  - **Acceptance criteria:**
    - Tests validate privacy budget vs error trade‑off.

- **R2. Composition/accounting** — **Difficulty 3/5**
  - **What it teaches:**
    - Budget tracking across queries; advanced composition.
  - **Acceptance criteria:**
    - Budgets enforced per user/session with audit trail.

- **R3. DP query API** — **Difficulty 3/5**
  - **What it teaches:**
    - Enforcing privacy at API; denial on exhausted budget.
  - **Acceptance criteria:**
    - API refuses over‑budget requests; returns calibrated results otherwise.

- **R4. Utility vs privacy plots** — **Difficulty 2/5**
  - **What it teaches:**
    - MSE vs epsilon curves; policy selection.
  - **Acceptance criteria:**
    - Plots generated and explained in README.

#### Bonus Features
- **B1. Federated learning sim** — **Difficulty 4/5**
  - **Teaches:** FedAvg; secure aggregation.
  - **Acceptance:** Round‑based training with DP noise; convergence shown.
- **B2. Membership inference tests** — **Difficulty 3/5**
  - **Teaches:** Attacks; mitigation evaluation.
  - **Acceptance:** Attack success rate reduced with DP.
- **B3. K‑anonymity lints** — **Difficulty 2/5**
  - **Teaches:** Static checks before DP.
  - **Acceptance:** Risky columns flagged with guidance.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
