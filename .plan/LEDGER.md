# Replace the ledger with DECISIONS.md, open.md and git history — build ledger

Statuses: `todo → doing → done`, plus `blocked` (waiting on a human or an
external gate — the stage becomes a runbook) and `skipped` (decided against,
one-line reason). Partial completion is a normal, resumable state.

Keep table rows to **ONE line** — detail goes in the notes block below, never
in a table cell. Sessions read the status table plus only the notes blocks of
the stages they `depend` on (the final review stage reads all of it). Update
your stage's row and notes block at the end of every session (Operating
protocol, finish protocol).

## Status

| Stage | Status | Verified | Date | Result |
|---|---|---|---|---|
| S0 Format specs and file templates | done | yes | 2026-11-03 | Shared spec copied byte-identical; open-format.md (199 lines) and both templates landed |
| S1 Config, resolution and reading contracts | todo | — | — | — |
| S2 project-log writes both files | todo | — | — | — |
| S3 Catchup and decisions read git history | todo | — | — | — |
| S4 Gaps, summary, list and sources skills | todo | — | — | — |
| S5 Judgement, thread, meeting-review and other readers | todo | — | — | — |
| S6 setup-project registers git-backed projects only | todo | — | — | — |
| S7 Slack bot reports unreadable project data | todo | — | — | — |
| S8 Migration from the old ledger | todo | — | — | — |
| S9 User guide, README and retiring ledger-format.md | todo | — | — | — |
| SF Plan review | todo | — | — | — |

## Notes

As-built notes, acceptance evidence, gotchas, handoff notes, follow-ups. One
block per stage; sessions read only the blocks of their `depends` stages.

### S0 Format specs and file templates

As built — the shapes later stages consume (all in `docs/open-format.md`):

- **Open item line:** `- <YYYY-MM-DD> -- <@owner> -- <text>`, split on ` -- `
  at most twice; no checkbox, no ID. Date first, then owner (the old
  date/owner order with the ID dropped). `@unassigned` kept for `project-gaps`.
- **`Blocked by:` prefix:** opens the text, names the other item in words, runs
  to the first `. `/end of line. A prefix naming an item no longer in the file
  is read as "names an item no longer open" (it was closed). `project-log`
  offers to drop the prefix when it closes the named item.
- **Items are found by their words**; `project-log` asks on an ambiguous match.
  New items go under the heading; no skill depends on order.
- **Sections:** `## Open items`, `## Context links`, `## Sources` — all three
  required. Context link and source head lines are both `- <label> -- <target>`
  (split once); sources keep the four field lines (`modified:`, `read:`,
  `covers:`, `does not answer:`). Sources content otherwise untouched (#293).
- **Version rule (both files):** newer → readers warn once per run,
  `project-log` refuses the whole batch; **no version line → read as version 1,
  `project-log` adds it in its next approved write**; unparseable line →
  reported, read as 1. The no-line and unparseable cases are an addition beyond
  D-4's wording, needed for hand-made `DECISIONS.md` files.
- **Reading rules** carried over from `ledger-format.md` § Reading rules, minus
  the Changelog/ID/range rules; a missing H2 still reports and asks.
- `templates/open.md` has `{{PROJECT}}` in the H1; `templates/DECISIONS.md` has
  none (shared spec's H1 is `# Decisions`) and is copied as it stands.

Acceptance (run in `../daikenja-s0`):

```
$ cmp docs/decisions-format.md <scratch>/upstream-decisions-format.md
(exit 0, no output)
$ wc -l docs/decisions-format.md docs/open-format.md
  161 docs/decisions-format.md
  199 docs/open-format.md
$ head -n 1 docs/open-format.md templates/open.md templates/DECISIONS.md
==> docs/open-format.md <==
<!-- daikenja-open-format: 1 -->
==> templates/open.md <==
<!-- daikenja-open-format: 1 -->
==> templates/DECISIONS.md <==
<!-- decisions-format: 1 -->
$ python3 tests/check-invariants.py
All invariant checks passed.
```

Upstream fetched with `gh api repos/by-carlos/plan-staged-rollout/contents/skills/staged-rollout/references/decisions-format.md -H "Accept: application/vnd.github.raw"` on 2026-11-03.

Follow-ups (not this stage's): `docs/README.md` does not list the two new specs
yet — S9 (its step on the docs index). `templates/README.md`'s intro still says
`project-log` scaffolds "the ledger"; S9 retires `templates/ledger.md` and can
reword it then. `open-format.md` sits at 199 lines: any addition by a later
stage needs a matching cut to keep Done check 4.

Actuals: 2026-11-03T06:59:45.244Z → 2026-11-03T07:04:03.589Z · 4 min · tokens in=50 out=17740 cache_read=3136960 cache_write=118578 · subagents=0
Artifacts check: match

### S1 Config, resolution and reading contracts
_(empty)_

### S2 project-log writes both files
_(empty)_

### S3 Catchup and decisions read git history
_(empty)_

### S4 Gaps, summary, list and sources skills
_(empty)_

### S5 Judgement, thread, meeting-review and other readers
_(empty)_

### S6 setup-project registers git-backed projects only
_(empty)_

### S7 Slack bot reports unreadable project data
_(empty)_

### S8 Migration from the old ledger
_(empty)_

### S9 User guide, README and retiring ledger-format.md
_(empty)_

<!-- One ### S<N> block per stage. Templates for the states you'll hit:

  done      — paste the real acceptance output, then the as-built summary and
              any gotchas the next stage needs to know.
  actuals   — every session on the stage, whatever its outcome, adds one
              `Actuals:` line (`scripts/effortlog.py usage`, its `line` as is);
              `/plan-close` sums them against the estimates.
  artifacts — the finish protocol adds one `Artifacts check:` line
              (`scripts/artifacts_check.py`, its line as is); a record, never
              a gate — the final review judges each `outside` line.
  doing     — tick the completed Steps checkboxes in the stage file; write a
              handoff note here (what's left, where to resume).
  blocked   — record exactly what human/external action unblocks it, as a
              runbook the human can follow; no faked progress. Where that row
              and runbook get committed depends on whether the stage branch
              exists yet — see PLAN.md, Operating protocol, "Recording a
              block". A mid-stage block lands on the stage branch, so this
              file's copy on the plan branch keeps reading `doing` and the
              block is recorded in BLOCKED.md instead. Discovered mid-run that
              the stage needs a resource only the local machine has? Use the
              literal reason `needs-local` in the Result cell (or the
              BLOCKED.md section) instead of a generic note — see PLAN.md,
              "Recording a block", "The discovered case".
  skipped   — one-line reason; if this stage owned acceptance/verification
              work nothing else covers, say so here too, so SF sees it.
  follow-up — a shortcut or scope-creep item spotted here that became (or
              should become) its own stage; name it so the review stage sees it.
  added     — a stage added after the scaffold opens its notes block with its
              `Added by` line and the scope referee's verdict (PLAN.md,
              "Adding a stage").
-->

### SF Plan review
_(empty)_
