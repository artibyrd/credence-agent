# Credence Agent Toolkit & Antigravity Plugin (`credence-agent`)

This repository contains the Google Antigravity developer kit, progressive disclosure skills, rules, and invariants for the **Credence Ecosystem**.

---

## Repository Structure

```text
credence-agent/
├── .agents/
│   └── skills/
│       ├── epistemic-benchmark/     # Golden 12 benchmark runner skill
│       ├── mesh-cluster/            # 13-node Watts-Strogatz chaos lab skill
│       └── white-label-ops/         # White-label federation scaffolding skill
├── AGENTS.md                        # Master epistemic invariants and safety rules
├── plugin.json                      # Antigravity plugin definition (v1.0.0)
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
