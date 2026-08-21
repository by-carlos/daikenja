# AGENTS.md — Daikenja

**Read [`CLAUDE.md`](CLAUDE.md) — it is the single source of project context and
guardrails for this repository, and it applies to you in full.** Despite the
filename it is not Claude-specific: it covers the git and merge conventions, the
release/distribution model, branch protection, and the repo conventions that
govern what ships to users.

This file exists so that agents and review tools which bootstrap from
`AGENTS.md` find that pointer. It is deliberately **not** a second copy — a
duplicated ruleset drifts, and sibling repos in this estate have already been
bitten by exactly that.

## Non-negotiables, restated here so they cannot be missed

These are the rules where *not having read the doc yet* is itself the failure
mode. They are also in `CLAUDE.md`; that copy is authoritative.

- **`main` is the working branch, `release` is what users get.** The marketplace
  entry in `by-carlos/claude-plugins` points at `release`, which only ever
  advances by a fast-forward push of a tag (`git push origin vx.y.z:release`). A
  merge to `main` never reaches installers on its own.
- **Never push directly to `main`, and never merge unilaterally** — work on a
  branch, open a PR, propose the merge and wait for the maintainer's explicit OK.
- **Both branches are protected on GitHub.** `main` requires the maintainer's
  review and passing CI, with an admin bypass for owner-authored PRs because
  GitHub forbids self-approval. `release` permits normal updates only by
  `@by-carlos`; nobody can force-push or delete it. **Do not attempt to relax
  either from an agent session** — that is a settings change outside the
  working tree and needs the maintainer's explicit sign-off under the global
  risk-labeling rule.
- **`skills/` ships to users; `.claude/` is for people working on this repo.
  Never put contributor-facing instructions in `skills/`** — it would ship them
  to every Daikenja user.
- **`templates/` files are copied to a user's machine and never edited by the
  plugin afterwards.** A change there affects only new copies, never existing
  installs.
- **`docs/ledger-format.md` defines a parsing contract that existing ledger
  files depend on.** Treat the field separator and the split bound as **frozen**
  unless an issue explicitly scopes a format change.
- **Test fixtures must stay synthetic.** `tests/fixtures/` uses invented
  projects, invented people, and `example.com` links. **Never** put real work
  content, personal data, or organization data there. There is no test runner —
  fixtures are exercised by hand through the skills.
- **Voice is contractual.** Anything Daikenja drafts or rewrites follows
  `docs/voice.md`, and `docs/config-contract.md` fixes how a user's own
  `writing-style.md` layers on top. Read both before changing either.
- **Never move `release` without bumping `version` in
  `.claude-plugin/plugin.json`.** Claude Code compares version strings to decide
  whether to update an installed plugin, so an unbumped fast-forward ships
  nothing and **fails silently**.
- **Rollback is forward-only.** Revert on `main`, bump the patch, tag, release,
  fast-forward. **Never** point `release` at an older commit and never
  force-push it — consumers on the newer version string would not downgrade.
- **Changelog as-you-go, under `## [Unreleased]`.** Never write a
  dated/versioned heading or bump the version file mid-batch — that recreates
  version drift.
- **Upgrade notes as-you-go too, under `## [Unreleased]` in
  `docs/upgrading.md`** — but only when the change touches something already on
  a user's disk (the `daikenja.yaml` schema, the ledger grammar or location, a
  skill name, any path the plugin reads). Most changes add nothing there. A
  release only promotes that heading; it never writes the note.
- **Before filing an issue, read `.claude/reference/github-issues.md`** — it
  defines the required body format, label rules, and when to suggest rather than
  file. Default to suggesting.

Everything else — and the reasoning behind these — is in
[`CLAUDE.md`](CLAUDE.md).
