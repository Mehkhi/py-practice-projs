### 3) gRPC Microservices Pair
**What you’re building:** User and Order services communicating over gRPC.
**Core skills:** Protobuf contracts, gRPC servers/clients, compatibility.

#### Required Features
- **R1. Protos & codegen** — **Difficulty 2/5**
  - **Teaches:** Service/Message design; reserved fields; backward compatibility.
  - **Acceptance:** `protoc`/`grpclib` generate clients/servers; versions documented.
- **R2. Server stubs & interceptors** — **Difficulty 3/5**
  - **Teaches:** Auth interceptors, deadlines, metadata.
  - **Acceptance:** Deadline exceeded handled; auth metadata required.
- **R3. Retries & idempotency** — **Difficulty 3/5**
  - **Teaches:** Retryable vs non‑retryable codes; idempotent method design.
  - **Acceptance:** Policies enforced; retries visible in logs.
- **R4. Client libraries** — **Difficulty 2/5**
  - **Teaches:** Packaging clients; timeouts; connection reuse.
  - **Acceptance:** Example app consumes both services with timeouts set.

#### Bonus Features
- **B1. Contract tests** — **Difficulty 3/5**
  - **Teaches:** Provider/consumer tests; golden responses.
  - **Acceptance:** Breaking proto changes caught in CI.
- **B2. Load testing** — **Difficulty 2/5**
  - **Teaches:** ghz/vegeta scenarios; latency SLOs.
  - **Acceptance:** Report with p95/p99 and throughput.
- **B3. Local mesh (Envoy)** — **Difficulty 4/5**
  - **Teaches:** mTLS, retries at proxy, circuit breaking.
  - **Acceptance:** Requests succeed through Envoy with policies applied.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
