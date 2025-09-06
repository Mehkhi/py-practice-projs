### 13) Email Sender (CLI)
**What you’re building:** Send templated emails via SMTP (test account).
**Core skills:** `smtplib`, SSL/TLS, MIME, secrets handling.

#### Required Features
- **R1. SMTP client with TLS** — **Difficulty 2/5**
  - **What it teaches:** Auth flows; ports; STARTTLS vs SMTPS.
  - **Acceptance criteria:** Connects and sends via test SMTP; bad creds handled.

- **R2. Template rendering** — **Difficulty 2/5**
  - **What it teaches:** Jinja2 templates; variables from JSON/CSV.
  - **Acceptance criteria:** Personalization fields substituted correctly.

- **R3. Dry‑run preview** — **Difficulty 1/5**
  - **What it teaches:** Printing composed emails before send.
  - **Acceptance criteria:** `--dry-run` prints payload; sends nothing.

- **R4. Attachments & rate‑limit** — **Difficulty 2/5**
  - **What it teaches:** MIME parts; respecting provider rate limits.
  - **Acceptance criteria:** Attaches files; delays between sends configurable.

#### Bonus Features
- **B1. Exponential backoff on failure** — **Difficulty 2/5**
  - **What it teaches:** Retry with jitter; idempotency (avoid duplicates).
  - **Acceptance criteria:** Retries logged; stops after max attempts.

- **B2. CSV mail merge** — **Difficulty 2/5**
  - **What it teaches:** Batch personalization; per‑row status tracking.
  - **Acceptance criteria:** Success/failure report CSV produced.

- **B3. Signed messages (DKIM, optional)** — **Difficulty 4/5**
  - **What it teaches:** Email signing basics; deliverability.
  - **Acceptance criteria:** Documented setup; signatures added where supported.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
