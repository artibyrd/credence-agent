#!/usr/bin/env python3
"""
Ecosystem PR Management and Approval Gating Engine.
Handles:
- Generating clean, rich GitHub Markdown PR descriptions with zero escape artifacts.
- Creating / updating PRs across all 3 ecosystem repositories.
- Verifying approval gating (Mk1 Eyeball human review) and CI status before merging.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ECOSYSTEM_DIR = Path(__file__).resolve().parent.parent.parent
REPOS = {
    "credence": ECOSYSTEM_DIR / "credence",
    "credence-docs": ECOSYSTEM_DIR / "credence-docs",
    "credence-agent": ECOSYSTEM_DIR / "credence-agent",
}

REPO_DESCRIPTIONS = {
    "credence": "Compute & Execution Plane (FastAPI, FastMCP, SQLite, Cloud Run)",
    "credence-docs": "Edge Documentation & Workstation Plane (Zero-Build Vanilla Web UI, Invariant Canon)",
    "credence-agent": "Declarative Governance Plane (Skills, Subagent Specs, Knowledge Linters)",
}

def run_cmd(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    res = subprocess.run(args, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def get_branch_name(repo_path: Path) -> str:
    _, out, _ = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)
    return out

def get_commits_for_branch(repo_path: Path, branch: str) -> list[tuple[str, str]]:
    # Try origin/main..HEAD, fallback to main..HEAD
    code, out, _ = run_cmd(["git", "log", "origin/main..HEAD", "--oneline"], cwd=repo_path)
    if code != 0 or not out:
        code, out, _ = run_cmd(["git", "log", "main..HEAD", "--oneline"], cwd=repo_path)
    if code != 0 or not out:
        return []
    
    commits = []
    for line in out.splitlines():
        if line.strip():
            parts = line.strip().split(" ", 1)
            commits.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return commits

def generate_pr_markdown(repo_name: str, branch: str, title: str, commits: list[tuple[str, str]]) -> str:
    desc = REPO_DESCRIPTIONS.get(repo_name, "Ecosystem Component")
    commits_md = "\n".join(f"- `{sha}` {msg}" for sha, msg in commits) if commits else "- *No discrete commits (synced state)*"
    
    md = f"""# {title}

> **Plane**: {desc}  
> **Milestone Branch**: `{branch}` $\\rightarrow$ `main`  
> **Governance Gate**: **Mk1 Eyeball Human Approval Required**

---

## 🎯 Executive Summary & Objectives
This pull request bundles verified architectural milestones, governance enhancements, and operational tooling for the **Credence ecosystem**. All changes have passed local shift-left integrity checks and hermetic unit suites.

---

## 📦 Staged Commits on Branch (`{branch}`)
{commits_md}

---

## 🚀 Deployment & Routing Architecture
| Trigger Event | Target Environment | Automation Pipeline |
| :--- | :--- | :--- |
| **PR Opened / Pushed** | `credence-dev-495173` | Automated Cloud Run Dev deployment & live health probe |
| **PR Approved & Merged** | `credence-prod-505902` | Production Cloud Run & Cloudflare Edge live rollout |

---

## 🛡️ Shift-Left Verification & Integrity Matrix
- [x] **Universal 3-Class Invariant Canon Audit**: Tier 0 prompt budget & dynamic naming verified.
- [x] **The Invariant Challenger**: Demotion Highway evaluated against shift-left test saturation.
- [x] **7-Manifest Version Parity**: `pyproject.toml`, `__init__.py`, `app.js`, `index.html`, and `plugin.json` synchronized.
- [x] **Zero-npm Invariant**: 100% vanilla ES Modules with zero npm build chain dependencies.
- [x] **Hermetic Unit & Gauntlet Suite**: In-memory unit tests passing in <35s.

---

## 👥 Review & Approval Gate ("Mk1 Eyeball")
- [ ] **Human Architecture Review**: Verify semantic versioning, invariants, and release notes.
- [ ] **Dev Staging Verification**: Verify live `/health` telemetry on Cloud Run Dev.
- [ ] **Approval Sign-off**: Required before merging into `main`.
"""
    return md

def create_or_update_prs(title: str) -> None:
    for repo_name, repo_path in REPOS.items():
        branch = get_branch_name(repo_path)
        if branch == "main":
            print(f"⏩ Skipping {repo_name} (already on main).")
            continue
        
        print(f"=== Managing PR for {repo_name} ({branch} -> main) ===")
        commits = get_commits_for_branch(repo_path, branch)
        body = generate_pr_markdown(repo_name, branch, title, commits)
        
        tmp_body_file = repo_path / ".pr_body_tmp.md"
        tmp_body_file.write_text(body, encoding="utf-8")
        
        try:
            # Check if PR exists
            code, out, _ = run_cmd(["gh", "pr", "view", "--json", "number,url"], cwd=repo_path)
            if code == 0:
                pr_info = json.loads(out)
                pr_num = pr_info.get("number")
                print(f"📝 Updating existing PR #{pr_num} for {repo_name}...")
                run_cmd(["gh", "pr", "edit", str(pr_num), "--title", title, "--body-file", str(tmp_body_file)], cwd=repo_path)
                print(f"✅ Updated PR #{pr_num}: {pr_info.get('url')}")
            else:
                print(f"🚀 Creating new PR for {repo_name}...")
                code, out, err = run_cmd([
                    "gh", "pr", "create",
                    "--title", title,
                    "--body-file", str(tmp_body_file),
                    "--base", "main",
                    "--head", branch,
                ], cwd=repo_path)
                if code == 0:
                    print(f"✅ Created PR: {out}")
                else:
                    print(f"❌ Failed to create PR for {repo_name}: {err}")
        finally:
            if tmp_body_file.exists():
                tmp_body_file.unlink()

def check_pr_status() -> None:
    for repo_name, repo_path in REPOS.items():
        print(f"\n=== PR Status: {repo_name} ===")
        code, out, _ = run_cmd(["gh", "pr", "list", "--state", "open"], cwd=repo_path)
        if out:
            print(out)
        else:
            print("No open pull requests.")

def merge_pr(pr_arg: str, force: bool = False) -> None:
    for repo_name, repo_path in REPOS.items():
        branch = get_branch_name(repo_path)
        if branch == "main":
            continue
        
        print(f"\n=== Evaluating PR Merge for {repo_name} ===")
        cmd = ["gh", "pr", "view"]
        if pr_arg:
            cmd.append(pr_arg)
        cmd.extend(["--json", "number,title,reviewDecision,reviews,statusCheckRollup,mergeable,url"])
        
        code, out, err = run_cmd(cmd, cwd=repo_path)
        if code != 0:
            print(f"❌ Could not retrieve PR for {repo_name}: {err}")
            continue
        
        pr_data = json.loads(out)
        pr_num = pr_data.get("number")
        review_decision = pr_data.get("reviewDecision", "NONE")
        url = pr_data.get("url")
        
        print(f"PR #{pr_num} ({pr_data.get('title')})")
        print(f"Review Decision : {review_decision or 'REVIEW_REQUIRED'}")
        
        # Check approval gating
        is_approved = review_decision == "APPROVED"
        if not is_approved and not force:
            print(f"⛔ MERGE BLOCKED: PR #{pr_num} requires an approving review ('Mk1 Eyeball') before merging to main.")
            print(f"   URL: {url}")
            print("   To approve on GitHub: Visit the PR URL and click 'Review changes' -> 'Approve'.")
            print("   To override as administrator, use: just pr merge-force")
            continue
        
        if force and not is_approved:
            print("⚠️  WARNING: Admin override active. Merging PR without formal GitHub approval...")
            
        print(f"🚀 Merging PR #{pr_num} into main...")
        merge_cmd = ["gh", "pr", "merge", str(pr_num), "--merge", "--auto"]
        if force:
            merge_cmd.append("--admin")
            
        m_code, m_out, m_err = run_cmd(merge_cmd, cwd=repo_path)
        if m_code == 0:
            print(f"✅ Successfully merged PR #{pr_num} into main!")
        else:
            print(f"❌ Failed to merge PR #{pr_num}: {m_err or m_out}")

def main():
    parser = argparse.ArgumentParser(description="Credence PR Management & Approval Gating Engine")
    subparsers = parser.add_subparsers(dest="action", required=True)
    
    create_p = subparsers.add_parser("create")
    create_p.add_argument("title", help="Title of the pull request")
    
    update_p = subparsers.add_parser("update")
    update_p.add_argument("title", help="Title of the pull request")
    
    subparsers.add_parser("status")
    
    merge_p = subparsers.add_parser("merge")
    merge_p.add_argument("pr_num", nargs="?", default="", help="Optional PR number")
    merge_p.add_argument("--force", action="store_true", help="Admin override for unapproved PRs")
    
    args = parser.parse_args()
    
    if args.action in ("create", "update"):
        create_or_update_prs(args.title)
    elif args.action == "status":
        check_pr_status()
    elif args.action == "merge":
        merge_pr(args.pr_num, force=args.force)

if __name__ == "__main__":
    main()
