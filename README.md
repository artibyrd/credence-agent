# Credence Agent Toolkit & Antigravity Plugin (`credence-agent`)

This repository contains the Google Antigravity developer kit, progressive disclosure skills, rules, and invariants for the **Credence Ecosystem**.

---

## Repository Structure

```text
credence-agent/
├── .agents/
│   └── skills/
│       ├── architecture-governance/ # 500 LOC Ceiling Law & compute_* ontology
│       ├── cloudrun-ops/            # Cloud Run compute & cold start tuning
│       ├── epistemic-benchmark/     # Golden 12 benchmark runner skill
│       ├── invariant-audit/         # Living Canon & token budget audit
│       ├── knowledge-governance/    # 4-tier taxonomy & Demotion Highway
│       ├── mesh-cluster/            # 13-node Watts-Strogatz chaos lab skill
│       └── white-label-ops/         # White-label federation scaffolding skill
├── scripts/
│   ├── audit_demotions.py           # Demotion Highway candidate scanner
│   └── lint_skills.py               # Skill schema and token economy linter
├── templates/
│   └── subagents/                   # Declarative subagent delegation profiles
│       ├── docs_sync_agent.json
│       ├── epistemic_auditor.json
│       └── refactor_sentinel.json
├── AGENTS.md                        # Master epistemic invariants and safety rules
├── plugin.json                      # Antigravity plugin definition (v2.2.2)
├── LICENSE                          # Apache-2.0
└── README.md
```

---

## Antigravity Native Discovery

The workspace root at `/home/pendragon/Projects/credence-ecosystem/.agents/skills.json` automatically registers this repository's skills via native declarative discovery:

```json
{
  "entries": [
    {
      "path": "credence-agent/.agents/skills"
    }
  ]
}
```

No manual shell scripts or brittle symlinks are required.

---

## License

Apache License 2.0 &copy; 2026 Credence Network Contributors.
