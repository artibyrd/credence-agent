#!/usr/bin/env bash
# credence-agent/setup.sh
# Verifies Antigravity workspace health, skills, rules, and invariants configuration.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Credence Antigravity Workspace Verification ==="
echo "Workspace root: $WORKSPACE_ROOT"

# Verify .agents directory structure
if [ -d "$SCRIPT_DIR/.agents/skills" ]; then
    echo "✅ Native .agents/skills structure verified in credence-agent."
else
    echo "❌ Missing .agents/skills in credence-agent."
    exit 1
fi

# Verify root AGENTS.md
if [ -f "$WORKSPACE_ROOT/AGENTS.md" ]; then
    echo "✅ Universal workspace AGENTS.md present."
else
    echo "❌ Missing workspace AGENTS.md."
    exit 1
fi

# Verify sub-repository AGENTS.md files
REPOS=(
    "credence"
    "credence-docs"
    "credence-agent"
)
for repo in "${REPOS[@]}"; do
    if [ -f "$WORKSPACE_ROOT/$repo/AGENTS.md" ]; then
        echo "✅ $repo/AGENTS.md verified."
    else
        echo "⚠️ $repo/AGENTS.md not found."
    fi
done

echo ""
echo "=== All Credence Antigravity Workspace Checks Passed ==="
