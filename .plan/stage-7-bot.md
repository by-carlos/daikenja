# S7 — Slack bot reports unreadable project data

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
> Also read S5's notes block (the fixed "project data unreadable" token),
> `bot/README.md`, `bot/daikenja_bot/prompts.py` (`UNAVAILABLE_TOKEN` and
> `extract_output`) and `bot/daikenja_bot/runner.py`.

## Goal

The Slack bot never posts a normal-looking verdict for a project whose data it
cannot read. The bot prompts name no ledger paths and the section names stay (D-7),
so the skills resolve the files; what the bot needs is to recognise the fixed
token S5 added for "project data unreadable" (needs migration, newer format
version), log which project and why, and post one fixed line. The bot stays
read-only and dependency-free (D-17): it reads current files only and never calls
git.

## Steps

- [ ] `bot/daikenja_bot/prompts.py` and `runner.py`: recognise S5's token the way
  `UNAVAILABLE_TOKEN` is recognised, before `extract_output` discards everything
  outside the delimiters. On a match, write the project and the reason to the bot
  log and post one fixed line saying the project data needs attention (no
  "run setup-user" text that the channel cannot act on).
- [ ] `--check`: list the configured projects that are not yet on the new format,
  if that can be done without a git call; if it cannot, say so in this stage's
  ledger notes and leave `--check` as it is.
- [ ] Add a test per state in `bot/tests/` (needs migration, newer format
  version) that asserts the fixed line is posted and the log line is written.
- [ ] Edit the comments, docstrings and `bot/README.md` that still describe the
  old ledger file: `commands.py`, `config.py` (comments), `runner.py`
  (docstring), `bot/README.md`, and any `bot/tests/` file that cites it. Keep the
  user-facing word "ledger" (D-7).
- [ ] Add nothing to `bot/requirements.txt`, and add no code path that calls git
  (D-17).
- No `CHANGELOG.md` entry here: S9 writes it (D-14).
- [ ] Run `python3 tests/check-invariants.py` (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `python -m pytest bot/tests` passes; the output (with the test count) goes into
  the ledger notes.
- `python3 tests/check-invariants.py` passes.
- `git diff --stat origin/feat/292-replace-ledger-decisions-md-open -- bot/requirements.txt`
  prints nothing, and `git grep -nE "subprocess|git " -- bot/daikenja_bot` shows
  no new call into git. Both checks detect a dependency or a git call slipping in,
  which the read-only design (D-17) forbids.

## Artifacts

- `bot/daikenja_bot/prompts.py`
- `bot/daikenja_bot/commands.py`
- `bot/daikenja_bot/config.py`
- `bot/daikenja_bot/runner.py`
- `bot/daikenja_bot/__main__.py`
- `bot/README.md`
- `bot/tests/test_prompts.py` (and any other test under `bot/tests/` that cites the ledger or the new token)
- `.plan/LEDGER.md` (this stage's row and notes)
