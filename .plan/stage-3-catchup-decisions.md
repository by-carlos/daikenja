# S3 — Catchup and decisions read git history

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
> Also read S0's and S1's notes blocks, `skills/project-catchup/SKILL.md`,
> `skills/project-decisions/SKILL.md` and `docs/config-schema.md` (the
> `last_checkpoint` map).

## Goal

`project-catchup` reports what changed since the last checkpoint using git
history instead of a ledger Changelog, and `project-decisions` answers from the
current `DECISIONS.md` files with history from git. These two skills are where
D-3 and D-6 become behaviour.

## Steps

- [ ] `skills/project-catchup/SKILL.md`: per registered repository, run
  `git log <sha>..HEAD -- DECISIONS.md .daikenja/open.md` from that repository's
  `last_checkpoint` SHA (D-3). An unresolvable SHA means a first run, and the
  skill says so. A scalar or non-hex `last_checkpoint` (the old UTC timestamp)
  is also a first run: say "checkpoint predates the new ledger" and propose the
  per-repository SHA map. List uncommitted changes to the two files from `git status` as
  "not committed yet" (D-6). Propose advancing each repository's SHA, and write
  only after the user approves.
- [ ] Make the SHA safe to pass to git: validate it is hexadecimal and 7 to 40
  characters long, pass it as a revision argument after the end-of-options marker,
  and never interpolate it into a shell string.
- [ ] `skills/project-decisions/SKILL.md`: answer from the `DECISIONS.md` of every
  registered repository; take history from `git log -p` and from linked issues or
  ADRs; warn once on a newer format version (D-4).
- [ ] Fixtures: retire or replace `broken-supersession.md`; update
  `malformed-ledger.md` and `sample-ledger.md`; add a synthetic fixture
  `tests/fixtures/catchup-git-history.md` for the checkpoint, first-run,
  scalar-timestamp and uncommitted cases (invented project and people, `example.com` links), and list
  it in `tests/README.md`.
- No `CHANGELOG.md` entry here: S9 writes it (D-14).
- [ ] Run `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  and fix anything they flag (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` and `python3 tests/check-skill-size.py`
  both pass.
- A hand walk of `tests/fixtures/catchup-git-history.md` shows three outcomes,
  each written into the ledger notes: changes reported since a SHA, an
  unresolvable SHA reported as a first run, and an uncommitted edit listed as
  "not committed yet". Three is the threshold because they are the three paths
  Done check 7 names; a skill that handles two of them still fails the check.
- A scalar-timestamp `last_checkpoint` in the fixture is reported as "checkpoint
  predates the new ledger" and proposes the per-repository SHA map; the walk goes
  into the ledger notes.
- A shell-metacharacter SHA in the fixture (for example one containing a space or
  a semicolon) is rejected by the validation step, not passed to git.

## Artifacts

- `skills/project-catchup/SKILL.md`
- `skills/project-decisions/SKILL.md`
- `tests/fixtures/catchup-git-history.md`
- `tests/fixtures/broken-supersession.md`
- `tests/fixtures/malformed-ledger.md`
- `tests/fixtures/sample-ledger.md`
- `tests/README.md`
- `.plan/LEDGER.md` (this stage's row and notes)
