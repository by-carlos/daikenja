#!/usr/bin/env python3
"""PR-only warn-level size trigger for skills/*/SKILL.md growth.

Design: by-carlos/daikenja#164 (comment on measured growth), scoped by #194.

For every skills/*/SKILL.md changed in this pull request, compares its size
in the PR head against its size at the most recent release tag reachable from
the PR base. When the head size is SIZE_MULTIPLE times the baseline or more,
this posts (or updates, if it already commented on this PR) a single comment
naming the file, the baseline size, the current size, and the ratio, pointing
at the section-level measurement done on #164 as the review to redo.

This is a nudge, not a cap: it never fails the build and never modifies the
file. A file reviewed and accepted at its new size is not flagged again until
it doubles past the *next* release tag, since the baseline moves with each
release. Any internal error is reported to stderr with exit 0 rather than a
failure, so an unrelated CI environment problem here never blocks an
unrelated PR.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SIZE_MULTIPLE = 2  # starting point recommended by the #164 measurement
SKILL_MD_RE = re.compile(r"^skills/[^/]+/SKILL\.md$")
COMMENT_MARKER = "<!-- check-skill-size.py -->"


def run(args):
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def file_size_at(sha, path):
    """Byte size of `path` at `sha`, or None if it doesn't exist there."""
    result = run(["git", "cat-file", "-s", f"{sha}:{path}"])
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def latest_release_tag(sha):
    """Most recent tag reachable from `sha`, or None if there isn't one."""
    result = run(["git", "describe", "--tags", "--abbrev=0", sha])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def find_existing_comment(repo, pr_number):
    """id of this script's own prior comment on the PR, or None."""
    result = run([
        "gh", "api", f"repos/{repo}/issues/{pr_number}/comments",
        "--jq", f'[.[] | select(.body | startswith("{COMMENT_MARKER}"))] | last | .id',
    ])
    if result.returncode != 0:
        return None
    comment_id = result.stdout.strip()
    return comment_id if comment_id and comment_id != "null" else None


def main():
    base_sha = os.environ.get("BASE_SHA")
    head_sha = os.environ.get("HEAD_SHA")
    if not base_sha or not head_sha:
        print(
            "check-skill-size: BASE_SHA/HEAD_SHA not set, skipping "
            "(not a pull_request build?)",
            file=sys.stderr,
        )
        return 0

    diff = run(["git", "diff", "--name-only", base_sha, head_sha])
    if diff.returncode != 0:
        print(f"check-skill-size: git diff failed:\n{diff.stderr}", file=sys.stderr)
        return 0
    changed_files = diff.stdout.splitlines()

    changed_skills = sorted(p for p in changed_files if SKILL_MD_RE.match(p))
    if not changed_skills:
        print("check-skill-size: no SKILL.md files changed.")
        return 0

    tag = latest_release_tag(base_sha)
    if not tag:
        print("check-skill-size: no release tag reachable from base, skipping.", file=sys.stderr)
        return 0

    findings = []
    for path in changed_skills:
        baseline = file_size_at(tag, path)
        if baseline is None:
            continue  # didn't exist at the last release -- no baseline to compare against
        current = file_size_at(head_sha, path)
        if current is None:
            continue  # deleted in this PR
        if baseline <= 0 or current < baseline * SIZE_MULTIPLE:
            continue
        findings.append((path, baseline, current, current / baseline))

    if not findings:
        print("check-skill-size: no file crossed the size trigger.")
        return 0

    print(f"check-skill-size: files past {SIZE_MULTIPLE}x their size at {tag}:")
    for path, baseline, current, ratio in findings:
        print(f"  - {path}: {baseline} -> {current} bytes ({ratio:.1f}x)")

    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("check-skill-size: PR_NUMBER not set, not posting a comment", file=sys.stderr)
        return 0

    lines = "\n".join(
        f"- `{path}`: {baseline:,} -> {current:,} bytes ({ratio:.1f}x since `{tag}`)"
        for path, baseline, current, ratio in findings
    )
    body = (
        f"{COMMENT_MARKER}\n"
        "**Skill size check**\n\n"
        f"This PR pushes a `SKILL.md` to {SIZE_MULTIPLE}x or more of its size at "
        "the last release. That isn't a problem by itself -- #164 found growth "
        "like this was real capability, not padding -- but it's the point to "
        "look again: do a section-level pass like the one on #164 and confirm "
        "the growth is still muscle before it doubles again.\n\n"
        f"{lines}"
    )

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    try:
        existing_id = find_existing_comment(repo, pr_number) if repo else None
        if existing_id:
            update = run([
                "gh", "api", f"repos/{repo}/issues/comments/{existing_id}",
                "-X", "PATCH", "-f", f"body={body}",
            ])
            if update.returncode != 0:
                print(f"check-skill-size: failed to update PR comment:\n{update.stderr}", file=sys.stderr)
        else:
            create = run(["gh", "pr", "comment", pr_number, "--body", body])
            if create.returncode != 0:
                print(f"check-skill-size: failed to post PR comment:\n{create.stderr}", file=sys.stderr)
    except OSError as exc:
        print(f"check-skill-size: could not run gh: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never fail the build over this check's own bugs
        print(f"check-skill-size: unexpected error, skipping: {exc}", file=sys.stderr)
        sys.exit(0)
