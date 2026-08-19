# CLAUDE.md -- Daikenja

Instructions for Claude Code and other agents working in this repo.

## Git and merge conventions

- **Merge strategy:** default to **squash merge** for pull requests, unless a
  skill or workflow in this repo specifies otherwise, or the maintainer asks for
  a different one.
- **Branch cleanup:** delete a branch after it is merged, unless the workflow
  says to keep it.
- **Never push directly to `main`.** Work on a branch off `main` and open a PR.
- **Merging is never unilateral.** Propose the merge and wait for the
  maintainer's explicit OK.

## Releasing

- **Never move `release` without bumping `version` in
  `.claude-plugin/plugin.json`.** Claude Code decides whether to update an
  installed plugin by comparing version strings -- if two refs resolve to the
  same version, it skips the update. An unbumped fast-forward therefore ships
  nothing and **fails silently**, which is worse than not shipping at all.
- **Rollback is forward-only.** To undo a released change: revert it on `main`
  as a normal commit, bump the patch version, tag, release, and fast-forward
  `release` onto it. **Never** point `release` at an older commit and never
  force-push it -- consumers already on the newer version string would not
  downgrade, and the branch would no longer match any released tag.
- **Changelog as-you-go, under `## [Unreleased]`.** Add entries to
  `CHANGELOG.md` under an `## [Unreleased]` heading as changes land. This
  records *what* changed without declaring a version. Never write a
  dated/versioned heading or bump the version file mid-batch -- that
  recreates version drift.
- **A release is one atomic change**, done all together (own commit/PR):
  1. Bump `version` in `.claude-plugin/plugin.json` (semver).
  2. Rename `## [Unreleased]` to `## [x.y.z] - YYYY-MM-DD` and add the
     `[x.y.z]: https://github.com/by-carlos/daikenja/releases/tag/vx.y.z`
     link at the bottom.
  3. Tag `vx.y.z` and cut the matching GitHub release, with the release notes
     body set to that version's actual `CHANGELOG.md` entry content (copied
     in, not a bare "see CHANGELOG.md" pointer) plus a link back to the file
     for full history.
  4. Fast-forward the `release` branch to that tag and push it:
     `git push origin vx.y.z:release`. This is the actual distribution step --
     the marketplace entry in `by-carlos/claude-plugins` points at `release`,
     not `main`, so nothing reaches installers until this push happens.
- **Semver:** a `feat` in the batch means a **minor** bump; only
  `fix`/`docs`/`chore` means a **patch**. Pre-1.0, breaking changes go in a
  minor.
- **Tag per released version** (not per commit, not major-only) -- the
  `CHANGELOG.md` release links assume a tag exists for each version.

## Distribution and branch protection

- **`main` is the working branch, `release` is what users get.** The
  marketplace entry in `by-carlos/claude-plugins` points its plugin source at
  Daikenja's `release` branch, which only ever advances by the fast-forward
  push in step 4 above. A merge to `main` never reaches installers on its own.
- **Both branches are protected on GitHub**, not just documented here:
  `main` requires a pull request, the maintainer's Code Owner approval, and
  passing `gitleaks` and `validate` checks. Repository admins can bypass its
  rules so the maintainer can merge owner-authored PRs, which GitHub does not
  allow them to self-approve. `release` permits normal updates only by
  `@by-carlos`; force pushes and deletion are blocked without bypass so it can
  only move forward. Do not attempt to relax either from an agent session --
  that is a settings change outside this repo's working tree and needs the
  maintainer's explicit sign-off, per the global risk-labeling rule.

## Capturing follow-up work (GitHub issues)

Follow-up work goes to this repo's GitHub issues (`by-carlos/daikenja`).
**Before opening one, read `.claude/reference/github-issues.md`** -- it defines
the required body format (Context / Options / AI prompt), the label rules, the
public-repo scrub list, and when to suggest rather than file. Do not file
without reading it.

- **Tracker & board:** issues live in `by-carlos/daikenja` and go to the
  **"Claude Plugins"** project (project 3). Its priority scale is **P0-P4**.
- **That board is shared across every Claude plugin repo**, not scoped to this
  one -- `by-carlos/claude-plugins` and `by-carlos/plan-staged-rollout` file
  there too. So don't read the board as a view of this repo: filter by the
  Repository field before concluding anything about what is open here, and
  don't assume a neighbouring item is ours.
- **Default to suggesting.** Name the follow-up in one line and offer to open
  an issue; file it once the maintainer agrees.

## Repo conventions

- **Voice.** Anything Daikenja drafts or rewrites follows `docs/voice.md`. That
  document is the source of truth for generated output, and
  `docs/config-contract.md` fixes how a user's own `writing-style.md` layers on
  top of it. Read both before changing either.
- **Ledger format.** `docs/ledger-format.md` defines a parsing contract that
  existing ledger files depend on. Treat the field separator and the split bound
  as frozen unless an issue explicitly scopes a format change.
- **Templates.** Files under `templates/` are copied to a user's machine and
  never edited by the plugin afterwards. Changes there affect only new copies.
- **Shipped vs local skills.** `skills/` holds the skills the plugin ships to
  users. `.claude/` holds guidance for people working on this repo. Never put
  contributor-facing instructions in `skills/`: it would ship them to every
  Daikenja user.
- **Test fixtures.** `tests/fixtures/` holds synthetic inputs that a stage's
  acceptance checks are re-run against. There is no test runner: the fixtures
  are exercised by hand through the skills. Every fixture must stay synthetic,
  with invented projects, invented people and `example.com` links. Never put
  real work content, personal data or organization data there.
