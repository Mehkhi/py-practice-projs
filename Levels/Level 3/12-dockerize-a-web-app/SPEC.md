### 12) Dockerize a Web App
**What you’re building:** Containerized Flask/FastAPI app with Compose.
**Core skills:** Dockerfile, Compose, env vars, volumes, healthchecks.

#### Required Features
- **R1. Dockerfile (multi‑stage)** — **Difficulty 2/5**
  - **What it teaches:** Slim images, dependency caching, non‑root user.
  - **Acceptance criteria:** Image builds reproducibly; `docker run` works.

- **R2. docker‑compose.yml** — **Difficulty 2/5**
  - **What it teaches:** Service definitions, env files, volumes, ports.
  - **Acceptance criteria:** `docker compose up` boots app + DB.

- **R3. Dev vs Prod configs** — **Difficulty 2/5**
  - **What it teaches:** Different compose overrides; debug on/off.
  - **Acceptance criteria:** Prod disables debug and mounts; dev enables.

- **R4. Healthchecks** — **Difficulty 1/5**
  - **What it teaches:** Command‑based health; restart policies.
  - **Acceptance criteria:** Unhealthy container auto‑restarted.

#### Bonus Features
- **B1. CI image build** — **Difficulty 2/5**
  - **Teaches:** GH Actions caching; tags by commit/branch.
  - **Acceptance:** CI pushes image to registry (local or GHCR).

- **B2. Image scanning** — **Difficulty 2/5**
  - **Teaches:** Trivy/Grype; vulnerability gating.
  - **Acceptance:** CI fails on high severity vulns.

- **B3. Multi‑arch builds** — **Difficulty 3/5**
  - **Teaches:** `buildx` and QEMU; ARM64/AMD64 images.
  - **Acceptance:** Both arch images available.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
