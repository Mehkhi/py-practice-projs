### 18) Schema Registry
**What you’re building:** Centralize schemas with versioning and codegen.
**Core skills:** Compatibility checks, generators, registries.

#### Required Features
- **R1. Schema storage & versioning** — **Difficulty 3/5**
  - **What it teaches:**
    - Semantic/compat levels; deprecation policy.
  - **Acceptance criteria:**
    - Breaking changes rejected; changelog maintained.

- **R2. Codegen clients** — **Difficulty 3/5**
  - **What it teaches:**
    - Template generation for languages; package layout.
  - **Acceptance criteria:**
    - Client compiles and serializes/deserializes correctly.

- **R3. Governance flow** — **Difficulty 3/5**
  - **What it teaches:**
    - Review/approve/publish with owners.
  - **Acceptance criteria:**
    - Audit trail and approvals recorded.

- **R4. Access control** — **Difficulty 2/5**
  - **What it teaches:**
    - RBAC per schema/namespace.
  - **Acceptance criteria:**
    - Unauthorized access blocked; logs show attempts.

#### Bonus Features
- **B1. Multi‑language SDKs** — **Difficulty 3/5**
  - **Teaches:** Polyglot client generation.
  - **Acceptance:** At least two languages supported.
- **B2. Client caching & ETags** — **Difficulty 2/5**
  - **Teaches:** Conditional fetch; cache busting.
  - **Acceptance:** Fewer network requests; correct refresh on change.
- **B3. Schema graph** — **Difficulty 2/5**
  - **Teaches:** Dependencies and references.
  - **Acceptance:** Graph visualized and queryable.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
