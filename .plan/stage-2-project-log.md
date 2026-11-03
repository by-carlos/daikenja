# S2 — project-log writes both files

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
> Also read S0's and S1's notes blocks, `skills/project-log/SKILL.md`,
> `docs/project-log-reference.md`, `docs/open-format.md` and
> `docs/decisions-format.md`.

## Goal

`project-log` writes the new files: it proposes entries in one batch, the user
approves, and it writes `DECISIONS.md` and `open.md` without IDs, markers or
chains. This is the only skill that writes the ledger, so every other stage's
fixtures can assume its output shape.

## Steps

- [ ] Rewrite `skills/project-log/SKILL.md` and `docs/project-log-reference.md`
  for the new files: one approved batch covering decisions (to `DECISIONS.md`,
  with the shared spec's keep rule and `Paths:` areas) and open items (to
  `open.md`, closed items deleted per D-10); no IDs, no supersession chains.
  When a decision's paths don't say which repository it belongs to, ask which
  repository's `DECISIONS.md` (#292 option 6).
- [ ] Make `project-log`'s batch-and-approve path the one writer that S6
  (seeding) and S8 (migration) call with the entries they produce, so the D-4
  refusal, the home-repository question and the duplicate check apply to them
  too. When the repository already has a `DECISIONS.md` (for example one written
  by plan-staged-rollout), adopt it and add entries to it, never overwrite it.
  When there is no `DECISIONS.md` but an old-format ledger sits at the legacy
  location (D-21), refuse to scaffold a new one over it and point at
  `setup-user`.
- [ ] Add the D-4 refusal: a newer `decisions-format` or `daikenja-open-format`
  version than the plugin knows makes `project-log` refuse to write and ask for a
  plugin update, citing `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md`.
- [ ] State D-6: the skill writes the files and never commits.
- [ ] Keep the skill shorter than today's (constraint 5): move detail to the
  reference doc, cite the format specs instead of restating them.
- [ ] Update the fixtures: `dictated-log-requests.md`, `ledger-relationships.md`,
  `owner-handles.md`. Leave `ledger-backfill.md` as it is until the last steps of S9: invariant
  check (e) replays it, so rewriting it here would break the check early. Add a
  fixture case with `<!-- decisions-format: 2 -->` that must make `project-log`
  refuse, one with an existing `DECISIONS.md` that must be extended, and one with
  an old-format ledger at the legacy location that must make it refuse to
  scaffold. All three are cases in existing fixtures, so `tests/README.md` is
  not edited.
- [ ] Add a `docs/upgrading.md` note only if this stage changes something
  already on a user's disk beyond what S1 recorded, and then its
  `CHANGELOG.md` entry in the same commit; otherwise no changelog entry here,
  S9 writes it (D-14).
- [ ] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass. The size check is the guard for constraint 5: it fails when the
  skill grew past its budget.
- A hand walk of `tests/fixtures/dictated-log-requests.md` produces a batch that
  names both files, with the walk written into the ledger notes.
- A hand walk of the `decisions-format: 2` fixture case ends in a refusal that
  asks for a plugin update and writes nothing.
- A hand walk of the legacy-location case refuses to scaffold a new
  `DECISIONS.md` and points at `setup-user`; a hand walk of the existing
  `DECISIONS.md` case adds entries without overwriting. Both go into the ledger
  notes.

## Artifacts

- `skills/project-log/SKILL.md`
- `docs/project-log-reference.md`
- `tests/fixtures/dictated-log-requests.md`
- `tests/fixtures/ledger-relationships.md`
- `tests/fixtures/owner-handles.md`
- `.plan/LEDGER.md` (this stage's row and notes)
