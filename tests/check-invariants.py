#!/usr/bin/env python3
"""Enforce the invariants every v2 build stage checked by hand.

(a) `claude plugin validate .` exits zero (warnings are fine, non-zero is not).
(c) Every skills/*/SKILL.md frontmatter block parses as YAML, has `name` and
    `description`, `name` matches its directory, and `description` is not
    truncated by an unquoted ": " (which silently drops the whole block at
    load time while the skill still appears to load).
(d) docs/upgrading.md's version headings are well-formed, newest-first, and
    each names a version CHANGELOG.md also records.

Check (b), the em dash / en dash scan, is intentionally not implemented: the
rule it would enforce was removed (issue #2), so there is nothing left to
check.

What (d) deliberately does NOT check is the rule that matters most: that a pull
request touching user-side data adds an `## [Unreleased]` section to
docs/upgrading.md. Whether a diff changes something already on a user's disk is
a judgement, not a pattern, and a check that guessed at it would either pass
everything or block every unrelated change. That rule is enforced by review,
stated in CONTRIBUTING.md. What is left is mechanical and still worth having:
`setup-user`'s upgrade branch reads that file top to bottom and applies the
sections later than the user's recorded version, so an out-of-order heading
applies migrations in the wrong sequence, and a version that was never released
cannot be compared against anything.

Exits non-zero on the first invariant that fails, after running every check
and printing all failures found.
"""

import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
UPGRADING = REPO_ROOT / "docs" / "upgrading.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

BRACKET_HEADING_RE = re.compile(
    r"^## \[([^\]]+)\](?: - (\d{4}-\d{2}-\d{2}))?[ \t]*$", re.MULTILINE
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

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


def check_upgrading_headings():
    if not UPGRADING.exists():
        fail("d: upgrading.md", str(UPGRADING), "file is missing")
        return

    headings = BRACKET_HEADING_RE.findall(UPGRADING.read_text(encoding="utf-8"))
    if not headings:
        fail(
            "d: upgrading.md",
            str(UPGRADING),
            "no '## [version]' headings found -- it should hold at least one section",
        )
        return

    versions = []
    for index, (label, date) in enumerate(headings):
        if label == "Unreleased":
            if index != 0:
                fail(
                    "d: upgrading.md",
                    str(UPGRADING),
                    "'## [Unreleased]' must come first -- sections are newest-first",
                )
            if date:
                fail(
                    "d: upgrading.md",
                    str(UPGRADING),
                    "'## [Unreleased]' must not carry a date",
                )
            continue
        if not SEMVER_RE.match(label):
            fail("d: upgrading.md", str(UPGRADING), f"'## [{label}]' is not a semver version")
            continue
        if not date:
            fail("d: upgrading.md", str(UPGRADING), f"'## [{label}]' has no ' - YYYY-MM-DD' date")
        versions.append(label)

    parsed = [tuple(int(part) for part in version.split(".")) for version in versions]
    if parsed != sorted(parsed, reverse=True):
        fail(
            "d: upgrading.md",
            str(UPGRADING),
            f"version headings are not newest-first: {versions}. "
            "setup-user applies them in the order it reads them.",
        )

    if not CHANGELOG.exists():
        fail("d: upgrading.md", str(CHANGELOG), "file is missing")
        return

    released = {
        label
        for label, _ in BRACKET_HEADING_RE.findall(CHANGELOG.read_text(encoding="utf-8"))
    }
    for version in versions:
        if version not in released:
            fail(
                "d: upgrading.md",
                str(UPGRADING),
                f"'## [{version}]' names a version CHANGELOG.md does not record",
            )


def main():
    check_plugin_validate()
    check_skill_frontmatter()
    check_upgrading_headings()

    if failures:
        print("Invariant checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("All invariant checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
