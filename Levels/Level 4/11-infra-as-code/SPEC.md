### 11) Infra as Code (Pulumi/Terraform)
**What you’re building:** Reproducible infra stacks as code.
**Core skills:** State mgmt, modules, secrets, environments.

#### Required Features
- **R1. Module structure** — **Difficulty 2/5**
  - **Teaches:** Reusable modules and inputs/outputs.
  - **Acceptance:** Stacks compose modules; outputs documented.
- **R2. State & backends** — **Difficulty 2/5**
  - **Teaches:** Remote state storage; locking.
  - **Acceptance:** State stored remotely; locked during apply.
- **R3. Secrets mgmt** — **Difficulty 2/5**
  - **Teaches:** Encrypted variables; no secrets in VCS.
  - **Acceptance:** `terraform validate`/`pulumi config` secure.
- **R4. Dev/prod stacks** — **Difficulty 2/5**
  - **Teaches:** Per‑env configs; drift detection.
  - **Acceptance:** `plan` shows clean diffs; prod locked from accidental destroys.

#### Bonus Features
- **B1. Policy as code** — **Difficulty 3/5**
  - **Teaches:** OPA/Conftest checks.
  - **Acceptance:** CI fails on policy violations.
- **B2. Blueprints/templates** — **Difficulty 2/5**
  - **Teaches:** Starter stacks for common services.
  - **Acceptance:** New proj bootstraps in minutes.
- **B3. Cost estimates** — **Difficulty 2/5**
  - **Teaches:** Infracost integration.
  - **Acceptance:** PRs show cost delta.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
