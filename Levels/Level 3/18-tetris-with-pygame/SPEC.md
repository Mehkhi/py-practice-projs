### 18) Tetris with pygame
**What you’re building:** Playable Tetris clone with scoring and levels.
**Core skills:** pygame loop, collision detection, game state, rendering.

#### Required Features
- **R1. Tetrominoes & rotation** — **Difficulty 3/5**
  - **What it teaches:** Piece systems (SRS), rotation kicks, state machines.
  - **Acceptance criteria:** All 7 pieces rotate/move without clipping.

- **R2. Collision & line clear** — **Difficulty 3/5**
  - **What it teaches:** Grid representation; collision checks; row clears.
  - **Acceptance criteria:** Lines clear; gravity and lock delay feel right.

- **R3. Scoring & levels** — **Difficulty 2/5**
  - **What it teaches:** Tetris scoring rules; speed scaling.
  - **Acceptance criteria:** Scores/levels update per line clears; UI shows HUD.

- **R4. Pause/resume & high scores** — **Difficulty 2/5**
  - **What it teaches:** Input handling; persistence to JSON.
  - **Acceptance criteria:** High scores saved/loaded; pause works.

#### Bonus Features
- **B1. Ghost piece & hold** — **Difficulty 2/5**
  - **Teaches:** Predictive rendering; swap mechanics.
  - **Acceptance:** Ghost shows landing; hold obeys rule (once per drop).

- **B2. Replays** — **Difficulty 3/5**
  - **Teaches:** Input recording; determinism.
  - **Acceptance:** Recorded games replay identically.

- **B3. Skins & themes** — **Difficulty 1/5**
  - **Teaches:** Asset management.
  - **Acceptance:** Selectable theme packs.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
