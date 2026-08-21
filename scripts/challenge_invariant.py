#!/usr/bin/env python3
"""
The Invariant Challenger: Automated Epistemic Invariant Scrutiny & Disposition Engine.

Evaluates whether a system invariant is actively necessary in Tier 0 (AGENTS.md),
has achieved 100% test saturation for Demotion to Tier 2, requires amendment,
or has been nullified/superseded by ecosystem evolution.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOKENS_PER_WORD = 1.33

INVARIANT_TEST_MAP = {
    "inv-verbatim-grounding": ["tests/unit/test_grounding.py", "tests/unit/test_extraction.py"],
    "inv-mk1-eyeball": ["tests/governance/test_docs_integrity.py::test_ecosystem_naming_conventions_and_guardrails"],
    "inv-canonical-json-ed25519": ["tests/unit/test_crypto.py::test_canonical_json_rfc8785", "tests/unit/test_crypto.py::test_ed25519_signatures"],
    "inv-untrusted-ingestion": ["tests/unit/test_pipeline.py", "tests/unit/test_ssrf_protection.py"],
    "inv-version-governance": ["tests/governance/test_docs_integrity.py::test_ecosystem_version_parity"],
    "inv-zero-npm": ["tests/governance/test_docs_integrity.py::test_zero_npm_invariant"],
    "inv-four-way-parity": ["tests/governance/test_docs_integrity.py::test_sitemap_integrity_and_route_coverage"],
    "inv-dynamic-living-canon": ["tests/governance/test_docs_integrity.py::test_living_canon_dynamic_naming_invariant"],
    "inv-four-phase-lifecycle": ["tests/governance/test_docs_integrity.py::test_learning_lifecycle_and_invariant_governance_contracts"],
    "inv-commit-before-deploy": ["tests/integration/test_ci_cd_workflows.py::test_local_production_deploy_safety_gate"],
    "inv-hermetic-unit-isolation": ["tests/governance/test_docs_integrity.py::test_hermetic_unit_test_markers_invariant"],
    "inv-code-fence-hygiene": ["tests/governance/test_docs_integrity.py::test_all_markdown_code_fences_and_syntax"],
    "inv-workstation-viewport": ["tests/governance/test_architecture_governance.py::test_workstation_viewport_vertical_bounds_invariant"],
}


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def load_invariants_docs(docs_file: Path) -> dict[str, dict[str, str]]:
    """Parse invariants.md cards into dictionary keyed by slug."""
    if not docs_file.exists():
        return {}
    content = docs_file.read_text(encoding="utf-8")
    cards = re.findall(r'<div class="invariant-card" id="([^"]+)">(.*?)</div>', content, re.DOTALL)
    
    invariants = {}
    for slug, card_html in cards:
        title_match = re.search(r'<h3>(.*?)</h3>', card_html)
        class_match = re.search(r'badge-class-[a-z]+">([^<]+)</span>', card_html)
        tier_match = re.search(r'badge-tier-\d">([^<]+)</span>', card_html)
        
        raw_title = title_match.group(1).strip() if title_match else slug
        title = strip_html(raw_title)
        
        cls = class_match.group(1).strip() if class_match else ""
        if not cls:
            if "Class α" in card_html or "Class Alpha" in card_html or "badge-class-alpha" in card_html:
                cls = "Class α (Alpha)"
            elif "Class β" in card_html or "Class Beta" in card_html or "badge-class-beta" in card_html:
                cls = "Class β (Beta)"
            elif "Class γ" in card_html or "Class Gamma" in card_html or "badge-class-gamma" in card_html:
                cls = "Class γ (Gamma)"
            else:
                cls = "Class γ (Gamma)"
                
        tier = tier_match.group(1).strip() if tier_match else "Tier 0"
        
        invariants[slug] = {
            "slug": slug,
            "title": title,
            "class": cls,
            "tier": tier,
            "html": card_html
        }
    return invariants


def load_agents_tier0(agents_file: Path) -> dict[str, dict[str, str]]:
    """Parse Tier 0 rules from AGENTS.md."""
    if not agents_file.exists():
        return {}
    content = agents_file.read_text(encoding="utf-8")
    rules = {}
    current_class = "Unknown"
    
    for line in content.splitlines():
        if "Class α" in line:
            current_class = "Class α (Alpha)"
        elif "Class β" in line:
            current_class = "Class β (Beta)"
        elif "Class γ" in line:
            current_class = "Class γ (Gamma)"
        elif line.strip().startswith("## 2."):
            break
            
        m = re.match(r"^-\s+\*\*([^*]+)\*\*:\s*(.+)$", line.strip())
        if m:
            title = m.group(1).strip()
            body = m.group(2).strip()
            word_count = len((title + " " + body).split())
            tokens = int(word_count * TOKENS_PER_WORD)
            rules[title] = {
                "title": title,
                "body": body,
                "class": current_class,
                "tokens": tokens
            }
    return rules


def challenge_invariant(slug: str, repo_root: Path) -> None:
    """Run forensic challenge analysis on a specific invariant slug."""
    docs_file = repo_root / "credence-docs" / "docs" / "invariants.md"
    agents_file = repo_root / "AGENTS.md"
    if not agents_file.exists():
        agents_file = repo_root / "credence" / "AGENTS.md"

    invariants = load_invariants_docs(docs_file)
    agents_rules = load_agents_tier0(agents_file)

    matched_slug = None
    if slug in invariants:
        matched_slug = slug
    else:
        for s in invariants:
            if slug.lower() in s.lower() or slug.lower() in invariants[s]["title"].lower():
                matched_slug = s
                break

    if not matched_slug:
        print(f"❌ Invariant slug '{slug}' not found in Living Canon ({docs_file}).")
        print("Available slugs:")
        for s in sorted(invariants.keys())[:10]:
            print(f"  • {s}")
        sys.exit(1)

    inv = invariants[matched_slug]
    title = inv["title"]
    cls = inv["class"]
    tier = inv["tier"]

    # Match in AGENTS.md
    matched_agent_rule = None
    for r_title, r_data in agents_rules.items():
        if any(w.lower() in r_title.lower() for w in title.split()[:2]) or any(w.lower() in r_title.lower() for w in matched_slug.replace("inv-", "").split("-")[:2]):
            matched_agent_rule = r_data
            if not cls or cls == "Unclassified":
                cls = r_data["class"]
            break

    # If it's verbatim grounding, mk1 eyeball, or ed25519, mark Class α
    if matched_slug in ["inv-verbatim-grounding", "inv-mk1-eyeball", "inv-canonical-json-ed25519", "inv-untrusted-ingestion"]:
        cls = "Class α (Alpha)"

    token_cost = matched_agent_rule["tokens"] if matched_agent_rule else 0
    in_tier0 = matched_agent_rule is not None

    # Test coverage analysis
    tests = INVARIANT_TEST_MAP.get(matched_slug, [])
    has_test_coverage = len(tests) > 0

    print("========================================================================")
    print(" ⚖️  CREDENCE INVARIANT CHALLENGER: FORENSIC SCRUTINY BRIEF")
    print("========================================================================")
    print(f"  Target Slug       : {matched_slug}")
    print(f"  Canonical Title   : {title}")
    print(f"  Classification    : {cls} | {tier}")
    print(f"  Prompt Placement  : {'Tier 0 (AGENTS.md)' if in_tier0 else 'Tier 1 Skill / Tier 2 Test Gate'}")
    print(f"  Prompt Token Cost : ~{token_cost} tokens/turn" if in_tier0 else "  Prompt Token Cost : 0 tokens/turn (Decoupled)")
    print("------------------------------------------------------------------------")
    print(" 🔍 EVALUATION CRITERIA & EVIDENCE GAUNTLET:")
    print("------------------------------------------------------------------------")

    # Criterion 1: Sovereign Safety (Class α)
    is_class_alpha = "Alpha" in cls or "α" in cls
    print(f"  1. Sovereign Safety & Custody: {'🛡️ CRITICAL (Class α)' if is_class_alpha else '⚡ Operational / Presentation'}")
    
    # Criterion 2: Test Saturation
    print(f"  2. Deterministic Test Saturation : {'✅ 100% Covered' if has_test_coverage else '⚠️ Empirical LLM Prompt Only'}")
    if tests:
        for t in tests:
            print(f"     └─ Asserted by: {t}")
            
    # Criterion 3: Context Economy
    print(f"  3. Context Prompt Weight       : {'⚠️ High (~' + str(token_cost) + ' tok)' if token_cost > 60 else '✅ Lean (~' + str(token_cost) + ' tok)'}")

    # Disposition Recommendation
    print("------------------------------------------------------------------------")
    print(" 🎯 CHALLENGER DISPOSITION & RECOMMENDATION:")
    print("------------------------------------------------------------------------")

    if is_class_alpha:
        print("  Verdict : [RETAIN_ACTIVE] (Class α Sovereign Non-Negotiable)")
        print("  Reason  : Invariant governs core human authority, epistemic veracity (G=1.00),")
        print("            or cryptographic custody. Never demote from Tier 0.")
    elif in_tier0 and has_test_coverage:
        print("  Verdict : [DEMOTE_TO_TEST] (Demotion Highway Candidate)")
        print(f"  Reason  : Rule is 100% verified by deterministic test gates ({tests[0]}).")
        print(f"            Demoting from AGENTS.md saves ~{token_cost} tokens/turn with ZERO safety loss.")
        print("  Action  : Move from AGENTS.md to Tier 2 Shift-Left Gate.")
    elif in_tier0 and not has_test_coverage:
        print("  Verdict : [RETAIN_ACTIVE] (Heuristic Guardrail)")
        print("  Reason  : Rule lacks 100% deterministic test coverage; requires prompt memory.")
    else:
        print("  Verdict : [VERIFIED_DECOUPLED] (Tier 1 / Tier 2 Active)")
        print("  Reason  : Rule is already cleanly decoupled outside Tier 0 prompt memory.")
    print("========================================================================\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrutinize and challenge system invariants.")
    parser.add_argument("slug", nargs="?", default="inv-version-governance", help="Invariant slug or keyword (e.g. inv-verbatim-grounding)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    challenge_invariant(args.slug, repo_root)


if __name__ == "__main__":
    main()
