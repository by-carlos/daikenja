# Harbor ledger

<!--
Fixture: deliberately broken ledger, in the two-file shape. Synthetic content.

`DECISIONS.md` is well formed. `.daikenja/open.md` has two defects, both of
which `project-log` must report rather than write over, and every reading skill
must report rather than skip:

1. The `## Context links` heading is misspelled `## Context link`, so a
   required section is missing by exact-heading lookup.
2. The "Decide whether the 25% step waits for finance" item has two fields
   instead of three -- the owner is gone.

The continuation under the rollback-trigger item is NOT a defect. It is a legal
continuation and must never be reported as malformed.
-->

Depends on: open-format.md "Section: Open items", open-format.md "Reading rules for skills", project-log "Step 4: read what is already there"

## `DECISIONS.md`

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Rate limiting

Paths: `src/limiter/`

- **Harbor replaces the per-service limiter.** — one limiter is cheaper to tune
  than nine. Revisit: never. Source: https://example.com/harbor/issues/4
```

## `.daikenja/open.md`

```markdown
<!-- daikenja-open-format: 1 -->
# Harbor open items

## Open items

- 2026-08-14 -- Decide whether the 25% step waits for finance.
- 2026-08-13 -- @unassigned -- Decide the rollback trigger.
  The 25% step is the one that matters. Staging cannot reproduce the load, so
  this needs a real number agreed before Monday.

## Context link

- Runbook -- https://example.com/harbor/runbook

## Sources
```
