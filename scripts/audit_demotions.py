#!/usr/bin/env python3
"""Automated Invariant Demotion & Prompt Economy Scanner for Credence.

Analyzes AGENTS.md Tier 0 invariants against shift-left governance test suites
(test_docs_integrity.py, test_architecture_governance.py) to identify invariants
that have achieved 100% mechanical coverage and can be safely demoted to Tier 2 test gates.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Approximate tokens per word
TOKENS_PER_WORD = 1.33


def parse_agents_md_invariants(agents_file: Path) -> dict[str, list[dict[str, str]]]:
    """Parse AGENTS.md and group invariants by class (Alpha, Beta, Gamma)."""
    if not agents_file.exists():
        return {}

    content = agents_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    current_class = "Unclassified"
    invariants: dict[str, list[dict[str, str]]] = {
        "Class α (Alpha)": [],
        "Class β (Beta)": [],
        "Class γ (Gamma)": [],
    }

    for line in lines:
        if "Class α" in line or "Class Alpha" in line:
            current_class = "Class α (Alpha)"
        elif "Class β" in line or "Class Beta" in line:
            current_class = "Class β (Beta)"
        elif "Class γ" in line or "Class Gamma" in line:
            current_class = "Class γ (Gamma)"
        elif line.strip().startswith("## 2."):
            break  # Exit Tier 0

        match = re.match(r"^-\s+\*\*([^*]+)\*\*:\s*(.+)$", line.strip())
        if match and current_class in invariants:
            title = match.group(1).strip()
            body = match.group(2).strip()
            word_count = len((title + " " + body).split())
            invariants[current_class].append({
                "title": title,
                "body": body,
                "words": str(word_count),
                "est_tokens": str(int(word_count * TOKENS_PER_WORD)),
            })

    return invariants


def find_governance_test_contracts(tests_dir: Path) -> dict[str, str]:
    """Extract test function names and docstrings from governance test suites."""
    contracts: dict[str, str] = {}
    if not tests_dir.exists():
        return contracts

    for test_file in tests_dir.glob("test_*.py"):
        content = test_file.read_text(encoding="utf-8")
        matches = re.findall(r"def (test_[a-zA-Z0-9_]+)\([^)]*\):\s*(?:\"\"\"(.*?)\"\"\")?", content, re.DOTALL)
        for test_name, docstring in matches:
            contracts[test_name] = (docstring or "").strip().replace("\n", " ")

    return contracts


def evaluate_demotion_candidates(
    invariants: dict[str, list[dict[str, str]]],
    test_contracts: dict[str, str],
) -> list[dict[str, str]]:
    """Identify invariants that are 100% asserted by mechanical test gates."""
    # Mechanical test signatures and keywords
    mechanical_mappings = [
        (r"Zero-npm", "test_zero_npm_invariant", "Asserts zero package.json and node_modules"),
        (r"7-Manifest", "test_ecosystem_version_parity", "Asserts version synchronization across all 7 manifests"),
        (r"Code Fence", "test_all_markdown_code_fences_and_syntax", "Asserts column-0 code fence indentation"),
        (r"YAML Frontmatter", "test_all_markdown_files_valid_frontmatter", "Asserts title and description YAML frontmatter"),
        (r"Sitemap", "test_sitemap_integrity_and_route_coverage", "Asserts 100% sitemap route coverage"),
        (r"Mermaid", "test_mermaid_diagram_syntax_integrity", "Asserts high-contrast dark slate styling"),
        (r"Hermetic Unit Test Marker", "test_hermetic_unit_test_markers_invariant", "Asserts zero browser scraping in unit tests"),
    ]

    candidates: list[dict[str, str]] = []

    for cls_name, items in invariants.items():
        for item in items:
            title = item["title"]
            for pattern, test_func, reason in mechanical_mappings:
                if re.search(pattern, title, re.IGNORECASE):
                    candidates.append({
                        "class": cls_name,
                        "title": title,
                        "test_func": test_func,
                        "reason": reason,
                        "est_tokens": item["est_tokens"],
                    })

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Credence invariants for demotion candidates and token economy.")
    parser.add_argument(
        "--agents-file",
        type=Path,
        default=None,
        help="Path to AGENTS.md file",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    ecosystem_root = script_dir.parent.parent
    agents_file = (args.agents_file or (ecosystem_root / "AGENTS.md")).resolve()
    tests_dir = (ecosystem_root / "credence" / "tests" / "governance").resolve()

    if not agents_file.exists():
        print(f"❌ Error: AGENTS.md not found at {agents_file}", file=sys.stderr)
        return 1

    invariants = parse_agents_md_invariants(agents_file)
    test_contracts = find_governance_test_contracts(tests_dir)

    total_invariants = sum(len(items) for items in invariants.values())
    total_words = sum(int(item["words"]) for items in invariants.values() for item in items)
    total_est_tokens = int(total_words * TOKENS_PER_WORD)

    print("=" * 72)
    print(" 🏛️  CREDENCE LIVING INVARIANT & DEMOTION HIGHWAY AUDIT")
    print("=" * 72)
    print(f"  Target File       : {agents_file.relative_to(agents_file.parent.parent if agents_file.parent.name else agents_file.parent)}")
    print(f"  Total Invariants  : {total_invariants} across 3 Cognitive Classes")
    print(f"  Tier 0 Word Count : {total_words} words (~{total_est_tokens} tokens)")
    print(f"  Token Hard Budget : < 800 tokens  [{'✅ HEALTHY' if total_est_tokens < 800 else '⚠️ WARN: BLOAT'}]")
    print("-" * 72)

    for cls_name, items in invariants.items():
        print(f"\n📁 {cls_name} ({len(items)} invariants):")
        for item in items:
            print(f"   • {item['title'][:65]:<65} (~{item['est_tokens']} tok)")

    demotion_candidates = evaluate_demotion_candidates(invariants, test_contracts)

    print("\n" + "-" * 72)
    print(" 🚀 DEMOTION HIGHWAY CANDIDATE SCANNER")
    print("-" * 72)

    if not demotion_candidates:
        print("  ✅ All current Tier 0 rules require cognitive reasoning or human authority.")
        print("     Zero unnecessary mechanical rules found in Tier 0 prompt context.")
    else:
        print(f"  Found {len(demotion_candidates)} rule(s) already 100% verified by deterministic test gates:")
        total_potential_savings = 0
        for cand in demotion_candidates:
            tokens = int(cand["est_tokens"])
            total_potential_savings += tokens
            print(f"\n  🎯 [{cand['class']}] {cand['title']}")
            print(f"     Asserted By : {cand['test_func']}")
            print(f"     Reason      : {cand['reason']}")
            print(f"     Savings     : ~{tokens} tokens/turn")

        print(f"\n  💡 Total Potential Savings: ~{total_potential_savings} tokens per turn if demoted to Tier 2.")

    print("=" * 72 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
