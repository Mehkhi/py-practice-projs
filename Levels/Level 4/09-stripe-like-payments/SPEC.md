### 9) Stripe‑like Payments (Test Mode)
**What you’re building:** Test‑mode checkout sessions with webhook verification.
**Core skills:** Webhooks, signature verification, idempotency.

#### Required Features
- **R1. Checkout session & redirect** — **Difficulty 2/5**
  - **Teaches:** Creating sessions, returning success/cancel URLs.
  - **Acceptance:** Users reach hosted checkout and return to app with state.
- **R2. Webhook verification** — **Difficulty 3/5**
  - **Teaches:** Signing secrets, replay attack prevention.
  - **Acceptance:** Invalid signatures rejected; webhook retries handled.
- **R3. Idempotent operations** — **Difficulty 3/5**
  - **Teaches:** Idempotency keys; dedup of retries.
  - **Acceptance:** Replayed webhooks do not duplicate charges/orders.
- **R4. Receipts/refunds** — **Difficulty 2/5**
  - **Teaches:** Post‑payment flows; refund records.
  - **Acceptance:** Receipts stored; refunds update state and audit.

#### Bonus Features
- **B1. Error simulation** — **Difficulty 2/5**
  - **Teaches:** Simulating failures/timeouts to test resiliency.
  - **Acceptance:** Scenarios documented; system recovers as expected.
- **B2. Test cards catalog** — **Difficulty 1/5**
  - **Teaches:** QA coverage for payment cases.
  - **Acceptance:** List of test numbers and outcomes shown.
- **B3. Compensation transactions** — **Difficulty 3/5**
  - **Teaches:** Saga design for partial failures.
  - **Acceptance:** Failed steps compensated in order; idempotent.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
