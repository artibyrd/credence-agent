---
name: epistemic-benchmark
description: Run the Golden 12 evaluation benchmark, verify Gemini 4 and 3.8 thinkingLevel calibration across FREE, ECONOMY, BALANCED, and ULTRA profiles, and audit model lifecycle freshness with just check-models.
---

# Epistemic Benchmark & Model Calibration Skill

Use this skill when evaluating epistemic calibration, benchmarking active LLM profiles, verifying `thinkingLevel` vs. `thinkingBudget` behavior, or checking model lifecycle freshness and sunset dates.

---

## 1. Core Commands

```bash
# Audit active COST_PROFILES, sunset dates, pricing parity, and harness alignment (offline)
just check-models
poetry run credence models check

# Query live Gemini API model catalog to surface newly released or retiring models
poetry run credence models check --live

# Run Golden 12 benchmark suite and profile inspection
just benchmark
just config-verify
credence profile list

# Execute cross-model Pareto benchmark across active Gemini 3.8 & Gemini 4 models
poetry run python -m credence.pipeline.cross_model_benchmark

# Run bicameral shadow audits & federation bridge experiments
just experiment shadow-audit
just experiment federation-bridge

# Run hermetic unit & integration benchmark tests
poetry run pytest tests/unit/pipeline/test_model_registry.py tests/unit/pipeline/test_adapters.py tests/unit/pipeline/test_cost_profiles.py -v
```

---

## 2. Active Antigravity-Aligned Cost Profiles (Gemini 3.8 & Gemini 4)

All 4 active `COST_PROFILES` align with Google's active Antigravity-signaled model catalog and use `thinkingConfig.thinkingLevel` (`minimal` | `low` | `medium` | `high`), never combining `thinkingLevel` and `thinkingBudget` in the same request (which returns `400 Bad Request` on Gemini 4):

| Profile | Primary Model | Escalation Model | Triage Model | Thinking Level | Intended Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`FREE`** | `gemini-3.8-flash` | `gemini-3.8-flash` | `gemini-3.8-flash` | `minimal` | Zero-spend / offline heuristic fallback & smoke runs |
| **`ECONOMY`** | `gemini-3.8-flash` | `gemini-3.8-flash` | `gemini-3.8-flash` | `low` (`minimal` triage) | High-throughput dev & sentinel screening |
| **`BALANCED`** | `gemini-3.8-flash` | `gemini-4-neon` | `gemini-3.8-flash` | `medium` (`minimal` triage) | Pareto-optimal production default |
| **`ULTRA`** | `gemini-4-neon` | `gemini-4-carbon` | `gemini-4-hydrogen` | `high` (`low` triage) | Deep forensic / long-form & escalation audits |

### Reasoning Configuration Contract (`compute_thinking_config`)
- **Gemini 4 & Gemini 3.8 (`thinking_mode = "level"`)**: Always emit `thinkingConfig: {"thinkingLevel": "..."}` and never send `thinkingBudget`. Legacy integer budgets map deterministically (`0 -> "minimal"`, `<=1024 -> "low"`, `<=4096 -> "medium"`, `>4096 -> "high"`).
- **Legacy Replay Models (`thinking_mode = "budget"`)**: Deprecated/retired models (`gemini-2.5-flash-lite`, `gemini-3.7-flash`, `gemini-2.0-flash-lite`, `gemini-1.5-pro`) remain in `credence/pipeline/model_registry.py` strictly for historical replay or explicit Vertex Model Garden overrides; active `COST_PROFILES` must never reference them.
- **Surface Alignment Note (Harness vs. API)**: Every active model in `COST_PROFILES` declares `"antigravity-harness"` in `model_registry.py`'s `supported_surfaces` so Antigravity's model catalog serves as an active freshness signal. Other valid API/Vertex models (`gemini-3.5-flash-lite`, `gemini-4-argon`, Anthropic, OpenAI, Ollama) remain supported via explicit CLI/env overrides.

---

## 3. Bicameral Experimentation & Controlled Independent Variables

When running cross-environment benchmarks or shadow audits, enforce the controlled variable matrix:
- **Dev Tier**: `ECONOMY` / `FREE` profile (`minimal`/`low` thinking), SQLite storage, ephemeral keypair.
- **Prod Tier**: `BALANCED` / `ULTRA` profile (`medium`/`high` thinking), PostgreSQL/S3, sovereign root Ed25519 key.
- **Pre-Flight Gate**: Run `just config-verify` and `just check-models` before recording official benchmark measurements to confirm zero key collision, verified profile separation, and zero retiring models.

---

## 4. Golden 12 Calibration & Historical Baseline Reference

- **Golden 12 Scenarios**: 3 ground-truth news, 3 logical fallacy op-eds, 3 deceptive pattern checkouts, 3 satire/parody articles.
- **Required Calibration Floors**: 100% verbatim citation grounding ($G = 1.00$), Poe's Law satire neutralization ($0.00$ suspicion score), and cascaded Dev-to-Prod triage filtering to preserve FinOps headroom.
- **Historical Baseline (Pre-Gemini 4 Archive)**: Earlier v2.x Pareto benchmarks established `gemini-3.7-flash` at 4,096 thinking tokens ($0.34–$0.68 / 1k audits, 2.4s–5.1s latency, 83.3% cascaded cost reduction vs. flagship Pro). Treat Gemini 3.7 Flash figures strictly as historical reference baselines; all new benchmark runs target the active Gemini 3.8 / Gemini 4 lineup above.
