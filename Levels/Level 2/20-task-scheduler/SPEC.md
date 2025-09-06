### 20) Task Scheduler
**What you’re building:** Run functions at intervals.
**Core skills:** `threading`/timers, datetime math, graceful shutdown.

#### Required Features
- **R1. Schedule registry** — **Difficulty 2/5**
  - **What it teaches:** Registering jobs with intervals; IDs.
  - **Acceptance criteria:** Add/list/remove jobs via CLI.

- **R2. Runner & timing** — **Difficulty 2/5**
  - **What it teaches:** Timer threads; drift correction.
  - **Acceptance criteria:** Jobs fire at expected times (within tolerance).

- **R3. Persist schedule** — **Difficulty 1/5**
  - **What it teaches:** Saving jobs to JSON; reload on start.
  - **Acceptance criteria:** Survives restarts with same plan.

- **R4. Pause/resume & shutdown** — **Difficulty 2/5**
  - **What it teaches:** Signals and state.
  - **Acceptance criteria:** Ctrl‑C causes graceful stop after running jobs.

#### Bonus Features
- **B1. Crontab parser** — **Difficulty 3/5**
  - **What it teaches:** Cron expressions and next‑run calculation.
  - **Acceptance criteria:** Cron strings map to correct runtimes.

- **B2. Jitter** — **Difficulty 1/5**
  - **What it teaches:** Spreading load to avoid thundering herds.
  - **Acceptance criteria:** Optional jitter applies +/- seconds.

- **B3. Missfire policies** — **Difficulty 2/5**
  - **What it teaches:** What to do if job is late (skip vs catch up).
  - **Acceptance criteria:** Policy configurable and enforced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
