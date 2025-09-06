### 22) Security Hardening
**What you’re building:** Secure defaults across services and code.
**Core skills:** Bandit, pip‑audit, input validation, headers, cookies.

#### Required Features
- **R1. Dependency scanning** — **Difficulty 1/5**
  - **Teaches:** `pip‑audit`/`pip‑tools`, CVE handling.
  - **Acceptance:** No high‑severity vulns; remediations tracked.
- **R2. Static analysis** — **Difficulty 2/5**
  - **Teaches:** Bandit rules; custom plugins for org standards.
  - **Acceptance:** Violations triaged or fixed.
- **R3. Web security headers** — **Difficulty 2/5**
  - **Teaches:** CSP, HSTS, XFO, XSS‑Protection.
  - **Acceptance:** Headers present; CSP reports configured.
- **R4. Input validation** — **Difficulty 2/5**
  - **Teaches:** Pydantic validators; deny lists; canonicalization.
  - **Acceptance:** Fuzz tests for critical endpoints pass.

#### Bonus Features
- **B1. Signed service requests** — **Difficulty 3/5**
  - **Teaches:** HMAC signatures; replay prevention.
  - **Acceptance:** Signature verified; skew handled.
- **B2. Secrets rotation** — **Difficulty 2/5**
  - **Teaches:** Rotating keys with zero downtime.
  - **Acceptance:** Plan/runbook; rotation test completes.
- **B3. Threat modeling doc** — **Difficulty 2/5**
  - **Teaches:** STRIDE/LINDDUN basics.
  - **Acceptance:** Document with mitigations and owners.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
