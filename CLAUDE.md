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

## Filing issues

Follow-up work goes to this repo's GitHub issues (`by-carlos/daikenja`).
**Before opening one, read `.claude/reference/github-issues.md`** -- it defines
the required body format (Context / Options / AI prompt), the label rules, and
when to suggest rather than file. Do not file without reading it.

Default to suggesting. Name the follow-up in one line and offer to open an
issue; file it once the maintainer agrees.

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
