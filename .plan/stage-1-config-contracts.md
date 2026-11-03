# S1 — Config, resolution and reading contracts

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
> Also read S0's notes block in the ledger, `docs/open-format.md` and
> `docs/decisions-format.md` (the file names and headings you cite), and the
> existing `docs/upgrading.md` to match its five-part shape.

## Goal

Change the config and reading contracts to the new file layout: where
`DECISIONS.md` and `open.md` are found, what `last_checkpoint` holds, which keys
are gone. Every skill stage (S2 to S6) cites these docs instead of restating
them, so they must be settled before any skill is rewritten.

## Steps

- [ ] `docs/config-schema.md`: remove the `ledger:` key, the `paths: []` shape
  and the pathless example (D-9, D-21); make `last_checkpoint` a map from
  repository path to commit SHA (D-3); state that home is the first entry of
  `paths` (D-8). Update its `Depends-on` reverse index if headings change.
- [ ] `docs/config-resolution.md`: replace "Finding the ledger" with finding
  `DECISIONS.md` (every registered path) and `.daikenja/open.md` (home only);
  describe multi-repository reading and the D-21 handling of a leftover
  `ledger:` key, a `paths: []` project, and a project with no `DECISIONS.md`
  but an old-format ledger at the legacy location (`.daikenja/ledger.md`, no key
  needed): readers say "needs migration" in one line pointing at `setup-user`,
  and `project-log` refuses to scaffold over it (S2 implements the refusal).
- [ ] `docs/config-writers.md`, `docs/config-versioning.md` (if it mentions the
  ledger), `docs/reading.md` (the per-skill reading contract), `docs/project-card.md`,
  `docs/future-work.md` (drop the pathless limitations) and the `docs/README.md`
  index.
- [ ] `templates/daikenja.yaml`: remove `ledger:` and any pathless example, show
  `last_checkpoint` as a path-to-SHA map.
- [ ] `docs/upgrading.md` `## [Unreleased]`: the config part, in the file's
  five-part shape: `ledger:` key removed, `paths: []` removed, `last_checkpoint`
  timestamp replaced by a per-repository SHA map. Say that those removals (the
  `ledger:` key, `paths: []`, a scalar `last_checkpoint`) happen inside the
  migration, in the same approval as the file move (S8), not as a standalone
  `setup-user` edit. S8 extends this section with the migration part.
- [ ] Update the fixtures that cite changed headings (`tests/fixtures/ledger-location.md`,
  `project-resolution.md`, `project-card.md` as needed), and add a
  default-location case to `tests/fixtures/ledger-location.md`: no
  `DECISIONS.md` plus an old-format ledger at `.daikenja/ledger.md` reads as
  "needs migration". No fixture is added or removed, so `tests/README.md` is
  not edited.
- [ ] Add a `CHANGELOG.md` entry under `## [Unreleased]`, saying plainly that
  pathless projects are gone (D-15).
- [ ] Run `python3 tests/check-invariants.py` and fix anything it flags (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` passes.
- `git grep -n "Finding the ledger" -- . ":!.plan" ":!CHANGELOG.md" ":!docs/upgrading.md"`
  returns nothing. The pattern is the old heading itself, so any hit is a
  citation that was not updated.
- `git grep -nE "ledger:|paths: \[\]" -- docs/config-schema.md docs/config-resolution.md templates/daikenja.yaml`
  shows no live use of either key (mentions only inside a D-21 legacy-handling
  sentence are allowed, and are listed in the ledger notes). The path list is
  already scoped and excludes `.plan/`.
- A hand walk of `tests/fixtures/project-resolution.md` against the new
  resolution rules, with the result written into the ledger notes.
- A hand walk of the default-location case in `tests/fixtures/ledger-location.md`
  ends in a one-line "needs migration" pointing at `setup-user`, written into
  the ledger notes.

## Artifacts

- `docs/config-schema.md`
- `docs/config-resolution.md`
- `docs/config-writers.md`
- `docs/config-versioning.md`
- `docs/reading.md`
- `docs/project-card.md`
- `docs/future-work.md`
- `docs/README.md`
- `docs/upgrading.md`
- `templates/daikenja.yaml`
- `tests/fixtures/ledger-location.md`
- `tests/fixtures/project-resolution.md`
- `tests/fixtures/project-card.md`
- `CHANGELOG.md`
- `.plan/LEDGER.md` (this stage's row and notes)
