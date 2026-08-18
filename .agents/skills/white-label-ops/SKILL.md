---
name: white-label-ops
description: Scaffold independent sovereign federation organizations (credence init-org), validate multi-cloud Terraform templates (GCP and Cloudflare), and deploy zero-build multi-domain edge routing.
---

# White-Label Federation & Multi-Cloud Infrastructure Skill

Use this skill when deploying, provisioning, or scaffolding sovereign federated Credence networks.

---

## Core Commands
- `credence init-org <org-name> --domain <domain> --region us-central1`: Scaffold turnkey organization.
- `just gcp-build`: Build container image on Google Cloud Build and push to GCR.
- `just tf-plan` / `just tf-apply`: Plan and apply multi-cloud Terraform configurations across Cloudflare and GCP.
- `just seed-sync`: Synchronize signed genesis seeds (`peers.json`) and taxonomy catalogs to GCS origin buckets.
- `just tf-validate`: Validate Terraform configurations across Cloudflare and GCP modules.
- `just serve-web`: Launch local preview server for visual Mk1 Eyeball review of web artifacts.

---

## Multi-Cloud Architecture & Edge Topology
- **Google Cloud Platform (GCP)**:
  - **Cloud Run v2**: Compute engine for FastMCP 2.0 SSE (`/sse`) with scale-to-zero compute savings and IAM public invoker policy.
  - **Secret Manager**: Secure custody for reasoning engine API keys (`credence-gemini-api-key`).
  - **Google Cloud Storage (GCS)**: Durable origins for genesis seeds (`peers.json`) and taxonomy catalogs (`/v1/*.json`).
- **Cloudflare (Zero-Build Edge Network)**:
  - **Zero-Build Static Assets**: Native ES Modules with zero npm dependencies, zero build toolchains.
  - **Multi-Domain Edge Router (`_worker.js`)**: Single edge worker routing across apex domains and subdomains (`credence.run`, `credence.nexus`, `credence.foundation`, `credence.report`).
  - **FastMCP Reverse Proxy**: Intercepts `mcp.<domain>` traffic, rewrites internal `Host` header to Cloud Run service URL, and streams real-time Server-Sent Events with global CORS headers.

---

## Production Edge Router Invariants
1. **Worker Asset Binding**: Always specify `binding = "ASSETS"` in `wrangler.toml` when using `_worker.js` alongside static assets.
2. **Asset Boundary Protection**: Include `.assetsignore` containing `_worker.js` and `wrangler.toml` to prevent server-side code from being exposed as static files.
3. **FastMCP Transport Security**: Always configure `TransportSecuritySettings(enable_dns_rebinding_protection=False, allowed_hosts=["*"], allowed_origins=["*"])` on FastMCP SSE servers behind Cloudflare.
4. **Origin Header Translation**: Rewrite `Host` header to `<service>.run.app` in `_worker.js` to bypass Google Search Console TXT domain verification roadblocks.
