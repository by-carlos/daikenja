# S6 — setup-project registers git-backed projects only

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
> Also read S2's notes block (the `project-log` batch-and-approve path this stage
> calls), `skills/setup-project/SKILL.md`, `templates/README.md` and
> `templates/project.md`.

## Goal

`setup-project` registers only git-backed projects, asks which repository is home,
and has the new files seeded from the new templates through `project-log`, the
ledger's one writer. S8 builds the migration branch in the same skill file, so
this stage settles the registration flow first.

## Steps

- [ ] `skills/setup-project/SKILL.md`: remove the pathless branch; for a plain
  folder meant for non-code work, offer `git init`; ask which registered
  repository is home and write it first in `paths` (D-8); no `ledger:` key is
  written (D-9). `setup-project` itself keeps only the config entry and (S8) the
  dated backup copy and the card move. Seeding produces entries from
  `templates/DECISIONS.md` and `templates/open.md`, and those are written through
  `project-log`'s batch-and-approve path, never directly. When the repository
  already has a `DECISIONS.md` (for example one written by plan-staged-rollout),
  adopt it and add entries to it, never overwrite it.
- [ ] Update `templates/README.md`, and `templates/project.md` if it names the
  ledger. Do not delete `templates/ledger.md`: `docs/ledger-format.md` still
  links it, and the last steps of S9 remove both.
- [ ] Update `tests/fixtures/setup-project-seed.md` (add a case for a repository
  that already has a `DECISIONS.md`) and, if it still cites setup-project,
  `tests/fixtures/ledger-location.md`. No fixture is added or removed, so
  `tests/README.md` is not edited.
- [ ] Record in this stage's ledger notes, for S9's changelog entry, that
  pathless projects can no longer be registered (D-15). No `CHANGELOG.md`
  entry here (D-14).
- [ ] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass.
- A hand walk of `tests/fixtures/setup-project-seed.md` covers three cases, each
  recorded in the ledger notes: a code repository, a multi-repository project
  (home is asked and written first) and a non-code folder (`git init` offered).
  Three cases because each takes a different branch of the flow.
- A hand walk of the `setup-project-seed.md` case for a repository that already
  has a `DECISIONS.md` adds entries to it through `project-log` and overwrites
  nothing; the walk goes into the ledger notes.

## Artifacts

- `skills/setup-project/SKILL.md`
- `templates/README.md`
- `templates/project.md`
- `tests/fixtures/setup-project-seed.md`
- `tests/fixtures/ledger-location.md`
- `.plan/LEDGER.md` (this stage's row and notes)
