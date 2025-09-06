### 21) Cost‑Aware Autoscaling Simulator
**What you’re building:** Simulate autoscaling under budgets and workloads.
**Core skills:** Queueing theory, scaling policies, plotting.

#### Required Features
- **R1. Workload & service model** — **Difficulty 3/5**
  - **What it teaches:**
    - Arrival processes, service times, queues.
  - **Acceptance criteria:**
    - Sim matches analytical expectations on simple M/M/1 cases.

- **R2. Scaling policies** — **Difficulty 3/5**
  - **What it teaches:**
    - Threshold/predictive scaling; cooldown; min/max bounds.
  - **Acceptance criteria:**
    - Policies configurable; stability under oscillation.

- **R3. Cost model** — **Difficulty 2/5**
  - **What it teaches:**
    - Instance/hour, egress, storage; energy (optional).
  - **Acceptance criteria:**
    - Cost tracked per scenario; plotted with SLA.

- **R4. SLA vs cost frontier** — **Difficulty 2/5**
  - **What it teaches:**
    - Pareto frontier visualization.
  - **Acceptance criteria:**
    - Frontier chart produced; scenario runner outputs CSV.

#### Bonus Features
- **B1. RL policy search** — **Difficulty 4/5**
  - **Teaches:** Bandits/RL for scaling.
  - **Acceptance:** Outperforms heuristics on synthetic workloads.
- **B2. Multi‑tier microservices** — **Difficulty 3/5**
  - **Teaches:** Cascading queues; bottlenecks.
  - **Acceptance:** Upstream/downstream interactions captured.
- **B3. Spot/preemptible economics** — **Difficulty 3/5**
  - **Teaches:** Interrupted instances; checkpointing.
  - **Acceptance:** Cost savings vs reliability charted.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
