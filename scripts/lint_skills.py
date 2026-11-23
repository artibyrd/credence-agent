#!/usr/bin/env python3
"""Automated Skill, Overlay, and Plugin Manifest Linter for Credence.

Validates:
1. Every skill directory under skills/ contains a valid SKILL.md under the 24,000-byte cap.
2. YAML frontmatter contains lowercase kebab-case 'name' (matching directory) and 'description'.
3. Zero disallowed Claude Code-specific frontmatter keys.
4. Description adheres to token economy budget (<= 280 chars, <= 40 words).
5. All markdown code fences start at column 0 with valid syntax specifiers and balanced closures.
6. plugin.json contains strictly supported Antigravity schema keys and <= 3 suggestedPrompts.
7. overrides/*.md files contain zero SKILL.md files and enforce the 3-section delta contract.
8. Zero machine-local paths (/home/<user>/, /Users/<user>/) leaked into plugin files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - stdlib fallback for bare CI runners
    yaml = None

MAX_DESCRIPTION_CHARS = 280
MAX_DESCRIPTION_WORDS = 40
MAX_SKILL_BODY_BYTES = 24000

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_PLUGIN_KEYS = {
    "$schema",
    "name",
    "displayName",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "logo",
    "suggestedPrompts",
    "disabled",
}
DISALLOWED_CLAUDE_FRONTMATTER_KEYS = {
    "disable-model-invocation",
    "user-invocable",
    "argument-hint",
    "context",
    "agent",
    "allowed-tools",
}
REQUIRED_OVERLAY_SECTIONS = (
    "## Overrides",
    "## Extensions",
    "## Disabled / Not Applicable",
)
LOCAL_PATH_PATTERNS = (
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\"),
)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def _parse_frontmatter_fallback(fm_raw: str) -> dict[str, str]:
    """Minimal zero-dependency YAML frontmatter parser for simple key/value & folded scalars."""
    fields: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []

    def flush() -> None:
        nonlocal current_key, block_lines
        if current_key is not None and block_lines:
            fields[current_key] = " ".join(line.strip() for line in block_lines).strip()
        current_key = None
        block_lines = []

    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace() and current_key is not None:
            block_lines.append(line)
            continue
        flush()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val in {">", ">-", "|", "|-"}:
            current_key = key
            block_lines = []
        else:
            fields[key] = val.strip('"').strip("'")
    flush()
    return fields


def _lint_code_fences(label: str, lines: list[str]) -> list[str]:
    """Validate column-0 language-tagged code fences and balanced closures."""
    errors: list[str] = []
    in_code_block = False
    fence_opener_line = 0

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not line.startswith("```"):
                errors.append(f"[{label}:L{idx}] Code fence has leading whitespace (must start at column 0)")

            if not in_code_block:
                in_code_block = True
                fence_opener_line = idx
                tag = line[3:].strip()
                if not tag and not stripped.startswith("````"):
                    errors.append(f"[{label}:L{idx}] Code fence opening missing syntax language tag")
            else:
                in_code_block = False

    if in_code_block:
        errors.append(f"[{label}:L{fence_opener_line}] Unclosed code fence at end of file")
    return errors


def _lint_relative_links(label: str, md_path: Path, content: str) -> list[str]:
    """Verify relative markdown links inside plugin skills/overrides resolve cleanly."""
    errors: list[str] = []
    cleaned = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    for match in MD_LINK_RE.finditer(cleaned):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#", "/", "customization://", "file://")):
            continue
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            continue
        resolved = (md_path.parent / clean_target).resolve()
        if not resolved.exists():
            errors.append(f"[{label}] Broken relative link '{target}'")
    return errors


def lint_skill_file(skill_path: Path) -> list[str]:
    """Lint a single SKILL.md file and return a list of error strings."""
    errors: list[str] = []
    dir_name = skill_path.parent.name

    if not skill_path.exists():
        return [f"Missing SKILL.md in directory '{dir_name}'"]

    content = skill_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    if not content.startswith("---"):
        errors.append(f"[{dir_name}] Missing opening YAML frontmatter '---'")
        return errors

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        errors.append(f"[{dir_name}] Malformed or unclosed YAML frontmatter")
        return errors

    fm_raw = fm_match.group(1)
    body = content[fm_match.end() :]
    body_bytes = len(body.encode("utf-8"))
    if body_bytes > MAX_SKILL_BODY_BYTES:
        errors.append(
            f"[{dir_name}] Skill body is {body_bytes} bytes (exceeds {MAX_SKILL_BODY_BYTES}-byte Antigravity cap)"
        )

    if yaml is not None:
        try:
            fm = yaml.safe_load(fm_raw)
        except Exception as exc:
            errors.append(f"[{dir_name}] Invalid YAML in frontmatter: {exc}")
            return errors
    else:
        fm = _parse_frontmatter_fallback(fm_raw)

    if not isinstance(fm, dict):
        errors.append(f"[{dir_name}] Frontmatter must be a key-value mapping")
        return errors

    disallowed = sorted(set(fm.keys()) & DISALLOWED_CLAUDE_FRONTMATTER_KEYS)
    if disallowed:
        errors.append(f"[{dir_name}] Disallowed Claude-specific frontmatter key(s): {', '.join(disallowed)}")

    name = fm.get("name")
    if not name or not isinstance(name, str):
        errors.append(f"[{dir_name}] Frontmatter missing required 'name' field")
    elif not KEBAB_RE.match(name):
        errors.append(f"[{dir_name}] Skill name '{name}' must be lowercase kebab-case")
    elif name != dir_name:
        errors.append(f"[{dir_name}] Skill name '{name}' does not match directory '{dir_name}'")

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

    errors.extend(_lint_code_fences(dir_name, lines))
    errors.extend(_lint_relative_links(dir_name, skill_path, content))
    return errors


def lint_plugin_manifest(manifest_path: Path) -> list[str]:
    """Validate credence-agent/plugin.json against Antigravity plugin schema rules."""
    errors: list[str] = []
    if not manifest_path.is_file():
        return [f"Missing plugin manifest at {manifest_path}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"[plugin.json] Invalid JSON: {exc}"]

    if not isinstance(manifest, dict):
        return ["[plugin.json] Root must be a JSON object"]

    unknown = sorted(set(manifest.keys()) - ALLOWED_PLUGIN_KEYS)
    if unknown:
        errors.append(f"[plugin.json] Unsupported top-level key(s): {', '.join(unknown)}")

    name = manifest.get("name")
    if not isinstance(name, str) or not KEBAB_RE.match(name):
        errors.append(f"[plugin.json] 'name' must be lowercase kebab-case (got {name!r})")

    desc = manifest.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("[plugin.json] 'description' must be a non-empty string")

    prompts = manifest.get("suggestedPrompts")
    if prompts is not None:
        if not isinstance(prompts, list) or not all(isinstance(p, str) and p.strip() for p in prompts):
            errors.append("[plugin.json] 'suggestedPrompts' must be a list of non-empty strings")
        elif len(prompts) > 3:
            errors.append(f"[plugin.json] 'suggestedPrompts' has {len(prompts)} entries (max 3)")

    return errors


def lint_overrides_dir(overrides_dir: Path) -> list[str]:
    """Validate project overlays in overrides/*.md follow the 3-section delta contract."""
    errors: list[str] = []
    if not overrides_dir.is_dir():
        return [f"Missing overrides directory at {overrides_dir}"]

    if list(overrides_dir.rglob("SKILL.md")):
        errors.append("[overrides] SKILL.md files are forbidden inside overrides/ (use <skill-name>.md)")

    overlay_files = sorted(p for p in overrides_dir.glob("*.md") if p.is_file())
    if not overlay_files:
        return [f"[overrides] No overlay markdown files found in {overrides_dir}"]

    for overlay_path in overlay_files:
        stem = overlay_path.stem
        label = f"overrides/{overlay_path.name}"
        if not KEBAB_RE.match(stem):
            errors.append(f"[{label}] Overlay filename stem '{stem}' must be lowercase kebab-case")
        content = overlay_path.read_text(encoding="utf-8")
        for section in REQUIRED_OVERLAY_SECTIONS:
            if section not in content:
                errors.append(f"[{label}] Missing required delta section '{section}'")
        errors.extend(_lint_code_fences(label, content.splitlines()))

    return errors


def lint_local_paths(plugin_root: Path) -> list[str]:
    """Scan plugin files for accidental machine-local absolute path leaks."""
    errors: list[str] = []
    for path in sorted(plugin_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, line in enumerate(text.splitlines(), start=1):
            for pat in LOCAL_PATH_PATTERNS:
                match = pat.search(line)
                if match:
                    rel = path.relative_to(plugin_root)
                    errors.append(f"[{rel}:L{idx}] Machine-local path leak '{match.group(0)}'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Credence Antigravity skills, overlays, and manifest.")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=None,
        help="Path to skills directory (default: credence-agent/skills)",
    )
    parser.add_argument(
        "--overrides-dir",
        type=Path,
        default=None,
        help="Path to overrides directory (default: credence-agent/overrides)",
    )
    args = parser.parse_args()

    plugin_root = Path(__file__).resolve().parent.parent
    skills_dir = args.skills_dir.resolve() if args.skills_dir else (plugin_root / "skills").resolve()
    overrides_dir = args.overrides_dir.resolve() if args.overrides_dir else (plugin_root / "overrides").resolve()

    if not skills_dir.exists():
        print(f"❌ Error: Skills directory not found at {skills_dir}", file=sys.stderr)
        return 1

    skill_subdirs = [p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if not skill_subdirs:
        print(f"❌ Error: No skills found in {skills_dir}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    checked_skills = 0

    for skill_dir in sorted(skill_subdirs):
        skill_file = skill_dir / "SKILL.md"
        checked_skills += 1
        all_errors.extend(lint_skill_file(skill_file))

    all_errors.extend(lint_plugin_manifest(plugin_root / "plugin.json"))
    all_errors.extend(lint_overrides_dir(overrides_dir))
    all_errors.extend(lint_local_paths(plugin_root))

    if all_errors:
        print(f"❌ Found {len(all_errors)} violation(s) across {checked_skills} skills and overlays:\n")
        for err in all_errors:
            print(f"  • {err}")
        return 1

    overlay_count = len(list(overrides_dir.glob("*.md")))
    print(
        f"✅ Passed linting: {checked_skills} skills, {overlay_count} overlays, plugin.json, and zero local paths ({skills_dir.relative_to(plugin_root.parent)})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
