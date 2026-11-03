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
| S0 Format specs and file templates | todo | — | — | — |
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
_(empty)_

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
