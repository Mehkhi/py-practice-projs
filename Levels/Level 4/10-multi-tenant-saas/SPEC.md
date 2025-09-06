### 10) Multi‑Tenant SaaS
**What you’re building:** Single app hosting multiple tenants safely.
**Core skills:** SQLAlchemy, tenancy models, security boundaries.

#### Required Features
- **R1. Tenant isolation model** — **Difficulty 3/5**
  - **Teaches:** RLS (row‑level security) or schema‑per‑tenant; pros/cons.
  - **Acceptance:** Cross‑tenant data access prevented; tests enforce isolation.
- **R2. Tenant onboarding & quotas** — **Difficulty 2/5**
  - **Teaches:** Provisioning flows; per‑tenant limits.
  - **Acceptance:** Quotas enforced; errors explain limits.
- **R3. Billing hooks** — **Difficulty 2/5**
  - **Teaches:** Usage metering; invoicing hooks.
  - **Acceptance:** Usage recorded per tenant; monthly reports.
- **R4. Audit trails** — **Difficulty 2/5**
  - **Teaches:** Per‑tenant audit logs with actors.
  - **Acceptance:** Readable trail for sensitive actions.

#### Bonus Features
- **B1. Tenant migrations automation** — **Difficulty 3/5**
  - **Teaches:** Rolling schema updates tenant‑by‑tenant.
  - **Acceptance:** Progress logged; rollback procedure verified.
- **B2. Custom domains** — **Difficulty 2/5**
  - **Teaches:** Domain verification; SSL certs.
  - **Acceptance:** Tenant’s domain serves app securely.
- **B3. Data export/import** — **Difficulty 2/5**
  - **Teaches:** Per‑tenant backups; portability.
  - **Acceptance:** Tenant can export/import their data.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
