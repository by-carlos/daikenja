#!/usr/bin/env python3
"""Bump the plugin version and rotate CHANGELOG.md's Unreleased section.

Run by .github/workflows/release-prepare.yml. Edits
.claude-plugin/plugin.json and CHANGELOG.md in place; the caller commits the
result and opens a pull request. Never touches the `release` branch or
creates a tag -- that is release-publish.yml's job, run after this PR merges.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from changelog_lib import section_body

REPO = "by-carlos/daikenja"
PLUGIN_JSON = Path(".claude-plugin/plugin.json")
CHANGELOG = Path("CHANGELOG.md")

FEAT_COMMIT_RE = re.compile(r"^feat(\(.+\))?!?:")
UNRELEASED_HEADING_RE = re.compile(r"^## \[Unreleased\][ \t]*$", re.MULTILINE)
UNRELEASED_LINK_RE = re.compile(
    r"^\[Unreleased\]: (.+)/compare/v[0-9.]+\.\.\.HEAD[ \t]*$", re.MULTILINE
)


def current_version():
    data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    return data["version"]


def bump(version, kind):
    major, minor, patch = (int(part) for part in version.split("."))
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def has_feat_commit(since_tag):
    try:
        log = subprocess.run(
            ["git", "log", f"{since_tag}..HEAD", "--format=%s"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except subprocess.CalledProcessError:
        log = subprocess.run(
            ["git", "log", "--format=%s"], check=True, capture_output=True, text=True
        ).stdout
    return any(FEAT_COMMIT_RE.match(line) for line in log.splitlines())


def resolve_bump(requested, current):
    if requested != "auto":
        return requested
    return "minor" if has_feat_commit(f"v{current}") else "patch"


def set_plugin_version(new_version):
    text = PLUGIN_JSON.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'("version":\s*")[^"]+(")', rf"\g<1>{new_version}\g<2>", text, count=1
    )
    if count != 1:
        sys.exit("could not find a version field in .claude-plugin/plugin.json")
    PLUGIN_JSON.write_text(updated, encoding="utf-8")


def rotate_changelog(new_version):
    text = CHANGELOG.read_text(encoding="utf-8")

    heading = UNRELEASED_HEADING_RE.search(text)
    if not heading:
        sys.exit("CHANGELOG.md has no ## [Unreleased] section")
    if not section_body(text, heading.end()):
        sys.exit("## [Unreleased] section is empty -- nothing to release")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = (
        text[: heading.start()]
        + f"## [{new_version}] - {date}"
        + text[heading.end() :]
    )

    link = UNRELEASED_LINK_RE.search(text)
    if not link:
        sys.exit("CHANGELOG.md has no [Unreleased] compare link")
    replacement = (
        f"[Unreleased]: https://github.com/{REPO}/compare/v{new_version}...HEAD\n"
        f"[{new_version}]: https://github.com/{REPO}/releases/tag/v{new_version}"
    )
    text = text[: link.start()] + replacement + text[link.end() :]

    CHANGELOG.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bump", choices=["auto", "patch", "minor"], default="auto")
    parser.add_argument("--github-output")
    args = parser.parse_args()

    current = current_version()
    kind = resolve_bump(args.bump, current)
    new_version = bump(current, kind)

    rotate_changelog(new_version)
    set_plugin_version(new_version)

    print(f"{current} -> {new_version} ({kind} bump)")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"version={new_version}\n")
            fh.write(f"bump={kind}\n")


if __name__ == "__main__":
    main()
