### 22) Chaos Engineering Toolkit
**What you’re building:** Inject faults and run resilience experiments.
**Core skills:** Failure modes, experiments, observability.

#### Required Features
- **R1. Fault injectors** — **Difficulty 3/5**
  - **What it teaches:**
    - CPU/memory pressure, kill, latency, packet loss.
  - **Acceptance criteria:**
    - Faults scoped by target with TTL; revert cleanly.

- **R2. Steady‑state checks** — **Difficulty 2/5**
  - **What it teaches:**
    - Defining measurable steady state and abort conditions.
  - **Acceptance criteria:**
    - Experiment aborts on SLO breach; logs/metrics captured.

- **R3. Blast radius & safety** — **Difficulty 2/5**
  - **What it teaches:**
    - Guardrails, allow‑lists, scheduling windows.
  - **Acceptance criteria:**
    - No experiments outside allowed scope/time.

- **R4. Reporting** — **Difficulty 2/5**
  - **What it teaches:**
    - Experiment results, learnings, action items.
  - **Acceptance criteria:**
    - Markdown/HTML report generated with outcomes.

#### Bonus Features
- **B1. Hypothesis generator** — **Difficulty 3/5**
  - **Teaches:** Suggesting likely weak points.
  - **Acceptance:** Hypotheses formulated from SLOs/topology.
- **B2. Real‑time guardrails** — **Difficulty 3/5**
  - **Teaches:** Pause/rollback on metrics symptoms.
  - **Acceptance:** Auto‑abort triggers verified in tests.
- **B3. Orchestrator integration** — **Difficulty 3/5**
  - **Teaches:** Kubernetes/Compose hooks.
  - **Acceptance:** Run chaos as a job with RBAC.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
