# Contributing

Daikenja is a Claude Code plugin: a set of skills and the documents that define
how they behave. There is no application code to build, so most contributions
are edits to markdown under `skills/`, `docs/` or `templates/`.

The maintainer ([Carlos Eng](https://github.com/by-carlos)) reviews and merges
all pull requests.

## Where to file things

- **A bug or an idea about Daikenja** -- open an issue here.
- **A problem with the marketplace listing or the install command** -- open it
  in [`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins),
  which owns the catalog.

Open an issue before starting anything non-trivial. Typo fixes and other small
corrections can go straight to a pull request.

## What an issue needs

Every issue carries three sections, in this order: **Context** (what was
observed, when, with file paths and command output), **Options** (the candidate
approaches, with a recommendation and what you rejected), and **AI prompt** (a
self-contained blockquote a fresh session can act on cold). Use absolute dates
-- "15 Aug 2026", never "last Tuesday".

**This repository is public.** An issue body is published the moment it is
filed, and stays indexed even if it is edited or deleted afterwards. Scrub
before you file: no hostnames, LAN IPs, container names, personal filesystem
paths, email addresses, tokens, or raw log pastes. Redact to placeholders
(`<host>`, `10.x.x.x`, `/path/to/repo`) and keep the reproduction abstract
enough to stand on its own.

## Workflow

1. **Fork** the repo and branch off `main` (`feat/…`, `fix/…`, `docs/…`).
2. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:`, …), one logical change per commit.
3. **Add a changelog entry** under `## [Unreleased]` in `CHANGELOG.md` as part
   of the change. Never write a dated or versioned heading and never bump the
   version file -- releases are cut separately, as one atomic change.
4. **Add an upgrade note** under `## [Unreleased]` in
   [`docs/upgrading.md`](docs/upgrading.md), **but only if your change touches
   something that already exists on a user's machine** -- the `daikenja.yaml`
   schema, the ledger grammar or location, a skill name, or any path the plugin
   reads. Most changes need nothing here, and a release that changes nothing on
   disk adds nothing to that file. Same as-you-go rule as the changelog, for the
   same reason: a release that has to reconstruct what was breaking across a
   whole batch gets it wrong. A pull request that needs a note and does not have
   one is incomplete.
5. **Open a pull request** against `main`, describing what changed and why.
   Never push directly to `main`.

`main` requires a passing `gitleaks` scan, passing invariant checks, and the
maintainer's Code Owner approval.

## Conventions that are easy to trip over

- **Voice.** Anything Daikenja drafts or rewrites follows [`docs/voice.md`](docs/voice.md),
  and [`docs/config-contract.md`](docs/config-contract.md) fixes how a user's own
  `writing-style.md` layers on top of it. Read both before changing either.
- **Ledger format.** [`docs/ledger-format.md`](docs/ledger-format.md) is a
  parsing contract that existing ledger files depend on. The field separator and
  the split bound are frozen unless an issue explicitly scopes a format change.
- **Templates.** Files under `templates/` are copied to a user's machine and
  never edited by the plugin afterwards, so a change there affects only new
  copies.
- **Shipped vs local.** `skills/` ships to every user; `.claude/` is guidance for
  people working on this repo. Contributor-facing instructions never belong in
  `skills/`.
- **Test fixtures.** Everything under `tests/fixtures/` must stay synthetic --
  invented projects, invented people, `example.com` links. Never put real work
  content, personal data or organization data there.
- **Line endings.** `.gitattributes` pins LF. Check your staged diff is in
  proportion to your edit before committing.

## Validation

`.github/workflows/ci.yml` runs on every push and pull request:

- **gitleaks** scans the full history for secrets, with historical findings
  baselined in `.gitleaks-baseline.json`.
- **invariant checks** run `tests/check-invariants.py`.

Run the invariant checks locally before pushing:

```bash
python tests/check-invariants.py
```

There is no test runner for the skills themselves. The fixtures under
`tests/fixtures/` are exercised by hand through the skills.

## Releases

Releases are the maintainer's call and land as one atomic change: bump
`version` in `.claude-plugin/plugin.json`, promote `## [Unreleased]` to a dated
heading in `CHANGELOG.md` and -- when there is one -- in
[`docs/upgrading.md`](docs/upgrading.md) too, tag `vx.y.z`, and fast-forward the
`release` branch to that tag. The marketplace points at `release`, so a merge to
`main` never reaches installers on its own.

A release only ever **promotes** an upgrade note; it never writes one. If the
batch broke something on disk and nobody added the note when the change landed,
the release has no way to reconstruct it.

## Security

Do not report a security issue through a public issue or pull request. See
[SECURITY.md](SECURITY.md).
