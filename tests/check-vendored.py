#!/usr/bin/env python3
"""Keeps the files Daikenja copies byte-identical from other repositories in step.

Each copy is pinned in tests/vendored.json: the local path, the upstream
repository and path, the upstream commit it was copied from, and the git blob
hash of the file at that commit. The upstream file is the source of truth;
the local copy is never edited here.

Three modes:

- default (every push and pull request, offline): the local file's git blob
  hash must equal the pinned `blob`. A hand edit, a CRLF conversion or a
  partial re-copy fails the build.
- `--upstream` (the daily drift workflow): the pinned `blob` must be the file
  at the pinned `commit`, and the file on the upstream default branch must
  still have that blob. Upstream moving fails the run, naming the command
  that re-syncs.
- `--resync` (by hand): copies each upstream file from its default branch
  and rewrites the pin. Review the diff and commit it like any other change.

Upstream reads go through the GitHub REST API, authenticated with GH_TOKEN or
GITHUB_TOKEN when either is set. Standard library only.
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PIN_FILE = REPO_ROOT / "tests" / "vendored.json"
API = "https://api.github.com"


def blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def api_get(url, raw=False):
    headers = {"Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        body = resp.read()
    return body if raw else json.loads(body)


def upstream_blob(repo, path, ref):
    return api_get(f"{API}/repos/{repo}/contents/{path}?ref={ref}")["sha"]


def default_branch_head(repo):
    branch = api_get(f"{API}/repos/{repo}")["default_branch"]
    return api_get(f"{API}/repos/{repo}/commits/{branch}")["sha"]


def check_local(entries):
    failures = []
    for e in entries:
        local = REPO_ROOT / e["path"]
        if not local.is_file():
            failures.append(f"{e['path']}: missing")
            continue
        got = blob_sha(local.read_bytes())
        if got != e["blob"]:
            failures.append(
                f"{e['path']}: blob {got} does not match the pinned {e['blob']} "
                f"({e['upstream_repo']} {e['upstream_path']} at {e['commit'][:7]}). "
                "The copy is never edited here: revert it, or re-sync with "
                "`python tests/check-vendored.py --resync`."
            )
    return failures


def check_upstream(entries):
    failures = []
    heads = {}
    for e in entries:
        repo = e["upstream_repo"]
        pinned = upstream_blob(repo, e["upstream_path"], e["commit"])
        if pinned != e["blob"]:
            failures.append(
                f"{e['path']}: the pinned blob {e['blob']} is not "
                f"{e['upstream_path']} at {e['commit'][:7]} ({pinned})."
            )
            continue
        head = heads.setdefault(repo, default_branch_head(repo))
        current = upstream_blob(repo, e["upstream_path"], head)
        if current != e["blob"]:
            failures.append(
                f"{e['path']}: {repo} changed {e['upstream_path']} since "
                f"{e['commit'][:7]} (now {head[:7]}). Re-sync with "
                "`python tests/check-vendored.py --resync`, then add a "
                "CHANGELOG.md entry, and a docs/upgrading.md note if users "
                "must re-run an installer."
            )
    return failures


def resync(pins):
    heads = {}
    for e in pins["files"]:
        repo = e["upstream_repo"]
        head = heads.setdefault(repo, default_branch_head(repo))
        data = api_get(f"{API}/repos/{repo}/contents/{e['upstream_path']}?ref={head}", raw=True)
        (REPO_ROOT / e["path"]).write_bytes(data)
        changed = blob_sha(data) != e["blob"]
        e["commit"], e["blob"] = head, blob_sha(data)
        print(f"{e['path']}: {'updated' if changed else 'unchanged'} at {repo}@{head[:7]}")
    PIN_FILE.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--upstream", action="store_true", help="also compare against upstream")
    mode.add_argument("--resync", action="store_true", help="re-copy from upstream and re-pin")
    args = parser.parse_args()

    pins = json.loads(PIN_FILE.read_text(encoding="utf-8"))
    if args.resync:
        resync(pins)
        return 0

    failures = check_local(pins["files"])
    if args.upstream and not failures:
        failures = check_upstream(pins["files"])
    for f in failures:
        print(f"check-vendored: {f}", file=sys.stderr)
    if not failures:
        scope = "local copies and upstream" if args.upstream else "local copies"
        print(f"check-vendored: {len(pins['files'])} pinned file(s) match ({scope}).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
