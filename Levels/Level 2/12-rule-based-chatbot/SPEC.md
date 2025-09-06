### 12) Rule‑Based Chatbot
**What you’re building:** A small FAQ assistant via patterns.
**Core skills:** regex, control flow, normalization.

#### Required Features
- **R1. Normalization pipeline** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, punctuation stripping, whitespace collapsing.
  - **Acceptance criteria:** Same intent recognized despite casing/punctuation.

- **R2. Intent patterns** — **Difficulty 2/5**
  - **What it teaches:** Regex design; capture groups for slots.
  - **Acceptance criteria:** Patterns drive responses; tests cover overlaps.

- **R3. Fallback default** — **Difficulty 1/5**
  - **What it teaches:** Guard rails when nothing matches; help text.
  - **Acceptance criteria:** Non‑matches produce friendly guidance.

- **R4. Conversation logging** — **Difficulty 1/5**
  - **What it teaches:** Appending JSONL transcripts; redacting secrets.
  - **Acceptance criteria:** Logs contain timestamp, input, intent, response.

#### Bonus Features
- **B1. Plug‑in handler architecture** — **Difficulty 3/5**
  - **What it teaches:** Dynamic imports; discovery; handler registry.
  - **Acceptance criteria:** New intents load without code changes.

- **B2. Context memory (short‑term)** — **Difficulty 3/5**
  - **What it teaches:** Sliding windows; simple state machines.
  - **Acceptance criteria:** Follow‑ups resolve pronouns within N turns.

- **B3. Test harness** — **Difficulty 2/5**
  - **What it teaches:** Golden files for input→output tests.
  - **Acceptance criteria:** `pytest` runs and validates sample conversations.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
