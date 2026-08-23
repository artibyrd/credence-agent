---
name: architecture-governance
description: Enforces the 500 LOC Ceiling Law across Python and Justfiles, compute_* calculation naming ontology, zero-npm web invariant, modular subpackage decoupling, and shift-left intelligent guidance banners.
---

# Architecture Governance & Modularity Skill (`architecture-governance`)

Use this skill when refactoring, modularizing, or auditing source files, Justfiles, and subpackages across the Credence ecosystem to ensure strict adherence to modularity standards.

---

## 1. Core Modularity Laws

### 1. 500 LOC Ceiling Law across Code & Toolchains
- **Strict Hard Limit**: No individual source file (`.py`, `.js`, or `.just`) may exceed **500 Lines of Code (LOC)**.
- **Decomposition Pattern**: Large modules must be decoupled into cohesive subpackages with focused responsibilities:
  - **CLI**: Decomposed into `commands/`, `formatting/`, and lean root dispatcher `main.py` (<250 LOC).
  - **Server**: Decomposed into `lifespan.py`, `middleware/`, `mcp/`, `api/`, and lean Starlette application assembler `app.py` (<150 LOC).
  - **TUI**: Decomposed into `screens/`, `widgets/`, and lean app controller `app.py` (<250 LOC).
  - **Mesh**: Decomposed into `topology.py`, `badges.py`, `merit.py`, `stats.py`, and `models.py`.
  - **Subjects**: Decomposed into `analytics.py`, `weather.py`, and `models.py`.
  - **Justfile Toolchains**: Decomposed into a lean root `Justfile` (<80 LOC) importing focused subfiles under `just/` (`preflight.just`, `quality.just`, `engine.just`, `deploy.just`, `release.just`).

### 2. `compute_*` Naming Ontology Invariant
- **Standardized Prefix**: All calculation and metric derivation functions must strictly use the `compute_*` prefix.
- **Banned Prefixes**: Functions starting with `calc_*` or `calculate_*` are disallowed across all modules and tests.
- **Examples**: `compute_topic_entropy`, `compute_half_life_uptime`, `compute_longevity_days`, `compute_effective_weight`, `compute_subject_expertise`.

### 3. Circular Dependency Elimination
- Data structures and Pydantic/dataclass models must reside in dedicated `models.py` modules within each subpackage.
- Inter-module dependencies must flow strictly in a Directed Acyclic Graph (DAG) with zero circular imports.
- Subpackage public APIs must be cleanly exposed via `__all__` lists in `__init__.py` or subpackage entrypoints.

---

## 2. Shift-Left Intelligent Guidance & Workflow Chaining

### 1. Point-of-Action Guidance Banners
- **Context Economy**: Rather than overloading root prompt memory with procedural checklists, embed colorized terminal banners in `Justfile` recipes and helper scripts (`manage_pr.py`, `sync_version.py`).
- **Active Beacon Parsing**: Agents executing toolchain commands must actively parse and follow directional beacons printed by `Justfile` recipes.

### 2. Workflow State Chaining
- Toolchain commands must be chained so each successful step points directly to the next phase:
  - `just check` $\to$ Prompts to run `just pr create '<title>'`
  - `just pr create` $\to$ Prompts to watch `deploy-dev.yml` and probe live Dev links
  - Mk1 Eyeball Review $\to$ Prompts to run `just pr merge`
  - `just pr merge` $\to$ Prompts to switch to `main`, pull, and sync version
  - `just sync-version` $\to$ Verifies `docs/changelog.md` contains release header
  - `just release` $\to$ Prompts to watch production deployment and run `/learn`

### 3. Conventional PR Title & Scope Taxonomy
- **Strict Scope Taxonomy**: The CI gate strictly enforces conventional PR scopes. Scopes MUST strictly be one of:
  - `(governance)`: Invariant audits, skill updates, knowledge governance, policies.
  - `(forensics)`: Evidence extraction, DOM hashing, scrubber heuristics, parser guards.
  - `(mesh)`: P2P gossip, Watts-Strogatz clustering, consensus aggregation, Sybil defense.
  - `(crypto)`: Ed25519 signatures, RFC 8785 canonical JSON, node identity envelopes.
  - `(ui)`: Web workstations, CSS styling, components, TUI, CLI formatting.
  - `(ops)`: CI/CD workflows, Terraform, Cloud Run deployments, Dockerfiles, Justfiles.
- **PR Title Format**: `[vX.Y.Z] <type>(<scope>): <imperative summary>` (e.g. `[v2.10.0] feat(governance): add weighted median consensus`).

---

## 3. Epistemic Anti-Spoofing & Grounded Embed Governance

### 1. Zero Synthetic Dummy Fallbacks
- Client web components (`<credence-badge>`) and widgets must never render mock Ed25519 public keys (`ed25519:e3b0c44...41a7`), synthetic trajectory sparklines (`+2.4 pts (Improving)`), or fake digest placeholders.
- If telemetry is uninitialized, explicitly render `None Provided (Standalone)` or `Criteria Pending`.

### 2. Fail-Closed Unearned Milestones
- Any embed endpoint (e.g. `/api/badge/{id}`) or UI generator must strictly query canonical node merit (`get_local_node_merit()`).
- Unearned milestones must return **`UNEARNED`** in muted slate (`#475569` to `#334155`), and UI generator embed copy buttons must lock to prevent distribution of forged credentials.

### 3. Live In-Browser WebCrypto Anti-Tamper Hashing
- Never claim cryptographic tamper protection in comments without executing `window.crypto.subtle.digest('SHA-256')`.
- Web components must dynamically compute live DOM text hashes (`computeLiveDomHash`) to detect post-audit page tampering (`MODIFIED_POST_AUDIT`).

---

## 4. UI/UX Deck Architecture & Modality Grids

### 1. Balanced Modality Card Grids
- For major functional modalities (e.g. Node Epistemic Merit, Publisher DCI, Article Attestation), use prominent, self-describing interactive cards (`.studio-modality-grid`) with icons, bold titles, and explanatory subtitles rather than cramped inline button strips.

### 2. Balanced 50/50 Responsive Deck Layouts
- Workstation configurations and live stage previews must share equal visual weight using responsive grids (`repeat(auto-fit, minmax(360px, 1fr))`), avoiding asymmetric columns that compress configuration controls.

### 3. Minimalist Render Styles
- Avoid proliferating speculative or fragile badge styles. Keep only clean, battle-tested styles (e.g. Interactive Web Component and High-Contrast Shield).

### 4. Dense Workstation Viewport & Zero-Masking Invariant
- High-density card grids must be enclosed within `.ws-scroll-pane` (`max-height: 580px; overflow-y: auto;`).
- Table headers must remain sticky during deep scrolling (`thead th { position: sticky; top: 0; }`).

---

## 5. Fail-Closed UI Architecture & Zero-Mock Telemetry Invariant

### 1. Absolute Prohibition of Synthetic Mock Fallbacks
- **Zero Mock Data in Live Workstations**: Client scripts in `web/` must NEVER import, define, or fall back to synthetic mock datasets (`MOCK_NODES`, `MOCK_REPORTS`, `mock_claims`).
- **Simulations Isolated to Docs Playground**: Simulators and chaos models belong exclusively in documentation playground sandboxes (`credence-docs/playground`) or offline research tools (`tools/simulations/`), never in operator workstation bundles (`web/`).

### 2. Mandatory Fail-Closed Empty State Cards
- When an API endpoint fails, returns an empty array, or is offline:
  1. Set state explicitly to `STANDALONE`, `NO DATA`, or `CRITERIA PENDING`.
  2. Render an explicit high-contrast Empty State Card (`.ws-empty-card`) with an explanatory icon (`📡`), title, and remediation instructions.
  3. Never mask the empty state with synthetic "sample" data.

### 3. Zero Mock Tokens & Synthetic Digests
- Prohibited in all web surfaces:
  - Hardcoded Ed25519 keys (e.g. `ed25519:e3b0c44...41a7`).
  - Hardcoded sparkline trajectories (e.g. `+2.4 pts (Improving)`).
  - Dummy scores or synthetic consensus badges.

---

## 6. Scoped Workstation CSS & Viewport Isolation

To prevent compact workstation layout locks from freezing natural document scrolling on landing pages (`credence.run`), blogs (`blog.credence.run`), and documentation (`docs.credence.run`):

1. **Mandatory `:has()` Container Scoping**:
   - `height: 100vh; overflow: hidden;` must NEVER be applied unconditionally to global `html, body`.
   - Always scope desktop workstation layout to container presence:

```css
@media (min-width: 921px) {
  html:has(.workstation-container),
  body:has(.workstation-container) {
    height: 100vh;
    overflow: hidden;
  }
  body:has(.workstation-container) {
    display: flex;
    flex-direction: column;
  }
}
```

2. **Landing & Documentation Page Freedom**:
   - All document, marketing, and reading surfaces must retain unconstrained natural scrolling (`overflow: auto`, natural document height).


