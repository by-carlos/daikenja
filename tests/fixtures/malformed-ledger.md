# Harbor ledger

<!--
Fixture: deliberately broken ledger. Synthetic content.

Two defects, both of which `project-log` must report rather than write over:

1. The `## Changelog` heading is misspelled `## Change log`, so a required
   section is missing by exact-heading lookup.
2. The `D-002` line has three fields instead of four -- the owner is gone.

The `O-001` continuation line is NOT a defect. It is a legal continuation and
must never be reported as malformed.
-->

## Decisions

- 2026-08-14 -- D-002 -- Ramp the rollout over three days.
- 2026-08-12 -- D-001 -- @diablo -- Harbor replaces the per-service limiter.

## Open items

- [ ] 2026-08-13 -- O-001 -- @unassigned -- Decide the rollback trigger.
  The 25% step is the one that matters. Staging cannot reproduce the load, so
  this needs a real number agreed before Monday.

## Context links

- Runbook -- https://example.com/harbor/runbook

## Change log

- 2026-08-14T09:40Z -- log -- +D-002
- 2026-08-13T11:00Z -- log -- +O-001
- 2026-08-12T10:00Z -- log -- +D-001
