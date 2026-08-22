#!/usr/bin/env python3
"""Enforce the invariants every v2 build stage checked by hand.

(a) `claude plugin validate .` exits zero (warnings are fine, non-zero is not).
(c) Every skills/*/SKILL.md frontmatter block parses as YAML, has `name` and
    `description`, `name` matches its directory, and `description` is not
    truncated by an unquoted ": " (which silently drops the whole block at
    load time while the skill still appears to load).
(d) docs/upgrading.md's version headings are well-formed, newest-first, and
    each names a version CHANGELOG.md also records.
(e) tests/fixtures/ledger-backfill.md agrees with docs/ledger-format.md. The
    fixture's two bulk writes are replayed through the insert rule the contract
    states, and its Changelog lines through the continuation-join and range
    expansion it defines. This is the one part of the ledger contract that is
    arithmetic rather than judgement, so it is the one part worth checking
    mechanically -- every other fixture in tests/ is still exercised by hand.
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
DOCS_DIR = REPO_ROOT / "docs"
SKILLS_DIR = REPO_ROOT / "skills"
UPGRADING = REPO_ROOT / "docs" / "upgrading.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
BACKFILL_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "ledger-backfill.md"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
FIXTURES_README = REPO_ROOT / "tests" / "README.md"

ENTRY_RE = re.compile(
    r"^(- \[[ x]\] |- )(\d{4}-\d{2}-\d{2}) -- ([DO]-\d{3,}) -- (@\S+) -- (.*)$"
)
CHANGELOG_LINE_RE = re.compile(
    r"^- (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z) -- (.+?) -- (.*)$"
)
RANGE_RE = re.compile(r"^(\+|~|-|resolved |superseded )([DO])-(\d+)\.\.([DO])-(\d+)$")
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


def fenced_blocks(lines, heading):
    """Every fenced block under `heading`, up to the next heading of its level."""
    level = len(heading) - len(heading.lstrip("#"))
    try:
        index = lines.index(heading) + 1
    except ValueError:
        return None
    blocks, current = [], None
    while index < len(lines):
        line = lines[index]
        if current is None and line.startswith("#"):
            if len(line) - len(line.lstrip("#")) <= level:
                break
        if line.startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append(current)
                current = None
        elif current is not None:
            current.append(line)
        index += 1
    return blocks


def insert_at_date_position(section, entry):
    """docs/ledger-format.md § Ordering: directly above the first entry whose
    date is the same as or older than the new one, else at the end."""
    for index, existing in enumerate(section):
        if existing.group(2) <= entry.group(2):
            return section[:index] + [entry] + section[index:]
    return section + [entry]


def expand_summary(block, location):
    """Join continuation lines, then expand ranges, per § Compacting a long
    summary. Returns the changes in order, or None if an item cannot be read."""
    joined, changes = [], []
    for line in block:
        match = CHANGELOG_LINE_RE.match(line)
        if match:
            joined.append([match.group(1), list(match.groups())[2]])
        elif joined and line.startswith("  ") and not line.strip().startswith("- "):
            joined[-1][1] += " " + line.strip()
    for timestamp, summary in joined:
        for item in [part.strip() for part in summary.split(",") if part.strip()]:
            found = RANGE_RE.match(item)
            if not found:
                changes.append((timestamp, item))
                continue
            verb, first_section, first, last_section, last = found.groups()
            if first_section != last_section:
                fail("e: ledger fixture", location, f"range crosses sections: {item}")
                return None
            if int(first) >= int(last):
                fail("e: ledger fixture", location, f"range does not run forwards: {item}")
                return None
            for number in range(int(first), int(last) + 1):
                changes.append((timestamp, f"{verb}{first_section}-{number:03d}"))
    return changes


def check_ledger_backfill_fixture():
    location = str(BACKFILL_FIXTURE)
    if not BACKFILL_FIXTURE.exists():
        fail("e: ledger fixture", location, "file is missing")
        return

    lines = BACKFILL_FIXTURE.read_text(encoding="utf-8").splitlines()
    walks = [
        ("## The starting ledger", 1),
        ("## Walk 1: the first bulk write", 2),
        ("## Walk 2: a second bulk write, three days later", 2),
    ]
    blocks = {}
    for heading, wanted in walks:
        found = fenced_blocks(lines, heading)
        if found is None:
            fail("e: ledger fixture", location, f"heading not found: {heading}")
            return
        if len(found) < wanted:
            fail(
                "e: ledger fixture",
                location,
                f"'{heading}' has {len(found)} fenced blocks, expected at least {wanted}",
            )
            return
        blocks[heading] = found

    def entries(block):
        return [ENTRY_RE.match(line) for line in block if ENTRY_RE.match(line)]

    state = {"D": [], "O": []}
    for entry in entries(blocks["## The starting ledger"][0]):
        state[entry.group(3)[0]].append(entry)

    changes, allocated = [], set()
    for heading, _ in walks[1:]:
        proposal, expected = blocks[heading][0], blocks[heading][1]

        for entry in entries(proposal):
            key = entry.group(3)
            section = state[key[0]]
            existing = [item.group(3) for item in section]
            if key in existing:
                section[existing.index(key)] = entry      # edit in place
            else:
                if key in allocated:
                    fail("e: ledger fixture", location, f"{key} allocated twice")
                    return
                allocated.add(key)
                state[key[0]] = insert_at_date_position(section, entry)

        for kind in ("D", "O"):
            want = [e.group(0) for e in entries(expected) if e.group(3)[0] == kind]
            if not want:
                continue                                   # that walk shows one section
            got = [e.group(0) for e in state[kind]]
            if got != want:
                fail(
                    "e: ledger fixture",
                    location,
                    f"'{heading}' {kind} section does not match the insert rule.\n"
                    f"      contract gives: {[l.split(' -- ')[1] for l in got]}\n"
                    f"      fixture states: {[l.split(' -- ')[1] for l in want]}",
                )
                return

        expanded = expand_summary(proposal, location)
        if expanded is None:
            return
        changes += expanded

    if not changes:
        fail("e: ledger fixture", location, "no Changelog changes recovered from the walks")
        return

    present = {e.group(3) for e in state["D"] + state["O"]}
    for _, item in changes:
        named = re.match(r"^(?:\+|~|-|resolved |superseded )([DO]-\d+)$", item)
        if named and named.group(1) not in present:
            fail(
                "e: ledger fixture",
                location,
                f"Changelog names {named.group(1)}, which no entry in the walks creates",
            )

    malformed = fenced_blocks(lines, "### Malformed compactions, for the failure path")
    if not malformed:
        fail(
            "e: ledger fixture",
            location,
            "the malformed-compaction block is missing -- reading rule 5 is unexercised",
        )
        return
    for line in malformed[0]:
        match = CHANGELOG_LINE_RE.match(line)
        if not match:
            continue
        found = RANGE_RE.match(match.group(3).strip())
        if found and found.group(2) == found.group(4) and int(found.group(3)) < int(found.group(5)):
            fail(
                "e: ledger fixture",
                location,
                f"'{match.group(3)}' is filed as malformed but expands cleanly",
            )


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


def main():
    check_plugin_validate()
    check_skill_frontmatter()
    check_upgrading_headings()
    check_ledger_backfill_fixture()
    check_fixture_inventory()
    check_fixture_dependencies()
    check_reference_dependencies()

    if failures:
        print("Invariant checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("All invariant checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
