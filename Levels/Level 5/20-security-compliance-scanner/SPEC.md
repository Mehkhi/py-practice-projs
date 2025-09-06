### 20) Security & Compliance Scanner
**What you’re building:** Scan repos/infra for policy violations.
**Core skills:** AST/regex, config parsing, reporting, SBOM.

#### Required Features
- **R1. Rules engine** — **Difficulty 3/5**
  - **What it teaches:**
    - Rule DSL; severity levels; suppression policy.
  - **Acceptance criteria:**
    - Rules loaded from config; helpful messages.

- **R2. Repo + IaC scanning** — **Difficulty 3/5**
  - **What it teaches:**
    - AST for code; HCL/YAML for IaC; secret detection.
  - **Acceptance criteria:**
    - Findings categorized; false‑positive controls documented.

- **R3. Baselines & suppressions** — **Difficulty 2/5**
  - **What it teaches:**
    - Managing existing debt safely.
  - **Acceptance criteria:**
    - Baseline mode reduces noise; suppressions expire.

- **R4. Reports & SBOM** — **Difficulty 2/5**
  - **What it teaches:**
    - SARIF/JSON/HTML outputs; SBOM generation.
  - **Acceptance criteria:**
    - CI uploads reports; SBOM includes dependencies/versions.

#### Bonus Features
- **B1. Auto‑fix PR bot** — **Difficulty 3/5**
  - **Teaches:** Patch generation and PR creation.
  - **Acceptance:** Bot submits fixes; reviewers approve.
- **B2. DAST stub** — **Difficulty 3/5**
  - **Teaches:** Runtime checks; OWASP top‑10 probes.
  - **Acceptance:** Sample web app scanned with findings.
- **B3. Policy exceptions workflow** — **Difficulty 2/5**
  - **Teaches:** Approval/expiry.
  - **Acceptance:** Exceptions tracked and reviewed.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
