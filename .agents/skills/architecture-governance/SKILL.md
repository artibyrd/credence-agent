---
name: architecture-governance
description: Enforces the 500 LOC Ceiling Law, compute_* calculation naming ontology, zero-npm web invariant, and modular subpackage decoupling across CLI, Server, TUI, and Mesh.
---

# Architecture Governance & Modularity Skill (`architecture-governance`)

Use this skill when refactoring, modularizing, or auditing Python source files and subpackages across the Credence ecosystem to ensure strict adherence to modularity standards.

---

## 1. Core Modularity Laws

### 1. 500 LOC Ceiling Law
- **Strict Hard Limit**: No individual Python source file (`.py`) in `credence/` may exceed **500 Lines of Code (LOC)**.
- **Decomposition Pattern**: Large modules must be decoupled into cohesive subpackages with focused responsibilities:
  - **CLI**: Decomposed into `commands/`, `formatting/`, and lean root dispatcher `main.py` (<250 LOC).
  - **Server**: Decomposed into `lifespan.py`, `middleware/`, `mcp/`, `api/`, and lean Starlette application assembler `app.py` (<150 LOC).
  - **TUI**: Decomposed into `screens/`, `widgets/`, and lean app controller `app.py` (<250 LOC).
  - **Mesh**: Decomposed into `topology.py`, `badges.py`, `merit.py`, `stats.py`, and `models.py`.
  - **Subjects**: Decomposed into `analytics.py`, `weather.py`, and `models.py`.
  - **Tools / Simulations**: Standalone research, stress testing, and shadow audit scripts belong strictly in `tools/simulations/` rather than production packages.

### 2. `compute_*` Naming Ontology Invariant
- **Standardized Prefix**: All calculation and metric derivation functions must strictly use the `compute_*` prefix.
- **Banned Prefixes**: Functions starting with `calc_*` or `calculate_*` are disallowed across all modules and tests.
- **Examples**:
  - `compute_topic_entropy(...)`
  - `compute_half_life_uptime(...)`
  - `compute_longevity_days(...)`
  - `compute_effective_weight(...)`
  - `compute_subject_expertise(...)`

### 3. Circular Dependency Elimination
- Data structures and Pydantic/dataclass models must reside in dedicated `models.py` modules within each subpackage.
- Inter-module dependencies must flow strictly in a Directed Acyclic Graph (DAG) with zero circular imports.
- Subpackage public APIs must be cleanly exposed via `__all__` lists in `__init__.py` or subpackage entrypoints.

---

### 4. Modular Subpackage Architecture for Servers & Services
Starlette REST and FastMCP 2.0 servers must follow decoupled subpackage layouts:
- `credence/server/api/`: Individual REST route modules (`analytics.py`, `audits.py`, `cost.py`, `domains.py`, `feeds.py`, `mesh.py`, `system.py`).
- `credence/server/mcp/`: FastMCP tool modules (`server.py`, `query_tools.py`, `merit_tools.py`, `mesh_tools.py`, `eval_tools.py`, `consensus_tools.py`, `feed_tools.py`, `cost_tools.py`, `resources.py`, `prompts.py`).
- `credence/server/middleware/`: Security and observability middleware (`security.py`, `rate_limit.py`, `cors.py`, `telemetry.py`).
- `credence/server/lifespan.py`: Autonomous background daemons (Sifter, Boredom Engine) and startup warmup.
- `credence/server/app.py`: Lean route assembly and application factory (<150 LOC).

---

## 2. Shift-Left Contract Verification

Modularity and naming rules are deterministically verified in <0.3s via `tests/governance/test_architecture_governance.py`:
- `test_500_loc_ceiling_invariant`: Scans all Python files to verify `len(lines) <= 500`.
- `test_compute_naming_ontology_invariant`: Parses AST syntax trees across the codebase to ensure zero `calculate_*` or `calc_*` functions exist.
- `test_zero_npm_web_surfaces_invariant`: Verifies zero `package.json` or `node_modules` on web surfaces.

### 4. SQLModel AsyncSession & Query Conventions
- **Import Path**: Strictly import `AsyncSession` from `sqlmodel.ext.asyncio.session` (not raw `sqlalchemy.ext.asyncio`).
- **Execution Method**: Strictly use `await session.exec(stmt)` rather than `session.execute(stmt)` to eliminate runtime deprecation warnings and satisfy mypy typing.
- **Column Sorting**: Use `col(Model.field).desc()` when sorting query results.

### 5. Content Extraction Fallbacks
- When using Trafilatura for plain text or markdown extraction, provide a tag-stripping regex fallback (`re.sub(r"<[^>]+>", " ", ...)`). Short HTML fixtures (<100 chars) are discarded by Trafilatura; the fallback prevents empty content string failures in unit tests.

### 6. Web Component & Localhost State Invariants
1. **Localhost Documentation Link Isolation**: When running web workstations on `localhost` (ports 8000/8080), link normalizers (`normalizeLocalLinks`) must strictly rewrite only sibling web workstation domains (`credence.run`, `credence.report`, `credence.nexus`, `credence.foundation`) to local paths. Authoritative documentation (`docs.credence.run`) and sovereign blog essays (`blog.credence.run`) must preserve their HTTPS URLs with `target="_blank" rel="noopener"` to ensure all modal deep links and invariant references remain operational without requiring background port 8081 daemons.
2. **Direct 1-Click Action & Bidirectional UI Synchronization**: Workstation features (pinning, filtering, auditing) must prioritize direct in-place actions on primary content cards over modal creation dialogs. Any mutation in global state (e.g., removing a pinned item in a sidebar) must trigger centralized synchronization (`syncAllPinStates()`) across all active cards, catalog grids, and inspector headers.
3. **Never call `cloneNode(true)` on host containers**: In browser engines, cloning a tree containing custom elements triggers recursive constructor execution.
4. **Synchronous Attribute Observers**: `attributeChangedCallback` must execute pure synchronous state assignments (`this.state.x = val`) and call `this.render()`, with zero asynchronous event loops.
5. **Defensive Shadow DOM Event Binding**: Null-check all Shadow DOM element lookups (`if (pill) pill.addEventListener(...)`) before attaching listeners.

### 7. Dense Workstation Viewport & Zero-Masking Invariant
1. **Grid Viewport Ceiling**: High-density workstation card grids (Curated Articles, Publisher Catalog, Search Results) must be enclosed within a `.ws-scroll-pane` container with a maximum vertical bound (`max-height: 580px; overflow-y: auto;`) and sleek 6px dark scrollbars to prevent full datasets (16+ items) from expanding the page 2,000px+ vertically.
2. **Sticky Table Headers**: All dense data tables (`.ws-table-container`) must enforce `max-height: 520px; overflow-y: auto;` with sticky header positioning (`thead th { position: sticky; top: 0; background: #111b2e; z-index: 2; }`) so column headers remain visible during deep scrolling.
3. **Root Asset Isolation**: Never place a fallback `index.html` at the root of `web/` in multi-domain edge deployments, as Cloudflare Workers Static Assets default fallback can mask domain subfolder index files.


### 6. Proactive Subsystem Modularization & Serialization Invariants
- **Day-1 Modular Subpackages**: Any new subsystem anticipated to exceed 300 LOC (such as storage backends, consensus engines, or parsers) must be created directly as a package directory with discrete modules (`engine.py`, `manifest.py`, `transports.py`, `__init__.py`) rather than a monolithic file to strictly uphold the 500 LOC Ceiling Law.
- **Nested Dataclass/Pydantic Serialization**: When returning `@dataclass` structures containing nested Pydantic `BaseModel` objects from REST API handlers or FastMCP tools, always recursively serialize nested instances (`[b.model_dump() if hasattr(b, 'model_dump') else b for b in dataclass.field]`) to prevent `TypeError: Object of type X is not JSON serializable` in `json.dumps()` / `JSONResponse`.
