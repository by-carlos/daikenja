# S5 — Judgement, thread, meeting-review and other readers

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
> Also read S0's and S1's notes blocks, `docs/reading.md`, `docs/response-format.md`
> and `docs/preflight-reference.md`.

## Goal

Move the remaining ledger readers to `DECISIONS.md` and `open.md`, and give the
headless `thread` and `judgement` output paths a fixed token for "project data
unreadable" (needs migration, newer format version), which S7 makes the Slack bot
recognise. `judgement` carries the most references to the old format (55
mentions), so it is the bulk of the work.

## Steps

- [x] `skills/judgement/SKILL.md`: check claims against the current
  `DECISIONS.md` of every registered repository and against `open.md`; there are
  no IDs to cite, so cite the entry by its words and its repository.
- [x] `skills/thread/SKILL.md`, `skills/meeting-review/SKILL.md` (it proposes
  entries in the new shapes for `project-log` to write: decisions as
  `DECISIONS.md` entries, open items with owner and date, no IDs or markers),
  `skills/preflight/SKILL.md`, `skills/remember-persona/SKILL.md`,
  `skills/self-review/SKILL.md` and `skills/learn-voice/SKILL.md` (one mention).
- [x] `docs/response-format.md` and `docs/preflight-reference.md`.
- [x] Keep the user-facing word "ledger" (D-7); output section names stay as
  they are (D-7), so there is no list of relayed section names to hand to S7.
- [x] In the `thread` and `judgement` headless output paths, emit a fixed token
  for "project data unreadable" when the project needs migration (D-21) or its
  files carry a newer format version (D-4), instead of a normal-looking verdict.
  Record the token's exact text in this stage's ledger notes, because S7
  consumes it.
- [x] Update `tests/fixtures/judgement.md`, `sample-thread*.md`,
  `sample-transcript.md` and `sample-drafts-preflight.md`. No fixture is added or
  removed, so `tests/README.md` is not edited.
- No `CHANGELOG.md` entry here: S9 writes it (D-14).
- [x] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass.
- A hand walk of `tests/fixtures/judgement.md` against a synthetic
  `DECISIONS.md` (invented project, invented people) gives a verdict that cites an
  entry without an ID; the walk goes into the ledger notes.
- A hand walk of `thread` and of `judgement` over a project that needs migration,
  and over one with a newer format version, ends in the fixed token and in no
  verdict; the walks and the token text go into the ledger notes. S7 depends on
  the token, so a missing token fails the stage.

## Artifacts

- `skills/judgement/SKILL.md`
- `skills/thread/SKILL.md`
- `skills/meeting-review/SKILL.md`
- `skills/preflight/SKILL.md`
- `skills/remember-persona/SKILL.md`
- `skills/self-review/SKILL.md`
- `skills/learn-voice/SKILL.md`
- `docs/response-format.md`
- `docs/preflight-reference.md`
- `tests/fixtures/judgement.md`
- `tests/fixtures/sample-thread.md` (and the other `sample-thread*.md` fixtures)
- `tests/fixtures/sample-transcript.md`
- `tests/fixtures/sample-drafts-preflight.md`
- `.plan/LEDGER.md` (this stage's row and notes)
