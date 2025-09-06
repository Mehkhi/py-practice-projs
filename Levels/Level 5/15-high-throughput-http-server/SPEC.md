### 15) High‑Throughput HTTP Server
**What you’re building:** Tune uvicorn/uvloop, pools, and kernel for throughput.
**Core skills:** Async IO, load testing, profiling, kernel tuning.

#### Required Features
- **R1. Baseline & SLOs** — **Difficulty 2/5**
  - **What it teaches:**
    - Defining p50/p95/p99 targets; capacity planning.
  - **Acceptance criteria:**
    - Baseline charts saved; SLOs documented.

- **R2. Load tests & flamecharts** — **Difficulty 3/5**
  - **What it teaches:**
    - `wrk`/`hey`/`k6` runs; py‑spy/eBPF profiles.
  - **Acceptance criteria:**
    - Flamegraphs identify top bottlenecks; regressions tracked.

- **R3. Optimizations** — **Difficulty 3/5**
  - **What it teaches:**
    - Keepalive tuning, threadpools, zero‑copy (`sendfile`).
  - **Acceptance criteria:**
    - Throughput improved ≥ X%; tail latency reduced.

- **R4. Backpressure & overload protection** — **Difficulty 3/5**
  - **What it teaches:**
    - Queue limits, 503s, shed load, circuit breakers.
  - **Acceptance criteria:**
    - Under overload, system stays responsive with bounded latency.

#### Bonus Features
- **B1. TLS optimization** — **Difficulty 3/5**
  - **Teaches:** HTTP/2, ciphers, session resumption.
  - **Acceptance:** TLS adds minimal overhead; documented.
- **B2. Kernel tuning** — **Difficulty 3/5**
  - **Teaches:** SOMAXCONN, rmem/wmem, TCP knobs.
  - **Acceptance:** Bench vs defaults; wins recorded.
- **B3. eBPF profiling** — **Difficulty 3/5**
  - **Teaches:** System‑wide visibility.
  - **Acceptance:** Profiles correlate app ↔ kernel time.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
