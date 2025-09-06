### 11) Multi‑Client Chat Server
**What you’re building:** TCP chat server with rooms and private messages.
**Core skills:** sockets, threading, protocols, concurrency, persistence.

#### Required Features
- **R1. Protocol & message framing** — **Difficulty 3/5**
  - **What it teaches:** Line/length‑prefixed protocols; partial reads; keep‑alive.
  - **Acceptance criteria:** Handles fragmented packets and large messages.

- **R2. Threaded server & rooms** — **Difficulty 3/5**
  - **What it teaches:** Thread per client (or threadpool), room broadcast.
  - **Acceptance criteria:** 20+ clients join/leave and chat reliably.

- **R3. Usernames & private messages** — **Difficulty 2/5**
  - **What it teaches:** Routing to specific clients; presence tracking.
  - **Acceptance criteria:** `/pm @user` works; unknown user handled.

- **R4. Persistence (optional logs)** — **Difficulty 2/5**
  - **What it teaches:** Server logs; per‑room history.
  - **Acceptance criteria:** History saved with timestamps.

#### Bonus Features
- **B1. Asyncio implementation** — **Difficulty 3/5**
  - **Teaches:** `asyncio` sockets, tasks, cancellation.
  - **Acceptance:** Parity with threaded version under load.

- **B2. WebSocket gateway** — **Difficulty 3/5**
  - **Teaches:** Bridge TCP↔WS; simple web client.
  - **Acceptance:** Browser clients can join rooms via WS.

- **B3. Flood control & moderation** — **Difficulty 2/5**
  - **Teaches:** Rate limits; mute/kick tools.
  - **Acceptance:** Abusive clients throttled; admin commands work.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
