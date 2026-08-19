---
name: cloudrun-ops
description: Google Cloud Run compute plane operations, Workload Identity Federation (WIF) setup, automated CI/CD deployment, container troubleshooting, memory limits, and zero-downtime rollback.
---

# Google Cloud Run Compute Plane Operations Skill

Use this skill when deploying, inspecting, diagnosing, or managing the **Credence Compute Plane** on Google Cloud Run v2.

---

## 1. Quick Reference Commands (`Justfile`)

All Cloud Run operations are managed via the canonical parameterized `just gcp [action] [arg]` recipe family with automated `gcloud` preflight checks:

| Command | Action | Description |
| :--- | :--- | :--- |
| `just preflight gcloud` | Preflight Gate | Verifies `gcloud` binary installation and active authenticated account. |
| `just gcp status` | Status Table | Displays active Cloud Run revision, image tag, CPU/memory, and traffic split. |
| `just gcp logs [limit]` | Forensics | Queries structured Cloud Run logs via `gcloud logging read` (default: 30 lines). |
| `just gcp tail` | Live Stream | Streams real-time container logs via `gcloud beta run services logs tail`. |
| `just gcp revisions` | Revision History | Lists all historical revisions with author, deploy timestamp, and traffic split. |
| `just gcp describe` | Deep Specification | Dumps full JSON/YAML service specification. |
| `just gcp probe` | Multi-Probe | Probes `/health`, `/api/health`, `/sse`, `/api/reports`, and `/api/sifter/status`. |
| `just gcp germinate [burst]` | Remote Sifting | Invokes remote `/api/germinate` endpoint to trigger Miracle-Gro ignition. |
| `just gcp rollback <revision>` | Safe Revert | Rolls back 100% traffic allocation to a previous healthy revision. |
| `just deploy backend` | Safe Deployment | Submits container build via Cloud Build, deploys to Cloud Run, and executes health probe. |

---

## 2. Infrastructure & Compute Sizing Baseline

- **Resource Limits**:
  - **Memory Baseline**: **1Gi (`1024Mi`)**. Headless browser parsing (Playwright) during initial feed sifting / ignition requires ~520 MiB peak memory. Setting memory below 1Gi causes container OOM exit during cold boot.
  - **CPU Baseline**: **1.0 vCPU**.
  - **Scale-to-Zero**: `min_instance_count = 0` (idle compute cost = $0.00).
- **Canonical Container Image**:
  - `gcr.io/credence-prod-505902/credence-server:latest`

---

## 3. Workload Identity Federation (WIF) Setup for GitHub Actions

To enable automated GitHub Actions deployment from `.github/workflows/deploy-backend.yml`:

```bash
# 1. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --project="credence-prod-505902" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Create OIDC Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="credence-prod-505902" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Grant Service Account Access
gcloud iam service-accounts add-iam-policy-binding "credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" \
    --project="credence-prod-505902" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/663899237633/locations/global/workloadIdentityPools/github-pool/attribute.repository/artibyrd/credence"

# 4. Configure GitHub Repository Secrets
gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER -R artibyrd/credence -b "projects/663899237633/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
gh secret set GCP_SERVICE_ACCOUNT -R artibyrd/credence -b "credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com"
```

---

## 4. Troubleshooting & Disaster Recovery

- **Cold Boot Timeouts**: Ensure Starlette lifespan auto-germination executes in a background `asyncio.create_task` so the HTTP server yields immediately.
- **Container OOM (Exit 137)**: If container exits with `Memory limit exceeded`, increase memory with `gcloud run deploy credence-server --memory 1Gi`.
- **Instant Rollback**: If a newly deployed revision has issues:
  ```bash
  just gcp revisions
  just gcp rollback credence-server-00004-xxx
  ```

---

## 5. Build Context Optimization & Fast Remote Builds

- **Context Exclusion Payload (<5 MB)**:
  - Always maintain synchronized `.dockerignore` and `.gcloudignore` manifests.
  - Exclude `.venv/`, `terraform/`, `data/`, `.mypy_cache/`, `.pytest_cache/`, `tests/`, `docs/`, and `web/` so upload archives remain ~2 MB instead of 800+ MB.
- **Lean Container Builds (`--without dev`)**:
  - Production `Dockerfile` stages must invoke `poetry install --without dev --no-root` and `poetry install --without dev`.
  - Use BuildKit cache mounts (`--mount=type=cache,target=/root/.cache/pypoetry`) to preserve package wheel caches across incremental rebuilds.
- **Cloud Build Concurrency**:
  - In `cloudbuild.yaml`, configure `waitFor: ['-']` on independent validation stages (`quality-gate` Ruff/Mypy and `test-gate` Pytest) to run them concurrently before container compilation.

---

## 6. Scale-to-Zero Cold Start Optimization Invariants

When deploying containers under `min_instance_count = 0`:

1. **Startup CPU Boost (`startup_cpu_boost = true` / `--cpu-boost`)**:
   Always enable Startup CPU Boost in Terraform and `gcloud run deploy`. This dynamically allocates 2–4 vCPUs during container boot to accelerate CPU-bound Python imports and AST compilation at $0.00 idle cost.
2. **Direct Virtualenv Binary Invocation (`PATH="/app/.venv/bin:$PATH"`)**:
   Execute `credence serve` directly rather than wrapping in `poetry run credence serve`, eliminating ~800–1,000ms of Poetry CLI environment resolution overhead.
3. **Build-Time Bytecode Precompilation (`compileall`)**:
   Images must precompile bytecode (`RUN python -m compileall -q /app/.venv /app/credence`) to eliminate on-the-fly AST compilation on cold boots.
4. **Aggressive HTTP Readiness Probing**:
   Configure `startup_probe` with `initial_delay_seconds = 1`, `period_seconds = 2`, `timeout_seconds = 2`, and `http_get` against `/health` so Cloud Run detects readiness within ~1.5–2.0s rather than waiting for 10-second default polling windows.
5. **Execution Environment Gen 2 (`--execution-environment=gen2`)**:
   Always enforce Second Generation execution environment for dedicated Linux kernel performance and faster filesystem page caching.


