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

## 2. Shift-Left Contract Verification

Modularity and naming rules are deterministically verified in <0.3s via `tests/governance/test_architecture_governance.py`:
- `test_500_loc_ceiling_invariant`: Scans all Python files to verify `len(lines) <= 500`.
- `test_compute_naming_ontology_invariant`: Parses AST syntax trees across the codebase to ensure zero `calculate_*` or `calc_*` functions exist.
- `test_zero_npm_web_surfaces_invariant`: Verifies zero `package.json` or `node_modules` on web surfaces.
