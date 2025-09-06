### 9) Distributed Scheduler
**What you’re building:** Cron‑like system with leader election and failover.
**Core skills:** Locks, heartbeats, leases, idempotent jobs.

#### Required Features
- **R1. Leader election & lease** — **Difficulty 3/5**
  - **What it teaches:**
    - Lease durations, renewal, fencing tokens.
  - **Acceptance criteria:**
    - Single active leader; takeover on failure within SLA.

- **R2. Cron parser & registry** — **Difficulty 3/5**
  - **What it teaches:**
    - Cron expressions, calendars, time zones.
  - **Acceptance criteria:**
    - Next‑run times match reference; edge cases (DST) tested.

- **R3. Idempotent job execution** — **Difficulty 3/5**
  - **What it teaches:**
    - Dedup keys, retries, misfire policies, jitter.
  - **Acceptance criteria:**
    - No duplicate effects under retries; misfires handled per policy.

- **R4. Pause/resume & monitoring** — **Difficulty 2/5**
  - **What it teaches:**
    - Operational controls; status APIs.
  - **Acceptance criteria:**
    - Jobs listable/filterable; pause/resume persists.

#### Bonus Features
- **B1. Sharded schedulers** — **Difficulty 3/5**
  - **Teaches:** Distributing cron across nodes.
  - **Acceptance:** Shards balance; hot shard detection present.
- **B2. Priority scheduling** — **Difficulty 2/5**
  - **Teaches:** Priority queues.
  - **Acceptance:** High priority moves earlier within window.
- **B3. History retention & audit** — **Difficulty 2/5**
  - **Teaches:** Job history and outcomes.
  - **Acceptance:** Query by date/status; export CSV.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
