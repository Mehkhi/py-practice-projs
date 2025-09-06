### 26) Platform Starter Kits
**What you’re building:** Cookiecutters/templates for teams to bootstrap secure apps.
**Core skills:** Cookiecutter, templates, docs, DX design.

#### Required Features
- **R1. Templates with secure defaults** — **Difficulty 2/5**
  - **What it teaches:**
    - App skeletons with logging, metrics, health checks, security headers.
  - **Acceptance criteria:**
    - New app passes lint/tests/security scans out of the box.

- **R2. CI/CD included** — **Difficulty 2/5**
  - **What it teaches:**
    - GH Actions with tests, lint, build, release.
  - **Acceptance criteria:**
    - Generated repo has working CI on first push.

- **R3. DX & docs** — **Difficulty 2/5**
  - **What it teaches:**
    - READMEs, issue templates, pre‑commit, contribution guide.
  - **Acceptance criteria:**
    - New devs can ship a feature in < 1 day following docs.

- **R4. Update mechanism** — **Difficulty 2/5**
  - **What it teaches:**
    - Template versioning and upgrade commands.
  - **Acceptance criteria:**
    - Existing projects can pull template updates with minimal conflicts.

#### Bonus Features
- **B1. Internal portal UI** — **Difficulty 3/5**
  - **Teaches:** Self‑service scaffolding with RBAC.
  - **Acceptance:** Portal provisions repos with correct settings.
- **B2. Telemetry & governance** — **Difficulty 2/5**
  - **Teaches:** Template usage metrics; policy checks.
  - **Acceptance:** Reports show adoption; non‑compliant repos flagged.
- **B3. Plugin architecture** — **Difficulty 3/5**
  - **Teaches:** Extensible generators via entry points.
  - **Acceptance:** Teams add plugins without forking template.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
