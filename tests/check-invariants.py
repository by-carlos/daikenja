#!/usr/bin/env python3
"""Enforce the invariants every v2 build stage checked by hand.

(a) `claude plugin validate .` exits zero (warnings are fine, non-zero is not).
(c) Every skills/*/SKILL.md frontmatter block parses as YAML, has `name` and
    `description`, `name` matches its directory, and `description` is not
    truncated by an unquoted ": " (which silently drops the whole block at
    load time while the skill still appears to load).
(d) docs/upgrading.md's version headings are well-formed, newest-first, and
    each names a version CHANGELOG.md also records.
(e) The two ledger format specs and their templates start with their
    format-version lines, and each template's version matches its spec's:
    docs/decisions-format.md and templates/DECISIONS.md with
    `<!-- decisions-format: N -->`, docs/open-format.md and templates/open.md
    with `<!-- daikenja-open-format: N -->`. Every reading skill and
    `project-log` key their newer-format behaviour on that first line, so a
    spec or template that loses it, or drifts from the other, is a silent
    format change.
(g) The set of files under tests/fixtures/ equals the set of fixture names
    tests/README.md mentions, reported in both directions.
(h) Every `Depends on:` line found in tests/fixtures/*.md resolves: each
    `name "Section Title"` pair names a real docs/*.md file or skills/*/SKILL.md
    file, and the quoted title matches a `#`/`##`/`###` heading in that file,
    verbatim after stripping the leading `#`s and whitespace. A fixture with no
    `Depends on:` line at all is not an error here -- only a malformed one is.
(i) Every `Depends-on (reverse index ...):` block found in docs/*.md resolves:
    each `§ Heading -- name "Section Title"` entry names a real heading in the
    doc's own file, a real skills/*/SKILL.md file, and a quoted title matching
    a `#`/`##`/`###` heading in that skill file. This is the reverse of (h) --
    a doc names the skill sections that cite one of its own headings, instead
    of a fixture naming the doc/skill sections it exercises -- and reuses the
    same `name "Section Title"` pair grammar. A doc with no `Depends-on:` block
    at all is not an error here -- only a malformed one is.
(j) Every relative link or image in the repository's Markdown (README.md, the
    other top-level .md files, docs/**/*.md, bot/README.md, templates/README.md
    and tests/README.md) points at a file or directory that exists. The fragment
    after `#` is not checked, and fenced code blocks are skipped. A page moved
    or renamed without its inbound links is the failure this catches.
(k) templates/personas.md starts with the line `<!-- daikenja:private -->`.
    It is the marker a git guard keys on to keep persona notes out of a
    commit, and every file setup-user and remember-persona scaffold copies
    this template, so a template that loses the line ships unmarked files.

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
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SKILLS_DIR = REPO_ROOT / "skills"
UPGRADING = REPO_ROOT / "docs" / "upgrading.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
VERSION_LINE_FILES = (
    # (spec, template, version-line pattern)
    ("docs/decisions-format.md", "templates/DECISIONS.md",
     re.compile(r"^<!-- decisions-format: (\d+) -->$")),
    ("docs/open-format.md", "templates/open.md",
     re.compile(r"^<!-- daikenja-open-format: (\d+) -->$")),
)
PRIVATE_MARKER = "<!-- daikenja:private -->"
PRIVATE_MARKER_TEMPLATES = ("templates/personas.md",)
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
FIXTURES_README = REPO_ROOT / "tests" / "README.md"

FIXTURE_REF_RE = re.compile(r"fixtures/([a-zA-Z0-9_-]+\.md)")

BRACKET_HEADING_RE = re.compile(
    r"^## \[([^\]]+)\](?: - (\d{4}-\d{2}-\d{2}))?[ \t]*$", re.MULTILINE
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

DEPENDS_ON_RE = re.compile(r"^Depends on: (.+)$", re.MULTILINE)
DEPENDS_ITEM_RE = re.compile(r'([A-Za-z0-9_.-]+)\s+"([^"]+)"')
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)

REVERSE_DEPENDS_HEADER_RE = re.compile(
    r"^Depends-on \(reverse index[\s\S]*?\):[ \t]*\n", re.MULTILINE
)
REVERSE_DEPENDS_ITEM_RE = re.compile(r"^- § (.+?) -- (.+)$")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LINK_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)

failures = []


def fail(invariant, location, detail):
    failures.append(f"[{invariant}] {location}: {detail}")


def check_plugin_validate():
    # shutil.which honours PATHEXT, so on Windows it finds claude.cmd, which
    # subprocess cannot launch from the bare name "claude".
    claude = shutil.which("claude")
    if claude is None:
        fail("a: claude plugin validate", str(REPO_ROOT), "claude is not on PATH")
        return
    result = subprocess.run(
        [claude, "plugin", "validate", "."],
        check=False,
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


def check_format_version_lines():
    for spec, template, pattern in VERSION_LINE_FILES:
        versions = {}
        for name in (spec, template):
            path = REPO_ROOT / name
            if not path.exists():
                fail("e: format version lines", name, "file is missing")
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            match = pattern.match(lines[0]) if lines else None
            if not match:
                fail(
                    "e: format version lines",
                    name,
                    f"line 1 is not a format-version line matching {pattern.pattern}",
                )
                continue
            versions[name] = match.group(1)
        if len(versions) == 2 and versions[spec] != versions[template]:
            fail(
                "e: format version lines",
                template,
                f"version {versions[template]} differs from {spec}'s {versions[spec]}",
            )


def check_private_marker_templates():
    for name in PRIVATE_MARKER_TEMPLATES:
        path = REPO_ROOT / name
        if not path.exists():
            fail("k: private marker", name, "file is missing")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != PRIVATE_MARKER:
            fail("k: private marker", name, f"line 1 is not exactly {PRIVATE_MARKER}")


def check_fixture_dependencies():
    if not FIXTURES_DIR.is_dir():
        fail("h: fixture dependencies", str(FIXTURES_DIR), "directory is missing")
        return

    heading_cache = {}

    def headings_for(path):
        if path not in heading_cache:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                heading_cache[path] = {
                    heading.strip() for _, heading in HEADING_RE.findall(text)
                }
            else:
                heading_cache[path] = None
        return heading_cache[path]

    for fixture in sorted(FIXTURES_DIR.glob("*.md")):
        text = fixture.read_text(encoding="utf-8")
        match = DEPENDS_ON_RE.search(text)
        if not match:
            continue  # not every fixture has one yet -- that is not an error

        items = DEPENDS_ITEM_RE.findall(match.group(1))
        if not items:
            fail(
                "h: fixture dependencies",
                str(fixture),
                f"'Depends on:' line found but no 'name \"Section Title\"' pairs parsed: {match.group(1)!r}",
            )
            continue

        for name, title in items:
            if name.endswith(".md"):
                target = DOCS_DIR / name
            else:
                target = SKILLS_DIR / name / "SKILL.md"

            headings = headings_for(target)
            if headings is None:
                fail(
                    "h: fixture dependencies",
                    str(fixture),
                    f"'Depends on:' names '{name}', which does not resolve to {target}",
                )
                continue

            if title not in headings:
                fail(
                    "h: fixture dependencies",
                    str(fixture),
                    f"'Depends on:' quotes \"{title}\" for '{name}', which has no matching "
                    f"#/##/### heading in {target}",
                )


def check_reference_dependencies():
    if not DOCS_DIR.is_dir():
        fail("i: reference dependencies", str(DOCS_DIR), "directory is missing")
        return

    heading_cache = {}

    def headings_for(path):
        if path not in heading_cache:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                heading_cache[path] = {
                    heading.strip() for _, heading in HEADING_RE.findall(text)
                }
            else:
                heading_cache[path] = None
        return heading_cache[path]

    for doc in sorted(DOCS_DIR.glob("*.md")):
        text = doc.read_text(encoding="utf-8")
        header_match = REVERSE_DEPENDS_HEADER_RE.search(text)
        if not header_match:
            continue  # not every doc has one -- that is not an error

        doc_headings = headings_for(doc)
        for line in text[header_match.end():].splitlines():
            if line.strip() == "":
                break

            item_match = REVERSE_DEPENDS_ITEM_RE.match(line)
            if not item_match:
                fail(
                    "i: reference dependencies",
                    str(doc),
                    f"'Depends-on:' block has a line that doesn't parse: {line!r}",
                )
                continue

            heading, pairs_text = item_match.groups()
            heading = heading.strip()
            if heading not in doc_headings:
                fail(
                    "i: reference dependencies",
                    str(doc),
                    f"'Depends-on:' indexes '§ {heading}', which has no matching "
                    f"#/##/### heading in {doc.name} itself",
                )

            pairs = DEPENDS_ITEM_RE.findall(pairs_text)
            if not pairs:
                fail(
                    "i: reference dependencies",
                    str(doc),
                    f"'§ {heading}' entry has no 'name \"Section Title\"' pairs "
                    f"parsed: {pairs_text!r}",
                )
                continue

            for skill, title in pairs:
                target = SKILLS_DIR / skill / "SKILL.md"
                skill_headings = headings_for(target)
                if skill_headings is None:
                    fail(
                        "i: reference dependencies",
                        str(doc),
                        f"'§ {heading}' names skill '{skill}', which does not "
                        f"resolve to {target}",
                    )
                    continue

                if title not in skill_headings:
                    fail(
                        "i: reference dependencies",
                        str(doc),
                        f"'§ {heading}' quotes \"{title}\" for '{skill}', which "
                        f"has no matching #/##/### heading in {target}",
                    )


def check_fixture_inventory():
    if not FIXTURES_README.exists():
        fail("g: fixture inventory", str(FIXTURES_README), "file is missing")
        return
    if not FIXTURES_DIR.is_dir():
        fail("g: fixture inventory", str(FIXTURES_DIR), "directory is missing")
        return

    on_disk = {path.name for path in FIXTURES_DIR.glob("*.md")}
    named = set(FIXTURE_REF_RE.findall(FIXTURES_README.read_text(encoding="utf-8")))

    undocumented = sorted(on_disk - named)
    if undocumented:
        fail(
            "g: fixture inventory",
            str(FIXTURES_README),
            f"fixtures on disk but not named in tests/README.md: {undocumented}",
        )

    nonexistent = sorted(named - on_disk)
    if nonexistent:
        fail(
            "g: fixture inventory",
            str(FIXTURES_DIR),
            f"tests/README.md names fixtures that do not exist on disk: {nonexistent}",
        )


def markdown_link_sources():
    sources = sorted(REPO_ROOT.glob("*.md"))
    sources += sorted(DOCS_DIR.rglob("*.md"))
    # Only templates/README.md: the templates themselves hold placeholder links.
    sources += [REPO_ROOT / "templates" / "README.md"]
    sources += [REPO_ROOT / "bot" / "README.md", FIXTURES_README]
    return [path for path in sources if path.exists()]


def check_relative_links():
    for path in markdown_link_sources():
        in_fence = False
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in MD_LINK_RE.findall(line):
                if target.startswith("#") or LINK_SCHEME_RE.match(target):
                    continue
                file_part = target.split("#", 1)[0]
                if not (path.parent / file_part).exists():
                    fail(
                        "j: relative links",
                        f"{path.relative_to(REPO_ROOT).as_posix()}:{number}",
                        f"links to '{target}', which does not exist",
                    )


def main():
    check_plugin_validate()
    check_skill_frontmatter()
    check_upgrading_headings()
    check_format_version_lines()
    check_private_marker_templates()
    check_fixture_inventory()
    check_fixture_dependencies()
    check_reference_dependencies()
    check_relative_links()

    if failures:
        print("Invariant checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("All invariant checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
