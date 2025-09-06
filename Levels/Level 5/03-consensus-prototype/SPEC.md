### 3) Consensus (Raft) Prototype
**What you’re building:** Replicated log with leader election and compaction.
**Core skills:** State machines, RPC, timeouts, quorum.

#### Required Features
- **R1. Leader election & terms** — **Difficulty 4/5**
  - **What it teaches:**
    - Election timeouts, randomized backoff, majority quorum.
  - **Acceptance criteria:**
    - Single leader emerges; re‑election on leader crash.

- **R2. Log replication & commit index** — **Difficulty 4/5**
  - **What it teaches:**
    - AppendEntries RPC, log matching property, commit rules.
  - **Acceptance criteria:**
    - Writes acknowledged after majority commit; followers converge.

- **R3. Snapshot/installSnapshot** — **Difficulty 4/5**
  - **What it teaches:**
    - Log compaction; truncated prefix; state machine snapshots.
  - **Acceptance criteria:**
    - Followers catch up via snapshots; memory bounded under churn.

- **R4. Fault injection tests** — **Difficulty 4/5**
  - **What it teaches:**
    - Partition, reordering, duplication; safety/liveness checks.
  - **Acceptance criteria:**
    - Linearizable command sequence verified on a Jepsen‑style harness.

#### Bonus Features
- **B1. Joint consensus membership changes** — **Difficulty 4/5**
  - **Teaches:** Safe config changes.
  - **Acceptance:** Add/remove node without availability loss.
- **B2. Pre‑vote optimization** — **Difficulty 3/5**
  - **Teaches:** Avoiding disruptive elections.
  - **Acceptance:** Fewer term bumps during partitions.
- **B3. Log compaction policy** — **Difficulty 3/5**
  - **Teaches:** Snapshot intervals vs throughput.
  - **Acceptance:** Tunable trade‑off documented with benchmarks.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
