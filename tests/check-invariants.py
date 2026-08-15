#!/usr/bin/env python3
"""Enforce the invariants every v2 build stage checked by hand.

(a) `claude plugin validate .` exits zero (warnings are fine, non-zero is not).
(c) Every skills/*/SKILL.md frontmatter block parses as YAML, has `name` and
    `description`, `name` matches its directory, and `description` is not
    truncated by an unquoted ": " (which silently drops the whole block at
    load time while the skill still appears to load).

Check (b), the em dash / en dash scan, is intentionally not implemented: the
rule it would enforce was removed (issue #2), so there is nothing left to
check.

Exits non-zero on the first invariant that fails, after running every check
and printing all failures found.
"""

import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

failures = []


def fail(invariant, location, detail):
    failures.append(f"[{invariant}] {location}: {detail}")


def check_plugin_validate():
    result = subprocess.run(
        ["claude", "plugin", "validate", "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        fail(
            "a: claude plugin validate",
            str(REPO_ROOT),
            f"exited {result.returncode}\n{result.stdout}\n{result.stderr}",
        )


def check_skill_frontmatter():
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        fail("c: skill frontmatter", str(SKILLS_DIR), "no skills/*/SKILL.md files found")
        return

    for skill_file in skill_files:
        directory_name = skill_file.parent.name
        text = skill_file.read_text(encoding="utf-8")

        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            fail("c: skill frontmatter", str(skill_file), "does not start with a '---' frontmatter delimiter")
            continue
        try:
            end_index = lines[1:].index("---") + 1
        except ValueError:
            fail("c: skill frontmatter", str(skill_file), "no closing '---' delimiter found")
            continue
        frontmatter_text = "\n".join(lines[1:end_index])

        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as exc:
            detail = str(exc)
            if "mapping values are not allowed here" in detail:
                fail(
                    "c: skill frontmatter",
                    str(skill_file),
                    "frontmatter fails to parse, likely an unquoted ': ' inside a scalar value "
                    f"(this silently drops the whole block at load time): {detail}",
                )
            else:
                fail("c: skill frontmatter", str(skill_file), f"frontmatter fails to parse: {detail}")
            continue

        if not isinstance(frontmatter, dict):
            fail("c: skill frontmatter", str(skill_file), "frontmatter did not parse to a mapping")
            continue

        name = frontmatter.get("name")
        description = frontmatter.get("description")

        if not name:
            fail("c: skill frontmatter", str(skill_file), "missing 'name'")
        elif name != directory_name:
            fail(
                "c: skill frontmatter",
                str(skill_file),
                f"'name: {name}' does not match its directory '{directory_name}'",
            )

        if not description:
            fail("c: skill frontmatter", str(skill_file), "missing 'description'")
        elif not isinstance(description, str):
            fail(
                "c: skill frontmatter",
                str(skill_file),
                "'description' did not parse as a single scalar string "
                "(an unquoted ': ' would have turned it into a nested mapping)",
            )


def main():
    check_plugin_validate()
    check_skill_frontmatter()

    if failures:
        print("Invariant checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("All invariant checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
