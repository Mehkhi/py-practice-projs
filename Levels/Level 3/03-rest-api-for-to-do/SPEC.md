### 3) REST API for To‑Do (FastAPI)
**What you’re building:** A JSON API exposing To‑Do CRUD with typed schemas.
**Core skills:** FastAPI, pydantic, dependency injection, OpenAPI.

#### Required Features
- **R1. Pydantic models & validation** — **Difficulty 2/5**
  - **What it teaches:** Request/response models, field validators, error mapping.
  - **Acceptance criteria:** Invalid payloads return 422 with field errors.

- **R2. CRUD endpoints** — **Difficulty 2/5**
  - **What it teaches:** REST semantics (status codes, idempotence), path/query params.
  - **Acceptance criteria:** `POST/GET/PATCH/DELETE /todos` behave per spec; 404s for missing IDs.

- **R3. Filtering, sorting, pagination** — **Difficulty 2/5**
  - **What it teaches:** Query parameter design, limit/offset, stable ordering.
  - **Acceptance criteria:** `?q=open&sort=due_at&limit=20&offset=20` works.

- **R4. Error handlers & OpenAPI docs** — **Difficulty 1/5**
  - **What it teaches:** Exception handlers; auto docs at `/docs`.
  - **Acceptance criteria:** Custom errors map to JSON; schema examples present.

#### Bonus Features
- **B1. JWT auth** — **Difficulty 3/5**
  - **Teaches:** Token issuance/verification, scopes/claims, expiry.
  - **Acceptance:** Protected endpoints require `Authorization: Bearer <token>`.

- **B2. API keys** — **Difficulty 2/5**
  - **Teaches:** Header/query key acceptance; rotation.
  - **Acceptance:** Requests without valid key receive 401/403 with docs link.

- **B3. Rate limiting** — **Difficulty 2/5**
  - **Teaches:** Client quota enforcement; 429 handling.
  - **Acceptance:** Limits applied per key/IP with `Retry-After` header.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
