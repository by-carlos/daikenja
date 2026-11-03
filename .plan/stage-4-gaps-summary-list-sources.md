# S4 — Gaps, summary, list and sources skills

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
> Also read S0's and S1's notes blocks, `docs/open-format.md`, `docs/reading.md`
> and the four skills named below.

## Goal

Move the four skills that read the open items and the project list to the new
files: `project-gaps` reads `open.md` and annotates `Blocked by:`, `project-summary`
and `project-sources` read the new sections, and `project-list` drops pathless
rows. Together with S2, S3 and S5 this makes every ledger-reading skill speak the
new layout.

## Steps

- [ ] `skills/project-gaps/SKILL.md`: read `.daikenja/open.md`, annotate items
  carrying a `Blocked by:` prefix (D-2), and take staleness from the date raised.
- [ ] `skills/project-summary/SKILL.md` and `skills/project-list/SKILL.md`: read
  `DECISIONS.md` and `open.md`; `project-list` has no pathless rows and reports a
  leftover `paths: []` project as "needs migration" (D-21).
- [ ] `skills/project-sources/SKILL.md`: the Sources section now lives in
  `open.md`. Do not rework Sources itself: that is by-carlos/daikenja#293 and out
  of scope.
- [ ] Multi-repository projects: each skill reads every registered repository's
  `DECISIONS.md`, and a newer format version makes it warn once and still read
  (D-4).
- [ ] Update `tests/fixtures/sources-ledger.md` and any fixture citing these
  skills; add the two-repository project as a case in an existing fixture. No
  fixture is added or removed, so `tests/README.md` is not edited.
- No `CHANGELOG.md` entry here: S9 writes it (D-14).
- [ ] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass.
- A hand walk of a two-repository synthetic project (written into the fixtures)
  shows both repositories' `DECISIONS.md` read and one `Blocked by:` item
  annotated; the walk goes into the ledger notes. Two repositories is the
  smallest case that tells reading every repository apart from reading only the
  first.

## Artifacts

- `skills/project-gaps/SKILL.md`
- `skills/project-summary/SKILL.md`
- `skills/project-list/SKILL.md`
- `skills/project-sources/SKILL.md`
- `tests/fixtures/sources-ledger.md`
- `.plan/LEDGER.md` (this stage's row and notes)
