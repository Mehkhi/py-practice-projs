### 2) Auth Basics & Password Hashing
**What you’re building:** A standalone auth module and demo app that implements secure login flows.
**Core skills:** Hashing (argon2/bcrypt), sessions, secure cookies.

#### Required Features
- **R1. Password hashing & verification** — **Difficulty 2/5**
  - **What it teaches:** Peppering vs salting; parameter selection; migration strategies.
  - **Acceptance criteria:** Hash includes parameters; rehash on login if params outdated.

- **R2. Session management** — **Difficulty 2/5**
  - **What it teaches:** Secure cookie flags (HttpOnly, Secure, SameSite), session fixation prevention.
  - **Acceptance criteria:** New session ID issued on login/logout; cookies configured securely.

- **R3. Password reset tokens (dev email)** — **Difficulty 3/5**
  - **What it teaches:** Signed tokens with expiry; one‑time use; email templating.
  - **Acceptance criteria:** Reset link invalid after use/expiry; audit logged.

- **R4. Account lockout & rate limiting** — **Difficulty 3/5**
  - **What it teaches:** Brute‑force mitigation; cooldown vs exponential backoff.
  - **Acceptance criteria:** After N failures, further attempts delayed or blocked per policy.

#### Bonus Features
- **B1. 2FA via TOTP** — **Difficulty 3/5**
  - **Teaches:** Time‑based codes, clock skew, backup codes.
  - **Acceptance:** TOTP setup QR; verification required at login if enabled.

- **B2. OAuth login (Google/GitHub)** — **Difficulty 3/5**
  - **Teaches:** Federated identity, account linking.
  - **Acceptance:** First login links to local account; subsequent logins succeed.

- **B3. Password strength meter** — **Difficulty 2/5**
  - **Teaches:** zxcvbn‑style feedback; UX for suggestions.
  - **Acceptance:** Weak passwords flagged with actionable tips.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
