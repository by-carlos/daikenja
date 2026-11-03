# S10 — Fix: align the migration batch exemption

Issue: by-carlos/daikenja#292

<!-- This stage's flags (depends / mode / exec / model / effort / gate /
estimate) live ONLY in the PLAN.md stage index — the single authoritative home. Do not restate them
here; a copy is what drifts. The `Issue:` line above is not a flag — it only
records which issue this stage came from. `/stage-run` prints it, and
`/plan-close` writes `Closes <ref>` (or `Refs`) for it into the final PR body. It is
optional; a stage without it runs unchanged. -->

> First read `.plan/PLAN.md` (Requirements › Outcome and Out of scope, Frozen
> decisions D-11, D-20, D-21, D-22, Operating protocol) and `.plan/LEDGER.md`:
> the S8 notes block and SF's `#### Loose ends` items 1-4. Follow the protocol,
> including the finish protocol: this stage ends when its Acceptance passes.
> Also read `docs/ledger-migration.md` (§ The proposal, § Writing, in order),
> `skills/project-log/SKILL.md` Step 2, `docs/project-log-reference.md` § A
> batch handed over by another skill, `docs/config-resolution.md` § Legacy
> keys and unmigrated ledgers, and `docs/config-writers.md`.

## Goal

A fix, not a feature: it repairs #292's "When this closes" item 5 and Done
check 6 (a pathless ledger migrates). `docs/ledger-migration.md` says the
migration's batch names its targets by absolute path and is exempt from both
the unmigrated-ledger refusal and the `paths: []` stop. `project-log`'s own
text exempts it from the first only, and the config edit runs after
`project-log` writes, so a no-folder project's entry still reads `paths: []`
when `project-log` resolves it: followed as written, `project-log` stops and
the migration ends after `git init` and the backup copy. Make the three texts
say the same thing, and correct three statements in the config docs that
still describe the migration wrongly.

## Steps

- [ ] `skills/project-log/SKILL.md` Step 2: the migration's own batch (per
  `project-log-reference.md` § A batch handed over by another skill) skips
  config resolution -- it names its targets by absolute path -- so neither
  item 2's no-paths stop nor item 4's `paths: []` and unmigrated-ledger
  refusals apply to it. Say it once, where the exception already sits; keep
  every other run's behaviour unchanged. The skill must not grow past
  `tests/check-skill-size.py`.
- [ ] `docs/project-log-reference.md` § A batch handed over by another skill:
  the same exemption, worded to match `docs/ledger-migration.md` § The
  proposal ("the refusals for an unmigrated ledger and for an entry with no
  paths do not apply to this batch, and every other check does").
- [ ] `docs/config-resolution.md` § Legacy keys: "the migration in
  `setup-user`" -> the migration in `setup-project`, reached from `setup-user`.
- [ ] `docs/config-writers.md`: the card row names the migration's card move
  as the one exception to "never touched"; the `daikenja.yaml` projects row
  names the migration's edit (dropping `ledger:`, replacing a timestamp
  `last_checkpoint`, setting `paths` for a no-folder project) and the backup
  rename; the reverse index lists `project-catchup` under § Who writes what.
- [ ] Re-walk `tests/fixtures/ledger-migration.md`'s no-folder input against the
  changed `project-log` text and record the result in the ledger notes; edit
  the fixture only if its expected output changes.
- [ ] `CHANGELOG.md` `## [Unreleased]` › Changed (or Fixed): one line, in user
  words. No `docs/upgrading.md` entry -- nothing on a user's disk changes.
- [ ] Run `python3 tests/check-invariants.py` and `python3
  tests/check-skill-size.py` (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python3 tests/check-invariants.py` passes.
- `python3 tests/check-skill-size.py` passes.
- `git grep -n "migration in .setup-user" -- docs` prints nothing.
- `skills/project-log/SKILL.md`, `docs/project-log-reference.md` and
  `docs/ledger-migration.md` each state that the migration's batch is exempt
  from both the unmigrated-ledger refusal and the no-paths stop -- quote the
  three sentences in the ledger notes.
- The no-folder walk of `tests/fixtures/ledger-migration.md` reaches
  `project-log` writing both files, followed through the skill's own text --
  the walk goes in the ledger notes.

## Artifacts

- `skills/project-log/SKILL.md`
- `docs/project-log-reference.md`
- `docs/config-resolution.md`
- `docs/config-writers.md`
- `tests/fixtures/ledger-migration.md` (only if its expected output changes)
- `CHANGELOG.md`
- `.plan/LEDGER.md` (this stage's row and notes)
