# Build Plan: Auth Basics Password Hashing

## 0. Strategy & Architecture Decisions (Half Day)
- Pick FastAPI + SQLAlchemy + Alembic + PostgreSQL stack; stick to sync ORM calls behind async endpoints.
- Choose `passlib[bcrypt]` for hashing, `itsdangerous` for signed tokens, and Starlette sessions backed by secure cookies.
- Define module layout from SPEC (`app/`, `tests/`, `docs/`, `migrations/`) and tooling (`pyproject.toml`, `ruff`, `black`, `mypy --strict`).
- Document environment variables (`DATABASE_URL`, `SECRET_KEY`, `EMAIL_SENDER`, etc.) up front in `README.md`.

## 1. Project Scaffolding & Tooling (Day 1)
- Initialize FastAPI app factory, settings module, logging config, and dependency container.
- Configure Alembic, create initial migration, and wire `makefile`/`tox` or simple `task` runner for lint/test/check.
- Add base Dockerfile + docker-compose for app + Postgres + Mailhog, plus CI workflow skeleton (pytest + mypy + ruff + docker build).

## 2. Data Modeling & Infrastructure (Day 1-2)
- Design `users`, `email_verifications`, `password_reset_tokens`, `login_attempts`, `sessions` tables with required indexes/constraints.
- Implement SQLAlchemy models + Pydantic schemas; add repository/service layers for persistence.
- Seed Alembic migrations for schema + constraints and ensure downgrade paths.
- Integrate email provider abstraction (dev: console or Mailhog; prod: SMTP placeholder).

## 3. Core Auth Flows (Day 2-3)
- **Registration**: validate unique email, hash password with bcrypt, store user, send verification email with signed token.
- **Email Verification**: verify token, activate account, log audit event.
- **Login/Logout**: verify credentials, enforce verified email, generate session id, store server-side session, set HttpOnly/SameSite cookie, add logout endpoint to revoke session.
- **Account Lockout & Rate Limiting**: track failed attempts per IP/user via `login_attempts` + Redis counter; lock after threshold with exponential backoff messaging.

## 4. Password Maintenance Flows (Day 3)
- **Password Reset**: generate expiring token, email link, validate + allow password update, invalidate outstanding sessions on success.
- **Password Change**: require current password, trigger session invalidation, reissue cookie.
- **Security Hardening**: add structured logging, custom exception hierarchy, standard API error envelope, and audit trail entries.

## 5. API Surface & Documentation (Day 3-4)
- Define versioned REST routes (`/api/v1/auth/*`, `/api/v1/users/me`) with OpenAPI tags and schemas.
- Add docs to `docs/ARCHITECTURE.md` covering sequence diagrams, data flow, locking strategy, and performance considerations.
- Expand `README.md` with setup, env vars, docker/dev instructions, troubleshooting, and API usage examples (cURL + HTTPie).

## 6. Testing Strategy (Throughout; Final Push Day 4)
- Unit tests for hashing utilities, token helpers, repositories (use sqlite in-memory / transactional fixtures).
- Integration tests hitting FastAPI app with TestClient for registration, login, password reset, and lockout paths.
- E2E smoke tests via docker-compose (containerized Postgres + Mailhog) to ensure flows against real DB + email service.
- Keep 15-25 tests total, target >70% coverage, and run `coverage html` locally; enforce via CI.

## 7. Quality Gates & Delivery (Day 4-5)
- Ensure mypy strict, ruff, black, and tests all pass locally + in CI.
- Verify Docker image builds and `docker-compose up` boots app + dependencies.
- Review logging output, confirm secrets are sourced from env vars only, and run security checks (`pip-audit`, `bandit` if time).
- Finalize CHANGELOG (if needed), tag release, and document next steps (2FA, OAuth) referencing Bonus checklist.

## Traceability to Checklist
- Required features: sections 3–4 map directly to hashing, registration, login, verification, reset, and lockout functionality.
- Completion criteria: sections 1, 5, 6, 7 cover docs, tooling, typing, linting, logging, tests, Docker, and performance notes.
- Stretch goals: note 2FA/OAuth as follow-up enhancements after baseline delivery.
