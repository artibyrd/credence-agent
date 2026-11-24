# Credence Agent Toolkit & Skill Overlay Plugin (`credence-agent`)

Domain-specific agent skills, self-contained project overlays, and shift-left governance tooling for the **Credence Ecosystem**.

> **Optimized for Antigravity, compatible with other harnesses:** `credence-agent` ships as a native Antigravity plugin (`plugin.json`, `skills/`, `rules/AGENTS.md`) and pairs seamlessly with the optional standalone workflow suite [`artibyrd/antigravity-customizations`](https://github.com/artibyrd/antigravity-customizations). Every skill uses the open Agent Skills `SKILL.md` standard and every overlay under `overrides/` is written as complete, self-contained Markdown policy—100% actionable on Claude Code, Cursor, Codex, OpenHands, or Antigravity without external plugin dependencies.

---

## Repository Structure

```text
credence-agent/
├── plugin.json                      # Antigravity native plugin manifest
├── rules/
│   └── AGENTS.md                    # Master Credence Tier 0 invariants (<800 tokens)
├── skills/                          # 6 Credence domain skills (open Agent Skills format)
│   ├── cloudrun-ops/                # Cloud Run compute, WIF & scale-to-zero ops
│   ├── epistemic-benchmark/         # Golden 12 benchmarks, Gemini 4/3.8 & check-models
│   ├── forensic-audit/              # Cluster swarms, DOM grounding (G=1.00) & DCI
│   ├── invariant-audit/             # 7-manifest parity, attestations & RFC standards
│   ├── mesh-cluster/                # 13-node Watts-Strogatz mesh & Byzantine Sybil ops
│   └── white-label-ops/             # Sovereign org init-org & multi-cloud Terraform
├── overrides/                       # 6 self-contained Credence project overlays
│   ├── architecture-review.md       # Deep Modules, compute_*, Epistemic Lensing, SVG tokens
│   ├── bootstrap-approvals.md       # Safe core vs. hosted Justfile command scopes
│   ├── domain-modeling.md           # Lexicon pointer & canonical domain primitives
│   ├── knowledge-governance.md      # Demotion tooling, 5-level docs & frontmatter provenance
│   ├── pr-brief.md                  # [vX.Y.Z] PR titles, 6 strict scopes & triad links
│   └── release-lifecycle.md         # 7-manifest sync-version, Dev probe & 3-repo merge order
├── scripts/
│   ├── audit_demotions.py           # Demotion Highway candidate & token budget scanner
│   ├── challenge_invariant.py       # Forensic invariant disposition challenger
│   ├── install_hooks.py             # Conventional commit-msg hook installer
│   ├── lint_skills.py               # Skills, overrides, plugin.json & local-path linter
│   └── manage_pr.py                 # Staged triad PR lifecycle helper
├── templates/
│   └── subagents/                   # Declarative subagent delegation profiles
├── LICENSE                          # Apache-2.0
└── README.md
```

---

## Discovery & Skill Overlay Architecture

1. **Workspace Plugin & Skill Discovery:** The umbrella workspace registers `credence-agent` via `.agents/plugins.json` and `.agents/skills.json`:

```json
{
  "entries": [
    {
      "path": "credence-agent/skills"
    }
  ]
}
```

2. **Project Overlays (`.agents/overrides/<skill>.md`):**
   - Umbrella workspace symlinks `.agents/overrides -> ../credence-agent/overrides`.
   - Standalone `artibyrd/credence` clones carry a synchronized `credence/.agents/overrides/` copy maintained via `just sync-overlays` and verified by `test_standalone_skill_overlays_parity`.
   - Generalized workflows from [`artibyrd/antigravity-customizations`](https://github.com/artibyrd/antigravity-customizations) automatically load `.agents/overrides/<skill>.md` before execution; other harnesses read the same files directly as Credence's on-demand subsystem guides.

3. **Validation:**

```bash
# Harness-agnostic schema, frontmatter, overlay & local-path check
python3 scripts/lint_skills.py

# Strict Antigravity plugin validation (when agy CLI is installed)
agy plugin validate --strict .
```

See the full architecture guide at [`docs/agentic/08-antigravity-customizations-and-skill-overlays.md`](https://docs.credence.run/agentic/08-antigravity-customizations-and-skill-overlays).

---

## License

Apache License 2.0 &copy; 2026 Credence Network Contributors.
