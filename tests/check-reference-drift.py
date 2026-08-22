#!/usr/bin/env python3
"""PR-only drift check for the reverse `Depends-on:` index tests/check-invariants.py
validates (see that file's check (i)).

Diffs base vs head for every docs/*.md file that changed in this pull request.
For each `Depends-on (reverse index ...):` heading whose own body text changed,
where the reverse index names a skill whose SKILL.md was NOT also touched in
the same PR, this posts one warning line into a single batched PR comment:

    docs/ledger-format.md § Body markers changed but project-catchup/SKILL.md
    (which cites it) wasn't touched in this PR -- check the citation still
    holds.

This is a coarse proxy for staleness, not a proof of it -- a section can be
edited without invalidating anything that cites it, and this script has no way
to tell the difference. It therefore never fails the build: it only posts a
comment, and any internal error is reported to stderr with an exit 0 rather
than a failure, so an unrelated CI environment problem here never blocks an
unrelated PR. Design: by-carlos/daikenja#192 (comment), implemented for #195.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

HEADING_RE = re.compile(r"^(#+)\s+(.+?)\s*$", re.MULTILINE)
REVERSE_DEPENDS_HEADER_RE = re.compile(
    r"^Depends-on \(reverse index[\s\S]*?\):[ \t]*\n", re.MULTILINE
)
REVERSE_DEPENDS_ITEM_RE = re.compile(r"^- § (.+?) -- (.+)$")
DEPENDS_ITEM_RE = re.compile(r'([A-Za-z0-9_.-]+)\s+"([^"]+)"')


def run(args):
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def show(sha, path):
    """File content at `sha`, or None if the path does not exist there."""
    result = run(["git", "show", f"{sha}:{path}"])
    if result.returncode != 0:
        return None
    return result.stdout


def parse_reverse_index(text):
    """{heading: [(skill, title), ...]} from a doc's own Depends-on block, or
    {} if it has none. Malformed entries are skipped here -- check (i) in
    check-invariants.py is what fails the build on those."""
    header_match = REVERSE_DEPENDS_HEADER_RE.search(text)
    if not header_match:
        return {}

    index = {}
    for line in text[header_match.end():].splitlines():
        if line.strip() == "":
            break
        item_match = REVERSE_DEPENDS_ITEM_RE.match(line)
        if not item_match:
            continue
        heading, pairs_text = item_match.groups()
        pairs = DEPENDS_ITEM_RE.findall(pairs_text)
        if pairs:
            index[heading.strip()] = pairs
    return index


def heading_body(text, heading_name):
    """The body of `heading_name` -- from just after its heading line to the
    next heading of equal-or-higher level, or EOF. None if not found."""
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match and match.group(2).strip() == heading_name:
            start, level = i + 1, len(match.group(1))
            break
    if start is None:
        return None

    end = len(lines)
    for j in range(start, len(lines)):
        match = HEADING_RE.match(lines[j])
        if match and len(match.group(1)) <= level:
            end = j
            break
    return "\n".join(lines[start:end])


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def main():
    base_sha = os.environ.get("BASE_SHA")
    head_sha = os.environ.get("HEAD_SHA")
    if not base_sha or not head_sha:
        print(
            "check-reference-drift: BASE_SHA/HEAD_SHA not set, skipping "
            "(not a pull_request build?)",
            file=sys.stderr,
        )
        return 0

    all_changed = run(["git", "diff", "--name-only", base_sha, head_sha])
    if all_changed.returncode != 0:
        print(f"check-reference-drift: git diff failed:\n{all_changed.stderr}", file=sys.stderr)
        return 0
    changed_files = set(all_changed.stdout.splitlines())

    changed_docs = sorted(p for p in changed_files if p.startswith("docs/") and p.endswith(".md"))

    warnings = []
    for doc_path in changed_docs:
        head_text = show(head_sha, doc_path)
        if head_text is None:
            continue  # deleted in this PR -- nothing to index

        reverse_index = parse_reverse_index(head_text)
        if not reverse_index:
            continue

        base_text = show(base_sha, doc_path)
        if base_text is None:
            continue  # newly added in this PR -- nothing to diff against

        for heading, pairs in reverse_index.items():
            head_body = heading_body(head_text, heading)
            base_body = heading_body(base_text, heading)
            if head_body is None or base_body is None:
                continue  # heading resolution is check (i)'s job, not this script's
            if normalize(head_body) == normalize(base_body):
                continue

            for skill, _title in pairs:
                skill_path = f"skills/{skill}/SKILL.md"
                if skill_path in changed_files:
                    continue  # same PR touched the citing skill -- stay silent
                warnings.append(
                    f"{doc_path} § {heading} changed but {skill}/SKILL.md "
                    "(which cites it) wasn't touched in this PR -- check the "
                    "citation still holds."
                )

    if not warnings:
        print("check-reference-drift: no drift found.")
        return 0

    # dedupe while preserving order -- the same (doc, heading, skill) can only
    # occur once, but a skill cited under two headings in one doc is not a dup.
    seen = set()
    unique_warnings = []
    for warning in warnings:
        if warning not in seen:
            seen.add(warning)
            unique_warnings.append(warning)

    print("check-reference-drift: found potential drift:")
    for warning in unique_warnings:
        print(f"  - {warning}")

    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("check-reference-drift: PR_NUMBER not set, not posting a comment", file=sys.stderr)
        return 0

    body = (
        "**Reference drift check**\n\n"
        "This PR edits a reference doc section that a skill's `Depends-on:` "
        "entry cites, without touching that skill in the same PR. This is a "
        "coarse proxy for staleness, not proof of it -- please check the "
        "citation still holds.\n\n"
        + "\n".join(f"- {warning}" for warning in unique_warnings)
    )
    try:
        comment = run(["gh", "pr", "comment", pr_number, "--body", body])
        if comment.returncode != 0:
            print(f"check-reference-drift: failed to post PR comment:\n{comment.stderr}", file=sys.stderr)
    except OSError as exc:
        print(f"check-reference-drift: could not run gh: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never fail the build over this check's own bugs
        print(f"check-reference-drift: unexpected error, skipping: {exc}", file=sys.stderr)
        sys.exit(0)
