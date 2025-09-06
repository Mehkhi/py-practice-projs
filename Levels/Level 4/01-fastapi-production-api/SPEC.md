### 1) FastAPI Production API
**What you’re building:** JWT‑secured API with roles, rate limit, and versioned endpoints.
**Core skills:** FastAPI, OAuth2/JWT, DI, pydantic, error mapping.

#### Required Features
- **R1. Auth & roles (JWT/OAuth2)** — **Difficulty 3/5**
  - **Teaches:** Token issuance/verification, scopes, refresh vs short‑lived tokens.
  - **Acceptance:** Protected endpoints require valid JWT; role‑gated routes enforced; token expiry honored.
- **R2. Validation & error mapping** — **Difficulty 2/5**
  - **Teaches:** Pydantic models/validators; converting exceptions to JSON errors.
  - **Acceptance:** 4xx/5xx payloads follow a consistent schema; field errors show paths.
- **R3. Pagination/filter/sort** — **Difficulty 2/5**
  - **Teaches:** Stable ordering, limits/offsets, defensive defaults.
  - **Acceptance:** `?limit&offset&sort` work; out‑of‑range values clamped; responses include paging hints.
- **R4. Versioned API & rate limiting** — **Difficulty 3/5**
  - **Teaches:** `/v1` vs `/v2` routing, deprecation headers; client throttling.
  - **Acceptance:** Separate routers for versions; 429 returned on limit with `Retry‑After`.

#### Bonus Features
- **B1. E2E tests with httpx + pytest** — **Difficulty 2/5**
  - **Teaches:** Test client, fixtures, token generation, happy/error paths.
  - **Acceptance:** CI runs green; coverage includes auth + pagination.
- **B2. Request/response logging & correlation IDs** — **Difficulty 2/5**
  - **Teaches:** Middleware for IDs; log context propagation.
  - **Acceptance:** Logs show ID across request lifecycle; sample trace linked.
- **B3. OpenAPI enhancements** — **Difficulty 2/5**
  - **Teaches:** Examples, error schemas, doc tags.
  - **Acceptance:** `/docs` shows examples; clients can be generated.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
