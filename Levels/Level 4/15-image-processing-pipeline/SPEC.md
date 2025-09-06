### 15) Image Processing Pipeline
**What you’re building:** Transform images at throughput with queues and retries.
**Core skills:** Pillow/OpenCV, workers, throughput tuning, metrics.

#### Required Features
- **R1. Worker pool & queue** — **Difficulty 3/5**
  - **Teaches:** Producer/consumer, backpressure, visibility timeouts.
  - **Acceptance:** Throughput charted; no unbounded queue growth.
- **R2. Transform chain** — **Difficulty 2/5**
  - **Teaches:** Resize/filter/OCR steps; idempotence.
  - **Acceptance:** Failed step retried; partial results quarantined.
- **R3. Error handling & retries** — **Difficulty 2/5**
  - **Teaches:** Retry policies; poison queue.
  - **Acceptance:** Persistent failures end up in DLQ with reason.
- **R4. Metrics & dashboards** — **Difficulty 2/5**
  - **Teaches:** Latency histograms; per‑stage rates; alarms.
  - **Acceptance:** Dashboards show bottlenecks; alert on backlog.

#### Bonus Features
- **B1. GPU acceleration (explore)** — **Difficulty 3/5**
  - **Teaches:** OpenCV/CUDA or PyTorch for ops.
  - **Acceptance:** Benchmarks show speedup or documented trade‑offs.
- **B2. Dedup via perceptual hash** — **Difficulty 3/5**
  - **Teaches:** pHash; near‑duplicate detection.
  - **Acceptance:** Duplicates skipped; stats reported.
- **B3. Content moderation stub** — **Difficulty 2/5**
  - **Teaches:** Simple classifiers/heuristics.
  - **Acceptance:** Flagged images routed differently.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
