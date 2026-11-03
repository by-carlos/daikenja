# beacon ledger

<!--
Fixture: a complete, well-formed ledger for the beacon project, in the two-file
shape -- the home repository's `DECISIONS.md` and `.daikenja/open.md`.
Synthetic content. The healthy-ledger control fixture.

Three decisions in force across two areas; the region-by-region rollout entry
replaced an all-regions-at-once rule, which is gone from the file (git keeps
it). Four open items, two of them unowned. One context link. An empty Sources
section, present because the skeleton requires it.
-->

Depends on: decisions-format.md "Shape", open-format.md "File skeleton", open-format.md "Section: Open items"

## `DECISIONS.md`

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Rollout

Paths: `deploy/`, `services/beacon/`

- **Roll the beacon service out region by region, not all at once.** — a bad
  region can be paused without a global rollback. Revisit: if every region
  comes to share one failure domain. Source: https://example.com/beacon/pull/41
- **Beacon replaces the old telemetry pipeline, with no dual-write period.** —
  running both would double the ingest bill for the whole rollout. Revisit:
  never. Source: https://example.com/beacon/issues/2

## Data

Paths: `migrations/`, `schema/events.sql`

- **Schema changes on the events table are frozen from 2026-08-18 until the
  rollout completes.** — two teams with pending migrations against that table
  agreed to hold. Revisit: when the rollout completes. Source:
  https://example.com/beacon/issues/17
```

## `.daikenja/open.md`

```markdown
<!-- daikenja-open-format: 1 -->
# beacon open items

## Open items

- 2026-08-15 -- @diablo -- Confirm the canary region for the rollout.
- 2026-08-14 -- @unassigned -- Decide who is on call during the region rollout.
- 2026-07-01 -- @diablo -- Write the rollback runbook for a single region.
- 2026-06-20 -- @unassigned -- Agree the success criteria for calling the rollout done.

## Context links

- Beacon runbook -- https://example.com/beacon/runbook

## Sources
```
