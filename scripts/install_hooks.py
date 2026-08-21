#!/usr/bin/env python3
"""Installs conventional commit-msg hook across all ecosystem repositories."""

from pathlib import Path
import os
import stat

HOOK_SCRIPT = r"""#!/usr/bin/env bash
MSG_FILE="$1"
MSG=$(cat "$MSG_FILE")
python3 -c '
import re, sys
msg = sys.argv[1].strip()
if msg.startswith("Merge branch") or msg.startswith("Revert") or msg.startswith("Release") or msg.startswith("chore(ops): synchronize"):
    sys.exit(0)
pat = r"^(\[v[0-9]+\.[0-9]+\.[0-9]+\] )?(feat|fix|docs|refactor|test|ci|chore|perf)(\((governance|forensics|mesh|crypto|ui|ops)\))?!?: .+$"
if not re.match(pat, msg):
    print("\033[1;31m❌ Commit Rejected: Message violates conventional format.\033[0m")
    print("   Message : " + repr(msg))
    print("   Allowed : <type>(<scope>): <summary> OR <type>: <summary>")
    print("   Types   : feat, fix, docs, refactor, test, ci, chore, perf")
    print("   Scopes  : (governance), (forensics), (mesh), (crypto), (ui), (ops)")
    sys.exit(1)
' "$MSG"
"""

ECOSYSTEM_DIR = Path(__file__).resolve().parent.parent.parent
REPOS = [
    ECOSYSTEM_DIR / "credence",
    ECOSYSTEM_DIR / "credence-docs",
    ECOSYSTEM_DIR / "credence-agent",
]

def main() -> None:
    for repo in REPOS:
        hooks_dir = repo / ".git" / "hooks"
        if not hooks_dir.exists():
            continue
        hook_path = hooks_dir / "commit-msg"
        hook_path.write_text(HOOK_SCRIPT.strip() + "\n", encoding="utf-8")
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"✅ Installed commit-msg hook in {repo.name}")

if __name__ == "__main__":
    main()
