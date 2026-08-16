# Meridian ledger

<!--
Fixture: deliberately broken supersession pairs. Synthetic content, hand
written -- NOT produced by `project-log`, which keeps the two supersession
markers in sync and cannot generate this defect.

Two mismatches, both of which `project-decisions` must report rather than
silently resolve one way or the other (`docs/ledger-format.md:153-156`,
`skills/project-decisions/SKILL.md:66-68`):

1. D-006 opens its body with "Supersedes D-003." but D-003 carries no
   "-> superseded by D-006" tail -- the body claims a supersession the tail
   does not confirm.
2. D-005 carries the tail "-> superseded by D-004" but D-004's body does not
   claim "Supersedes D-005." -- the tail claims a supersession the body does
   not confirm.

D-002 and D-001 are a correctly matched pair, included as a control -- same
mechanism as `docs/ledger-format.md`'s worked example -- so a skill that
reports the two mismatches above is not also flagging a pair that is fine.
-->

## Decisions

- 2026-08-15 -- D-006 -- @sam -- Supersedes D-003. Deploy the ingest worker as three replicas, not one.
- 2026-08-14 -- D-005 -- @sam -- Retry failed ingest jobs up to five times. -> superseded by D-004
- 2026-08-13 -- D-004 -- @priya -- Retry failed ingest jobs up to three times.
- 2026-08-12 -- D-003 -- @priya -- Deploy the ingest worker as a single replica.
- 2026-08-10 -- D-002 -- @sam -- Supersedes D-001. Store ingest checkpoints in the database, not a local file.
- 2026-08-08 -- D-001 -- @sam -- Store ingest checkpoints in a local file. -> superseded by D-002

## Open items

- [ ] 2026-08-11 -- O-001 -- @unassigned -- Decide the checkpoint retention window.

## Context links

- Runbook -- https://example.com/meridian/runbook

## Changelog

- 2026-08-15T10:00Z -- log -- +D-006
- 2026-08-14T09:00Z -- log -- +D-005
- 2026-08-13T08:30Z -- log -- +D-004
- 2026-08-12T14:00Z -- log -- +D-003
- 2026-08-10T11:15Z -- log -- +D-002, superseded D-001
- 2026-08-08T09:00Z -- log -- +D-001
