#!/usr/bin/env python3
"""Automated Skill Schema and Frontmatter Linter for Credence Antigravity Skills.

Validates:
1. Every skill directory contains a valid SKILL.md.
2. YAML frontmatter contains 'name' and 'description'.
3. 'name' matches the skill directory name.
4. Description adheres to token economy budget (<= 280 chars, <= 40 words).
5. All markdown code fences start at column 0 with valid syntax specifiers.
6. All code fences are properly balanced and closed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import yaml

MAX_DESCRIPTION_CHARS = 280
MAX_DESCRIPTION_WORDS = 40


def lint_skill_file(skill_path: Path) -> list[str]:
    """Lint a single SKILL.md file and return a list of error strings."""
    errors: list[str] = []
    dir_name = skill_path.parent.name

    if not skill_path.exists():
        return [f"Missing SKILL.md in directory '{dir_name}'"]

    content = skill_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # 1. Frontmatter existence and parsing
    if not content.startswith("---"):
        errors.append(f"[{dir_name}] Missing opening YAML frontmatter '---'")
        return errors

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        errors.append(f"[{dir_name}] Malformed or unclosed YAML frontmatter")
        return errors

    fm_raw = fm_match.group(1)
    try:
        fm = yaml.safe_load(fm_raw)
    except Exception as exc:
        errors.append(f"[{dir_name}] Invalid YAML in frontmatter: {exc}")
        return errors

    if not isinstance(fm, dict):
        errors.append(f"[{dir_name}] Frontmatter must be a key-value mapping")
        return errors

    # 2. 'name' validation
    name = fm.get("name")
    if not name:
        errors.append(f"[{dir_name}] Frontmatter missing required 'name' field")
    elif name != dir_name:
        errors.append(f"[{dir_name}] Skill name '{name}' does not match directory '{dir_name}'")

    # 3. 'description' validation
    desc = fm.get("description")
    if not desc or not isinstance(desc, str) or not desc.strip():
        errors.append(f"[{dir_name}] Frontmatter missing required 'description' field")
    else:
        desc_clean = desc.strip()
        char_len = len(desc_clean)
        word_count = len(desc_clean.split())

        if char_len > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"[{dir_name}] Description exceeds character budget ({char_len} > {MAX_DESCRIPTION_CHARS} chars)"
            )
        if word_count > MAX_DESCRIPTION_WORDS:
            errors.append(
                f"[{dir_name}] Description exceeds word budget ({word_count} > {MAX_DESCRIPTION_WORDS} words)"
            )

    # 4. Code fence hygiene (column 0, syntax specifier, balanced closures)
    in_code_block = False
    fence_opener_line = 0

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not line.startswith("```"):
                errors.append(f"[{dir_name}:L{idx}] Code fence has leading whitespace (must start at column 0)")

            if not in_code_block:
                in_code_block = True
                fence_opener_line = idx
                tag = line[3:].strip()
                if not tag and not stripped.startswith("````"):
                    errors.append(f"[{dir_name}:L{idx}] Code fence opening missing syntax language tag")
            else:
                in_code_block = False

    if in_code_block:
        errors.append(f"[{dir_name}:L{fence_opener_line}] Unclosed code fence at end of file")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Credence Antigravity skills.")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=None,
        help="Path to .agents/skills directory",
    )
    args = parser.parse_args()

    if args.skills_dir:
        skills_dir = args.skills_dir.resolve()
    else:
        # Default: locate relative to script
        script_dir = Path(__file__).resolve().parent
        skills_dir = (script_dir.parent / ".agents" / "skills").resolve()

    if not skills_dir.exists():
        print(f"❌ Error: Skills directory not found at {skills_dir}", file=sys.stderr)
        return 1

    skill_subdirs = [p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if not skill_subdirs:
        print(f"❌ Error: No skills found in {skills_dir}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    checked_count = 0

    for skill_dir in sorted(skill_subdirs):
        skill_file = skill_dir / "SKILL.md"
        checked_count += 1
        errors = lint_skill_file(skill_file)
        if errors:
            all_errors.extend(errors)

    if all_errors:
        print(f"❌ Found {len(all_errors)} skill schema violation(s) across {checked_count} skills:\n")
        for err in all_errors:
            print(f"  • {err}")
        return 1

    print(f"✅ All {checked_count} skills passed schema and frontmatter linting ({skills_dir.relative_to(skills_dir.parent.parent)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
