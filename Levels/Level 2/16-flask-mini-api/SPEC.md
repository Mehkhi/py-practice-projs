### 16) Flask Mini API
**What you’re building:** A tiny JSON API service.
**Core skills:** routing, JSON responses, blueprints, CORS.

#### Required Features
- **R1. Endpoints + blueprints** — **Difficulty 2/5**
  - **What it teaches:** Organizing routes and modularizing code.
  - **Acceptance criteria:** Namespaced routes; clean app factory.

- **R2. Input validation** — **Difficulty 2/5**
  - **What it teaches:** Marshmallow/pydantic‑style validation and error mapping.
  - **Acceptance criteria:** 400s include helpful messages with fields.

- **R3. Error handlers** — **Difficulty 1/5**
  - **What it teaches:** Centralized exception→response mapping.
  - **Acceptance criteria:** Consistent JSON error shape.

- **R4. CORS & config per env** — **Difficulty 1/5**
  - **What it teaches:** Environment configs; enabling specific origins.
  - **Acceptance criteria:** Dev vs prod configs documented and working.

#### Bonus Features
- **B1. OpenAPI/Swagger docs** — **Difficulty 2/5**
  - **What it teaches:** API discoverability and schemas.
  - **Acceptance criteria:** Docs served at `/docs`.

- **B2. API keys / simple auth** — **Difficulty 2/5**
  - **What it teaches:** Header parsing; secret rotation.
  - **Acceptance criteria:** Protected endpoint rejects missing/invalid keys.

- **B3. Rate limit** — **Difficulty 2/5**
  - **What it teaches:** Client‑side throttling via IP/key.
  - **Acceptance criteria:** Exceeding limits returns 429 with `Retry-After`.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
