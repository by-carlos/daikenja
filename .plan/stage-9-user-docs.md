# S9 — User guide, README and retiring ledger-format.md

Issue: by-carlos/daikenja#292

<!-- This stage's flags (depends / mode / exec / model / effort / gate /
estimate) live ONLY in the PLAN.md stage index — the single authoritative home. Do not restate them
here; a copy is what drifts. The `Issue:` line above is not a flag — it only
records which issue this stage came from. `/stage-run` prints it, and
`/plan-close` writes `Closes <ref>` (or `Refs`) for it into the final PR body. It is
optional; a stage without it runs unchanged. -->

> First read `.plan/PLAN.md` (Requirements › Outcome and Out of scope, Frozen
> decisions, Operating protocol) and `.plan/LEDGER.md`. Follow the protocol,
> including the finish protocol: this stage ends when its Acceptance passes.
> Also read the notes blocks of S2 to S8 (the as-built behaviour you document),
> `CONTRIBUTING.md` § User documentation, `tests/check-invariants.py` (check (e))
> and `tests/check-reference-drift.py`.

## Goal

The user-facing documentation describes the ledger as built: `DECISIONS.md` plus
`open.md`, git as the history, no pathless projects, and the migration path.
`CLAUDE.md` says a user-visible change updates the matching guide page in the same
PR, so this stage catches whatever the skill stages did not cover and removes the
last pathless claims. Its last steps then delete `docs/ledger-format.md` and
everything that still points at it (D-5): any earlier deletion would break the
citations and invariant check (e) that S2 to S8 still rely on.

## Steps

- [ ] `README.md`: remove the pathless claims and say plainly that projects
  without a folder are gone (D-15); keep it a landing page.
- [ ] `docs/guide/ledger.md`, `your-data.md`, `install.md`, `faq.md`, `commands.md`,
  `why.md`, `slack-bot.md`, `reviewing.md` and `writing.md`: describe the new
  files, where they live, that `project-log` never commits (D-6), how catchup uses
  git, the migration, and the version warning (D-4). The word "ledger" stays
  (D-7). `slack-bot.md` also carries the operator sequence after an upgrade:
  update the plugin, run `setup-user`, pull the bot checkout, restart the bot,
  run `--check` (the bot's Python loads at startup, the skills update at once).
- [ ] `docs/diagrams/how-it-works.svg` and `docs/diagrams/where-data-lives.svg`:
  redraw for the new file locations.
- [ ] Follow `CONTRIBUTING.md` § User documentation for page conventions.
- [ ] Write the `CHANGELOG.md` `## [Unreleased]` entry set for S0, S2–S7 and
  this stage, from their ledger notes (D-14); S1 and S8 wrote their own with
  their upgrade notes. Say plainly that pathless projects are gone (D-15).
- [ ] Run `python3 tests/check-invariants.py` and fix anything it flags,
  including its link check (D-16).

Last steps, in this order, once the guide pages no longer link the old spec:

- [ ] Delete `docs/ledger-format.md` and `templates/ledger.md` (S6 left the
  template in place because the old spec still links it).
- [ ] De-link what still points at them: `docs/upgrading.md` (the 0.3.0 section,
  as plain code text, since that note is released history), `docs/README.md` and
  `AGENTS.md`.
- [ ] `tests/check-invariants.py`: remove or replace check (e) (the backfill
  replay). A mechanical check worth keeping is that `docs/decisions-format.md`
  starts with its version line and `templates/open.md` starts with its own;
  update the docstring either way.
- [ ] `tests/check-reference-drift.py`: update the docstring example that names
  the old file.
- [ ] Remove orphaned fixtures (for example `ledger-backfill.md`) and their lines
  in `tests/README.md`.
- [ ] `CONTRIBUTING.md` and the repository `CLAUDE.md`: the "Ledger format" bullet
  now points at `docs/decisions-format.md` and `docs/open-format.md`, and the
  frozen-grammar rule covers the version line and the item line.
- [ ] Run `python3 tests/check-invariants.py` (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` passes, including check (j), the link
  check, so no guide page links a removed file.
- `git grep -nE "pathless|ledgers/" -- README.md docs/guide` returns nothing. The
  pattern is the two strings that mark the old model, so any hit is a stale
  claim.
- Done checks 1, 4 and 5 run and pass, output pasted into the ledger notes:
  `python3 tests/check-invariants.py`; `test ! -e docs/ledger-format.md` plus
  `wc -l docs/decisions-format.md docs/open-format.md` (each under 200);
  check 5's `git grep` exactly as `PLAN.md` writes it (it excludes `.plan/`,
  `docs/ledger-migration.md` and the migration fixtures, and allows the D-21
  legacy sentences).
- `git grep -n "ledger-format.md" -- . ":!.plan" ":!CHANGELOG.md" ":!docs/upgrading.md"`
  returns nothing. It deliberately does not exclude `docs/ledger-migration.md`, which
  must not cite the deleted spec. Any hit is a citation that would now dangle.
- `test ! -e templates/ledger.md` succeeds.

## Artifacts

- `README.md`
- `docs/guide/ledger.md`
- `docs/guide/your-data.md`
- `docs/guide/install.md`
- `docs/guide/faq.md`
- `docs/guide/commands.md`
- `docs/guide/why.md`
- `docs/guide/slack-bot.md`
- `docs/guide/reviewing.md`
- `docs/guide/writing.md`
- `docs/diagrams/how-it-works.svg`
- `docs/diagrams/where-data-lives.svg`
- `docs/ledger-format.md` (deleted)
- `templates/ledger.md` (deleted)
- `docs/upgrading.md`
- `docs/README.md`
- `AGENTS.md`
- `tests/check-invariants.py`
- `tests/check-reference-drift.py`
- `tests/fixtures/ledger-backfill.md` (and any other orphaned fixture)
- `tests/README.md`
- `CONTRIBUTING.md`
- `CLAUDE.md`
- `CHANGELOG.md`
- `.plan/LEDGER.md` (this stage's row and notes)
