### 24) GitHub Actions CI
**What you’re building:** CI to run tests, linting, and builds on each push.
**Core skills:** YAML pipelines, caching, matrices, artifacts.

#### Required Features
- **R1. Workflow YAML** — **Difficulty 2/5**
  - **What it teaches:** Jobs/steps; triggers; permissions.
  - **Acceptance criteria:** On push/PR, tests and linters run.

- **R2. Dependency caching** — **Difficulty 2/5**
  - **What it teaches:** Cache keys and performance trade‑offs.
  - **Acceptance criteria:** Subsequent runs are faster; cache key logged.

- **R3. Build & artifacts** — **Difficulty 2/5**
  - **What it teaches:** Packaging wheels; uploading artifacts.
  - **Acceptance criteria:** Artifacts downloadable from run.

- **R4. Matrix strategy** — **Difficulty 2/5**
  - **What it teaches:** Multi‑Python/OS testing.
  - **Acceptance criteria:** Jobs fan out and report status per cell.

#### Bonus Features
- **B1. Release on tags** — **Difficulty 2/5**
  - **Teaches:** Tag triggers; changelog generation.
  - **Acceptance:** Tagging `vX.Y.Z` triggers release job.

- **B2. Codecov integration** — **Difficulty 2/5**
  - **Teaches:** Coverage upload and gating.
  - **Acceptance:** Coverage badge in README; threshold enforced.

- **B3. Dependabot & linters** — **Difficulty 1/5**
  - **Teaches:** Automated dependency PRs; lint checks on PR.
  - **Acceptance:** Dependabot enabled; lint job required.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
