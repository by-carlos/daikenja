# S0 — Format specs and file templates

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
> Also read `.plan/decisions-format.md` (the spec you copy), and the current
> `docs/ledger-format.md` and `templates/ledger.md` for the item shapes you
> replace.

## Goal

Land the two format specs and the two empty-file templates every later stage
cites: `docs/decisions-format.md` (the byte-identical shared spec, D-5),
`docs/open-format.md` (Daikenja's own `open.md` grammar and the version rule for
both files, D-2, D-4, D-10) and the matching `templates/` files. S1 to S6 all
consume these file names and spec headings, so nothing else can start before
this stage.

## Steps

- [x] Copy `.plan/decisions-format.md` to `docs/decisions-format.md`
  byte-identical (it is itself the upstream file). Verify against upstream with
  `gh api repos/by-carlos/plan-staged-rollout/contents/skills/staged-rollout/references/decisions-format.md -H "Accept: application/vnd.github.raw"`
  written to a scratch file, then `cmp` the two.
- [x] Write `docs/open-format.md`: first line `<!-- daikenja-open-format: 1 -->`;
  where the file lives (`.daikenja/open.md` in the home repository, D-8, D-9);
  the item line grammar (owner, date raised `YYYY-MM-DD`, text, and the optional
  `Blocked by: <other item in words>` prefix, D-2); closing an item deletes its
  line (D-10); the "Context links" and "Sources" sections; no Changelog section
  and no IDs; the format-version rule for both files (D-4: reading skills read
  and warn once, `project-log` refuses and asks for a plugin update). Add no
  `Depends-on (reverse index ...)` block: no skill section cites the file yet.
  Keep it under 200 lines.
- [x] Write `templates/open.md`: an empty `open.md` with the version line and the
  sections from the spec.
- [x] Write `templates/DECISIONS.md`: an empty file with
  `<!-- decisions-format: 1 -->` and the shape `docs/decisions-format.md` defines.
  Leave `templates/ledger.md` in place (S9 removes it).
- [x] Update `templates/README.md` to list the two new templates.
- No `CHANGELOG.md` entry here: S9 writes the entry set for S0, S2–S7 and S9
  (D-14). This stage touches nothing on a user's disk, so `docs/upgrading.md`
  gets no note.
- [x] Run `python3 tests/check-invariants.py` and fix anything it flags (D-16).

<!-- Checkboxes are the resume mechanism: a session that stops mid-stage marks
the row `doing`, ticks the boxes it finished, and writes a handoff note in the
ledger. Re-running the stage resumes from the first unticked box. -->

## Acceptance

- `cmp docs/decisions-format.md <scratch copy of the upstream file>` prints
  nothing. Byte-identical is the threshold because the file is the contract
  between two plugins; one differing byte is a different contract.
- `wc -l docs/decisions-format.md docs/open-format.md` shows each under 200. The
  threshold is #292's target against the 799 lines of `docs/ledger-format.md`
  today; the check detects a spec that grew back.
- `head -n 1 docs/open-format.md templates/open.md templates/DECISIONS.md` shows
  `<!-- daikenja-open-format: 1 -->`, `<!-- daikenja-open-format: 1 -->` and
  `<!-- decisions-format: 1 -->` respectively.
- `python3 tests/check-invariants.py` passes.

## Artifacts

- `docs/decisions-format.md`
- `docs/open-format.md`
- `templates/open.md`
- `templates/DECISIONS.md`
- `templates/README.md`
- `.plan/LEDGER.md` (this stage's row and notes)
