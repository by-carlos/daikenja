# beacon ledger

Depends on: ledger-format.md "File skeleton", ledger-format.md "Ordering"

## Decisions

- 2026-08-13 -- D-004 -- @rimuru -- Supersedes D-002. Roll the beacon service out region by region, not all at once -- a bad region can be paused without a global rollback.
- 2026-08-10 -- D-003 -- @diablo -- Freeze schema changes on the events table from 2026-08-18 until the rollout completes.
  Two teams have pending migrations against that table. Both agreed to hold.
- 2026-07-20 -- D-002 -- @rimuru -- Roll the beacon service out to every region at once. -> superseded by D-004
- 2026-07-05 -- D-001 -- @unassigned -- Beacon replaces the old telemetry pipeline. No dual-write period.

## Open items

- [ ] 2026-08-15 -- O-005 -- @diablo -- Confirm the canary region for the rollout.
- [ ] 2026-08-14 -- O-004 -- @unassigned -- Decide who is on call during the region rollout.
- [ ] 2026-07-01 -- O-003 -- @diablo -- Write the rollback runbook for a single region.
- [ ] 2026-06-20 -- O-002 -- @unassigned -- Agree the success criteria for calling the rollout done.
- [x] 2026-08-01 -- O-001 -- @benimaru -- Confirm the events table row counts with the data team. -> resolved 2026-08-05

## Context links

- Beacon runbook -- https://example.com/beacon/runbook

## Changelog

- 2026-08-15T09:00Z -- project-log -- +O-005
- 2026-08-14T09:00Z -- log -- +O-004
- 2026-08-13T09:00Z -- log -- +D-004, superseded D-002
- 2026-08-10T09:00Z -- log -- +D-003
- 2026-08-05T09:00Z -- log -- resolved O-001
- 2026-08-01T09:00Z -- log -- +O-001
- 2026-07-20T09:00Z -- log -- +D-002
- 2026-07-05T09:00Z -- log -- +D-001
- 2026-07-01T09:00Z -- log -- +O-003
- 2026-06-20T09:00Z -- log -- +O-002
