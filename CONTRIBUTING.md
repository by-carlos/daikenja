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

Use the issue forms; the follow-up form carries four sections, in this order:
**In plain terms** (what is wrong or wanted and why it matters, without file
or issue names), **Context** (what was observed, when, with file paths and
command output), **Options / proposed fix** (the candidate approaches, with a
recommendation and what you rejected), and **AI prompt** (a self-contained
brief a fresh session can act on cold). Use absolute dates -- "15 Aug 2026",
never "last Tuesday".

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
  and [`docs/config-resolution.md`](docs/config-resolution.md) § Voice and
  writing style fixes how a user's own `writing-style.md` layers on top of it.
  Read both before changing either.
- **Ledger format.** [`docs/decisions-format.md`](docs/decisions-format.md)
  and [`docs/open-format.md`](docs/open-format.md) are the parsing contract that
  existing ledger files depend on. Each file's version line and the `open.md`
  item line -- its ` -- ` separator and two-split bound -- are frozen unless an
  issue explicitly scopes a format change. `decisions-format.md` is a
  byte-identical copy of plan-staged-rollout's spec: change it upstream, then
  copy it.
- **Templates.** Files under `templates/` are copied to a user's machine and
  never edited by the plugin afterwards, so a change there affects only new
  copies.
- **Where a file goes: three categories.** `skills/` ships to every user and
  Claude Code loads it. `bot/` ships to every user and Claude Code does not
  load it -- it is a Python service run by hand, so it stays lean and holds
  nothing a skill needs. `.claude/` is guidance for people working on this
  repo and ships nothing. Contributor-facing instructions never belong in
  `skills/`.
- **Test fixtures.** Everything under `tests/fixtures/` must stay synthetic --
  invented projects, invented people, `example.com` links. Never put real work
  content, personal data or organization data there.
- **Line endings.** `.gitattributes` pins LF. Check your staged diff is in
  proportion to your edit before committing.
- **Shared-document size.** If a change touches a document under `docs/` that
  is read in full by more than three skills and the file crosses roughly 500
  lines, the change should include a split review: does it divide along
  read/write or per-skill lines with zero duplicated sentences, the way the
  #130 split of the config docs did? The outcome is allowed to be "no split" --
  this is a prompt to look, not a size cap. The old single-file ledger spec
  growing 328 to 773 lines in two days while seven skills read it in full
  (measured on #117) is the case that motivated this.
- **`SKILL.md` size.** CI's `validate` job runs `tests/check-skill-size.py` on
  every pull request: if a `skills/*/SKILL.md` you touch reaches 2x its size at
  the last release tag, it posts a comment on the PR naming the file, the
  baseline size and the current size. It's warn-only -- never fails the build,
  never edits the file -- and it means do a section-level pass like the one on
  #164 (worked examples and rationale vs. step instructions) and confirm the
  growth is still muscle, not that anything must be cut.

## Validation

`.github/workflows/ci.yml` runs on every push and pull request:

- **gitleaks** scans the full history for secrets, with historical findings
  baselined in `.gitleaks-baseline.json`.
- **invariant checks** run `tests/check-invariants.py`.
- **bot** runs the `bot/` unit tests on Python 3.10 and 3.x, then imports the
  Slack transport once to catch the dependency range going stale.

Run both locally before pushing:

```bash
python tests/check-invariants.py
cd bot && python -m unittest discover -s tests -t .
```

The bot suite needs no Slack workspace, no network and no Claude Code CLI --
the Slack client and the headless session are both injected.

There is no test runner for the skills themselves. The fixtures under
`tests/fixtures/` are exercised by hand through the skills.

## Development

Load the working tree straight into a session, from the repo root:

```bash
claude --plugin-dir .
```

Run `/reload-plugins` after editing a skill to pick up the change without
restarting. Validate the manifest with:

```bash
claude plugin validate .
```

Installing this repo as a **local marketplace** is not a substitute for the
above: it copies the tree into the plugin cache at install time rather than
referencing it live, so edits go stale until you reinstall. Use
`--plugin-dir .` for development.

Layout:

```
.claude-plugin/plugin.json        the manifest
.claude-plugin/marketplace.json   lists this repo as its own marketplace
skills/                           one directory per skill, each with a SKILL.md
bot/                              the optional Slack service, and its own tests
templates/                        blank files copied out to the user
docs/                             the contracts the skills implement
docs/guide/                       the user guide the README links to
docs/diagrams/                    hand-drawn SVG diagrams used by the guide
tests/                            invariant checks and the hand-run fixtures
.claude/                          guidance for people working on this repo
```

`docs/` holds the contracts. A skill implements a contract and never redefines
one, so a format change happens in `docs/` first. `tests/check-invariants.py`,
run in CI, catches the parts of this it can check mechanically (like a
skill's headings drifting from what a contract's reverse index expects).

## User documentation

The README is a landing page: what Daikenja is, whether it fits, how to
install it, how to try it, and where to read next. Depth lives in
[`docs/guide/`](docs/guide/), one page per thing a reader is trying to do.

- **A change to what a user sees updates the guide in the same pull request.**
  That includes a skill's name, what it writes, whether it runs from plain
  language, and anything in [Your data](docs/guide/your-data.md).
- **Every guide page opens with the same nav line**, current page in bold, then
  an **In short:** box. A new page is added to the nav line of every page and
  to the README's Documentation table.
- **One name per concept, one canonical place per fact.** Other pages link to
  it rather than restating it. "Persona" (notes on a real person), "reviewer"
  (`preflight`'s built-in readers) and "Tensei" are kept apart.
- **Diagrams.** The SVGs in `docs/diagrams/` are hand-written source with a
  `<title>`, `<desc>` and `aria-label`; a change that alters what one shows
  updates it in the same pull request. Mermaid blocks inside guide pages
  follow the same rule.
- **The FAQ answers questions people actually asked.** Each answer is short
  and links to the page that owns the full story; it never describes
  behaviour no other page does.
- `tests/check-invariants.py` fails on a relative link that does not resolve.

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
