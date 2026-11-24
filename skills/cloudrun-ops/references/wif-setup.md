# Workload Identity Federation (WIF) Least-Privileged Setup for CI/CD

Complete `gcloud` and `gh secret` commands to enable automated GitHub Actions deployment across Dev (`credence-dev-495173`) and Production (`credence-prod-505902`) without long-lived keys.

---

## A. Dev Environment (`credence-dev-495173`)

```bash
# 1. Create Pool and Provider with repo condition
gcloud iam workload-identity-pools create "github-pool" --project="credence-dev-495173" --location="global" --display-name="GitHub Actions Pool"
gcloud iam workload-identity-pools providers create-oidc "github-provider" --project="credence-dev-495173" --location="global" --workload-identity-pool="github-pool" --display-name="GitHub Actions Provider" --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" --attribute-condition="assertion.repository=='artibyrd/credence'" --issuer-uri="https://token.actions.githubusercontent.com"

# 2. Resource-Scoped Service Account Bindings
gcloud iam service-accounts add-iam-policy-binding "credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com" --project="credence-dev-495173" --role="roles/iam.workloadIdentityUser" --member="principalSet://iam.googleapis.com/projects/865363499314/locations/global/workloadIdentityPools/github-pool/attribute.repository/artibyrd/credence"
gcloud iam service-accounts add-iam-policy-binding "credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com" --project="credence-dev-495173" --role="roles/iam.serviceAccountUser" --member="serviceAccount:credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com"

# 3. Project-Level Least-Privilege Roles
gcloud projects add-iam-policy-binding "credence-dev-495173" --member="serviceAccount:credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com" --role="roles/run.developer"
gcloud projects add-iam-policy-binding "credence-dev-495173" --member="serviceAccount:credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.builder"

# 4. Storage Bucket Least-Privilege Persistence Role
gcloud storage buckets add-iam-policy-binding "gs://credence-dev-495173-seeds-nexus" --member="serviceAccount:credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
```

---

## B. Production Environment (`credence-prod-505902`)

```bash
# 1. Create Pool and Provider with repo condition
gcloud iam workload-identity-pools create "github-pool" --project="credence-prod-505902" --location="global" --display-name="GitHub Actions Pool"
gcloud iam workload-identity-pools providers create-oidc "github-provider" --project="credence-prod-505902" --location="global" --workload-identity-pool="github-pool" --display-name="GitHub Actions Provider" --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" --attribute-condition="assertion.repository=='artibyrd/credence'" --issuer-uri="https://token.actions.githubusercontent.com"

# 2. Resource-Scoped Service Account Bindings
gcloud iam service-accounts add-iam-policy-binding "credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" --project="credence-prod-505902" --role="roles/iam.workloadIdentityUser" --member="principalSet://iam.googleapis.com/projects/663899237633/locations/global/workloadIdentityPools/github-pool/attribute.repository/artibyrd/credence"
gcloud iam service-accounts add-iam-policy-binding "credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" --project="credence-prod-505902" --role="roles/iam.serviceAccountUser" --member="serviceAccount:credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com"

# 3. Project-Level Least-Privilege Roles
gcloud projects add-iam-policy-binding "credence-prod-505902" --member="serviceAccount:credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" --role="roles/run.developer"
gcloud projects add-iam-policy-binding "credence-prod-505902" --member="serviceAccount:credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.builder"

# 4. Storage Bucket Least-Privilege Persistence Role
gcloud storage buckets add-iam-policy-binding "gs://credence-prod-505902-seeds-nexus" --member="serviceAccount:credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
```

---

## C. Configure GitHub Repository Secrets

```bash
gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER -R artibyrd/credence -b "projects/663899237633/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
gh secret set GCP_SERVICE_ACCOUNT -R artibyrd/credence -b "credence-cloud-run-sa@credence-prod-505902.iam.gserviceaccount.com"
gh secret set GCP_PROJECT_ID -R artibyrd/credence -b "credence-prod-505902"
gh secret set GCP_DEV_WORKLOAD_IDENTITY_PROVIDER -R artibyrd/credence -b "projects/865363499314/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
gh secret set GCP_DEV_SERVICE_ACCOUNT -R artibyrd/credence -b "credence-cloud-run-sa@credence-dev-495173.iam.gserviceaccount.com"
gh secret set GCP_DEV_PROJECT_ID -R artibyrd/credence -b "credence-dev-495173"
```
