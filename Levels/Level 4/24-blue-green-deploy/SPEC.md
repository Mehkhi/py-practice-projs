### 24) Blue/Green Deploy (Compose)
**What you’re building:** Switch traffic between two app versions safely.
**Core skills:** Nginx routing, healthchecks, rollback, smoke tests.

#### Required Features
- **R1. Two versions running** — **Difficulty 2/5**
  - **Teaches:** Compose overrides; side‑by‑side deployments.
  - **Acceptance:** Both `blue` and `green` are reachable; status endpoint OK.
- **R2. Router config** — **Difficulty 2/5**
  - **Teaches:** Nginx upstreams; health checks; stickiness.
  - **Acceptance:** Switch controlled by one flag/env; logs confirm.
- **R3. Smoke & health checks** — **Difficulty 2/5**
  - **Teaches:** Health endpoints; automated smoke tests.
  - **Acceptance:** Bad `green` blocks cutover; logs show failure.
- **R4. Drain connections & rollback** — **Difficulty 2/5**
  - **Teaches:** Graceful shutdown; quick rollback.
  - **Acceptance:** Cutover has no dropped requests; rollback succeeds.

#### Bonus Features
- **B1. Canary percent rollout** — **Difficulty 3/5**
  - **Teaches:** Weighted routing.
  - **Acceptance:** 5%→100% rollout with metrics gating.
- **B2. Database migration toggle** — **Difficulty 3/5**
  - **Teaches:** Expand/contract migrations.
  - **Acceptance:** Double‑write period documented; no data loss.
- **B3. Release notes automation** — **Difficulty 1/5**
  - **Teaches:** CI step to compile changes.
  - **Acceptance:** Artifact attached to deploy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
