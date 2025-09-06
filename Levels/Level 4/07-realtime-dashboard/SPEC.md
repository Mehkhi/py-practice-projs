### 7) Realtime Dashboard
**What you’re building:** Live metrics to frontend via WebSockets.
**Core skills:** FastAPI WebSockets, pub/sub, backpressure.

#### Required Features
- **R1. WebSocket server & auth** — **Difficulty 3/5**
  - **Teaches:** Connection lifecycle, token auth, origin checks.
  - **Acceptance:** Unauthorized connections denied; ping/pong keep‑alive.
- **R2. Pub/sub bridge** — **Difficulty 3/5**
  - **Teaches:** Channel fan‑out; topic subscriptions.
  - **Acceptance:** Clients receive only subscribed topics.
- **R3. Backpressure & rate limits** — **Difficulty 3/5**
  - **Teaches:** Drop/queue policies; slow consumer handling.
  - **Acceptance:** Slow clients don’t degrade server; metrics prove it.
- **R4. History buffer** — **Difficulty 2/5**
  - **Teaches:** Ring buffers; replay on connect.
  - **Acceptance:** New client receives last N events per topic.

#### Bonus Features
- **B1. SSE fallback** — **Difficulty 2/5**
  - **Teaches:** Server‑sent events as alternative.
  - **Acceptance:** Older browsers receive updates via SSE.
- **B2. Compression & batching** — **Difficulty 2/5**
  - **Teaches:** Message packing; trade‑offs.
  - **Acceptance:** Reduced bandwidth with acceptable latency.
- **B3. Frontend sample app** — **Difficulty 2/5**
  - **Teaches:** Minimal client; reconnect logic.
  - **Acceptance:** Demo shows charts updating live.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
