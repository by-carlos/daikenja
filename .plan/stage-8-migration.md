# S8 — Migration from the old ledger

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
> Also read S6's notes block, `skills/setup-project/SKILL.md`,
> `skills/setup-user/SKILL.md`, `docs/ledger-format.md` (the old grammar you
> migrate from; it still exists until the last steps of S9, so restate what the
> migration needs in `docs/ledger-migration.md` instead of citing it), S2's notes
> block (the `project-log` write path) and the S1 section of `docs/upgrading.md`.

## Goal

Existing ledgers, including pathless ones, migrate to `DECISIONS.md` and `open.md`
with the user's approval and a dated backup (D-11). Without this stage the format
swap strands every current user's data.

## Steps

- [ ] Write `docs/ledger-migration.md` (D-20). It is self-contained: it restates
  the old-format reading rules it needs (IDs, supersession chains, malformed
  tails) and cites nothing in `docs/ledger-format.md`, which is deleted in the
  last steps of S9. The procedure: follow supersession chains so only in-force
  decisions become `DECISIONS.md` entries, with `Imposed` folded into the entry's
  why clause (D-2); drop superseded entries (D-11); move open items to `open.md`,
  keeping `Blocked by:` and resolving any `Contradicts` (D-2); carry Context links
  and Sources over; write the backup `ledger.<YYYY-MM-DD>.bak.md` beside the old
  ledger. Migration is one more seeding source: the entries it produces are
  written through `project-log`'s batch-and-approve path (S2), shown first, and
  nothing is written until the user approves. When the target repository already
  has a `DECISIONS.md`, it is adopted and entries are added to it, never
  overwritten.
- [ ] The same approval covers the per-project config edit: set `paths` (home
  first, D-8), drop the `ledger:` key and a scalar `last_checkpoint`, and move the
  project card to `<home>/.daikenja/project.md`. `setup-project` itself keeps only
  that config edit, the dated backup copy and the card move; the entry writes go
  through `project-log`.
- [ ] Pathless ledger (D-22): ask for the target folder and suggest a sibling of a
  registered root named after the project key, but run `git -C <target> rev-parse
  --show-toplevel` first. If the target is inside a repository, name that
  repository and ask. The default is a new folder outside any repository, with
  `git init`. The approval line states that the content moves from a private
  folder into a repository.
- [ ] `skills/setup-project/SKILL.md`: add the migration branch, which runs the
  procedure per project. `skills/setup-user/SKILL.md`: the upgrade branch hands
  off to it. If the additions break `tests/check-skill-size.py`, move detail into
  `docs/ledger-migration.md` and revisit D-20 in `PLAN.md`.
- [ ] `docs/upgrading.md` `## [Unreleased]`: add the ledger-migration part, in the
  file's five-part shape, extending S1's section. Include the operator sequence
  for a Slack bot install: update the plugin, run `setup-user`, pull the bot
  checkout, restart the bot, run `--check`.
- [ ] Fixtures: a synthetic old ledger, a synthetic pathless one, a pathless
  config entry, a project card beside a non-default ledger location, and a
  repository that already has a `DECISIONS.md` (for example
  `tests/fixtures/ledger-migration.md`; invented projects and people,
  `example.com` links), update `tests/fixtures/setup-user-upgrade.md`, and list
  the new fixture in `tests/README.md`.
- [ ] Add a `CHANGELOG.md` entry under `## [Unreleased]`.
- [ ] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- In a scratch git folder, walk the procedure over the synthetic ledger and over
  the pathless one. Each ends with a `DECISIONS.md`, a `.daikenja/open.md` and a
  `ledger.<date>.bak.md` beside the old ledger; paste the resulting files into the
  ledger notes. Two inputs because Done check 6 names both.
- A superseded entry in the synthetic ledger is absent from `DECISIONS.md` and
  present in the backup (`git grep` or `grep` on both files, output in the notes).
- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass.
- The pathless config entry fixture ends with `paths` set, `ledger:` and a scalar
  `last_checkpoint` gone, and the card at `<home>/.daikenja/project.md`; the
  non-default-location card fixture ends the same way and the old ledger is not
  stranded. Output goes into the ledger notes.
- The existing-`DECISIONS.md` fixture ends with the migrated entries added to the
  file and none of its prior entries lost.
- A pathless walk whose suggested target is inside an existing repository names
  that repository and asks instead of writing; a walk with no such repository
  defaults to a new folder with `git init`. The approval line in both says the
  content moves from a private folder into a repository.
- `grep -n "ledger-format" docs/ledger-migration.md` returns nothing.

## Artifacts

- `docs/ledger-migration.md`
- `skills/setup-project/SKILL.md`
- `skills/setup-user/SKILL.md`
- `docs/upgrading.md`
- `tests/fixtures/ledger-migration.md`
- `tests/fixtures/setup-user-upgrade.md`
- `tests/README.md`
- `CHANGELOG.md`
- `.plan/LEDGER.md` (this stage's row and notes)
