---
name: invariant-audit
description: Audit Credence-specific ecosystem contracts including 7-manifest version parity, Ed25519 attestations, The Invariant Bible dynamic naming, Tier 2 shift-left gates, and autonomous RFC standards governance.
---

# Credence Invariant Audit Skill (`invariant-audit`)

Use this skill when auditing Credence-specific release, documentation, telemetry, and standards-governance contracts across `credence`, `credence-docs`, and `credence-agent`.

> General context-economy governance (4-tier taxonomy, `<800`-token `AGENTS.md`, Demotion Highway, `/learn` Admission Gate) is handled by `knowledge-governance` + `.agents/overrides/knowledge-governance.md`.

---

## 1. Credence-Specific Audit Surfaces

### 1. 7-Manifest Semantic Version Parity & Ed25519 Attestations
Verify simultaneous synchronization across all 7 version manifests (`just sync-version <X.Y.Z>`):
1. `credence/pyproject.toml`
2. `credence/credence/__init__.py`
3. `credence-docs/app.js`
4. `credence/web/assets/credence-workstation.js`
5. `credence-agent/plugin.json`
6. Multi-domain HTML badges across all 5 web workstations (`web/` + `credence-docs/`)
7. Open Graph social card assets (`og-card.svg` and `og-card.png`)

`just sync-version <version>` invokes `poetry run credence audit-docs --update`, deriving `__version__` dynamically from package metadata and minting Ed25519 cryptographic signatures in `credence-docs/assets/attestations.json`.

### 2. Dynamic Invariant Canon Naming ("The Invariant Bible")
- Scan public web surfaces (`web/`), documentation (`credence-docs/docs/`), sitemaps, and navigation footers.
- Assert zero hardcoded invariant counts (e.g., `"36 Core"`, `"38 Invariants"`).
- Enforce dynamic references to **The Invariant Bible** or **Living Canon of System Invariants**.

### 3. Tier 2 Shift-Left Automated Integrity Gates (`credence/tests/governance/`)
- **Gate 1 (`test_docs_attestation_and_manifest_version_parity`)**: 7-manifest version synchronization and Ed25519 signature validity.
- **Gate 2 (`test_all_registered_playgrounds_have_active_dom_mounts`)**: Every registered playground has an active DOM mount handler.
- **Gate 3 (`test_docs_cli_commands_and_flags_validity`)**: Documented CLI subcommands match `credence/cli/`.
- **Gate 4 (`test_docs_justfile_recipes_exist`)**: Documented `just` invocations exist in `Justfile` / `just/*.just`.
- **Gate 5 (`test_zero_hardcoded_invariant_counts_in_docs`)**: Prohibits hardcoded invariant counts.
- **Gates 6–7 (`test_docs_minimum_meaningful_length`, `test_zero_empty_or_sparse_sections`)**: Archetype word-count floors and non-empty sections.
- **Gate 8 (`test_zero_pseudo_box_art_and_dashed_boundaries_invariant`)**: Zero dashed borders, loose-pipe pseudo-boxes, or bare ASCII arrows in docs.
- **Gate 9 (`test_roadmap_pure_forward_looking_and_horizon_integrity`)**: Pure forward-looking roadmap with no completed features lingering in horizon queues.
- **Gates 13–15**: Narrative plot fidelity, linked invariants (`[`inv-...`](/docs/invariants#inv-...)`), zero `file:///` URIs, and resolving links/anchors.
- **Vector SVG & Overlay Parity**: Dark-theme SVG tokens (`#090d16`, `#050810`), descriptive figcaptions, SHA-256 parity between `credence-docs/assets/illustrations/` and `credence/web/assets/illustrations/`, and SHA-256 parity between `credence-agent/overrides/` and `credence/.agents/overrides/`.
- **Platform Hygiene Gates**: Zero tracked vendor IDE dotfolders (`.gemini/`, `.vscode/`, `.cursor/`, `.idea/`), `.gemini/` ignored in every repo `.gitignore`, zero machine-local paths (`/home/<user>/`, `/Users/<user>/`), and 1,000-LOC anti-god-file safety rail.

### 4. Autonomous RFC Standards Governance & Golden Control Corpus
- **3-Tier Hierarchy**: Standards belong strictly to Tier 0 (`UNIVERSAL_GENERAL`), Tier 1 (`DOMAIN_SPECIALIST`), or Tier 2 (`SOVEREIGN_NICHE`).
- **6-Stage Promotion State Machine**: `Draft -> Proposed -> Candidate -> Shadow Trial -> Voting -> Ratified`.
- **Golden Control Corpus ($N = 100$)**: Every candidate catalog must pass the synthetic gauntlet and immutable Golden Control Corpus asserting:
  $$\mathcal{F}_1 \ge 0.87, \quad \text{Precision} \ge 0.90, \quad \text{Recall} \ge 0.85, \quad \text{FPR}_{\text{golden}} = 0.00\%, \quad G = 1.00$$
- **CAS Pinning**: Ratified standards are pinned via RFC 8785 canonical JSON bytes and SHA-256 CAS hashes with dynamic hot-reload into `TaxonomyRegistry`.

### 5. Zero-Mock Telemetry Boundary (`inv-production-telemetry-boundary`)
Enforced by `tests/governance/test_production_telemetry_boundary.py`:
1. **Zero Synthetic Generators**: No synthetic audit generators or `Math.random` loops in live web workstations.
2. **Authentic WebCrypto**: Real `SubtleCrypto.digest` and `verifyEd25519Signature` over RFC 8785 canonical bytes (no `setTimeout` fake spinners).
3. **No Error Masking**: Workstation `catch` blocks surface authentic errors rather than fake "saved locally" states.
4. **Authentic Standalone State**: Unpeered nodes report `STANDALONE (UNPEERED)` ($N=1, f=0$) and $0.0\%$ worksharing efficiency.

### 6. Hermetic Pipeline Test & Markdown Parser Boundaries
- **Offline Heuristic Spectrum**: CI runs offline without cloud LLM keys (`evaluation_method: "offline_structural_heuristic"`). Unit tests evaluating profile overrides assert across the hermetic spectrum (`("LOW_SUSPICION", "SUSPICIOUS", "DECEPTIVE")`) and never mock LLM responses unless explicitly tagged `@pytest.mark.mock`.
- **Node.js Markdown AST Gate**: `test_javascript_markdown_parser_runtime_integrity` executes `parseMarkdown()` via Node.js across all docs, asserting zero raw `>` / `<p>&gt;` leaks and intact `.alert-box` wrappers.

---

## 2. Turnkey Audit Commands

```bash
# Full parallel pre-commit QA gate (lint, unit, docs, terraform, agent-check)
just check

# Targeted governance & skill/overlay audits
just agent-check
just audit-demotions
just challenge-invariant inv-verbatim-grounding
poetry run pytest tests/governance/ -v
```
