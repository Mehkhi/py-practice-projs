### 14) ML Model Serving
**What you’re building:** Serve a versioned ML model behind an API.
**Core skills:** FastAPI, model registry, A/B testing, drift alerts.

#### Required Features
- **R1. Model registry & versioning** — **Difficulty 3/5**
  - **Teaches:** Semantic versions; metadata; staging/prod.
  - **Acceptance:** Endpoint loads specific versions; fallback on load failure.
- **R2. Inference API** — **Difficulty 2/5**
  - **Teaches:** Typed request/response; timeouts.
  - **Acceptance:** p95 latency SLO met; errors mapped.
- **R3. A/B/Shadow traffic** — **Difficulty 3/5**
  - **Teaches:** Traffic splits; offline vs online eval.
  - **Acceptance:** Shadow requests don’t affect user; logs compare outputs.
- **R4. Drift detection** — **Difficulty 3/5**
  - **Teaches:** Feature/label drift, alerts.
  - **Acceptance:** Drift beyond threshold triggers alert.

#### Bonus Features
- **B1. Canary deploy + rollback** — **Difficulty 3/5**
  - **Teaches:** Gradual rollout with health metrics.
  - **Acceptance:** Rollback on regression; audit log updated.
- **B2. Batch inference job** — **Difficulty 2/5**
  - **Teaches:** Offline scoring at scale.
  - **Acceptance:** Job writes outputs with version tags.
- **B3. Explainability stub** — **Difficulty 2/5**
  - **Teaches:** Feature attributions (SHAP/LIME basics).
  - **Acceptance:** Endpoint returns simple attribution summary.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---
