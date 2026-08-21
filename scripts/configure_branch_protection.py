#!/usr/bin/env python3
"""
Configures branch protection for main across credence, credence-docs, and credence-agent.
Requires:
1. Pull request review approval before merging (required_approving_review_count = 1).
2. Dismiss stale approvals when new commits are pushed.
3. Require status checks to pass before merging.
4. Block force pushes and deletions.
"""

import json
import subprocess
import sys

REPO_CHECKS = {
    "artibyrd/credence": [
        "CI / Lint & Type Check (pull_request)",
        "CI / Hermetic Unit & Gauntlet Suite",
        "CI / Terraform Validation (pull_request)",
        "CI / Validate PR & Branch Naming Conventions",
    ],
    "artibyrd/credence-docs": [
        "Zero-Build Deploy",
    ],
    "artibyrd/credence-agent": [
        "CI / Validate PR & Branch Naming Conventions",
        "CI / Declarative Skill & Governance Linter",
    ],
}

def set_branch_protection(repo: str) -> bool:
    print(f"🔒 Configuring branch protection on {repo}:main ...")
    payload = {
        "required_status_checks": {
            "strict": True,
            "contexts": REPO_CHECKS.get(repo, []),
        },
        "enforce_admins": False,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1,
            "require_last_push_approval": False,
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }
    payload_json = json.dumps(payload)
    cmd = [
        "gh", "api",
        "-X", "PUT",
        f"repos/{repo}/branches/main/protection",
        "--input", "-",
    ]
    res = subprocess.run(cmd, input=payload_json, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Failed to set protection on {repo}: {res.stderr.strip()}")
        return False
    print(f"✅ Branch protection active on {repo}:main (Code Owner approval + CI checks).")
    return True

def main():
    success = True
    for repo in REPO_CHECKS:
        if not set_branch_protection(repo):
            success = False
    if not success:
        sys.exit(1)
    print("\n🎉 All 3 ecosystem repositories now enforce PR approval gating on main!")

if __name__ == "__main__":
    main()
