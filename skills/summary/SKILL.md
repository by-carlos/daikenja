---
name: summary
description: Gives a full-state overview of a project's Daikenja ledger, written for someone with no prior context. Use when the user says "what's the state of this project", "give me an overview", "summarize this project", "brief a new person on this", "where do things stand", or is opening a project they have not looked at before. Not for a personal delta since last time (that is /daikenja:catchup) or a single decision lookup (that is /daikenja:decisions). Read-only; writes nothing.
metadata:
  owner: Carlos
  version: 1
---

# Summary

The whole ledger, read for someone who was not in the room. No assumed
context, no "since last time" framing -- that is `catchup`'s job.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- entry grammar, supersession,
  resolution tails.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A and § Step B.

## Step 2: read the ledger

Follow `reading.md` § Step C. This is the one read skill that genuinely wants
every section, so read all four in full.

## Step 3: build the overview

**Decisions.** List every decision **currently in force** -- skip an entry
carrying `-> superseded by D-nnn`, since the entry that supersedes it is
already in the list and says so in its own body. State the count of
superseded decisions in one line rather than showing dead ones: "2 earlier
decisions were superseded; ask `/daikenja:decisions` for the history."

**Open items.** Two groups: open (`- [ ] `) and resolved (`- [x] `). Lead with
open, since that is what someone new needs to act on. For resolved, a count is
enough unless the user asks for detail -- do not repeat every resolved body.

**Context links.** List them all; there is no volume problem here.

**Shape.** Newest first within each group, matching the ledger's own order.
Do not silently reorder or group by owner -- that is a presentation choice
`gaps` makes, not this skill.

```
<project> ledger -- C:/GitHub/atlas/.daikenja/ledger.md

Decisions in force (4)
- D-005 -- @carlos -- Cut over on a Saturday, not a weekday evening.
- D-004 -- @unassigned -- Keep the legacy read replica online for 30 days after cutover.
- D-003 -- @priya -- Freeze schema changes from 2026-08-20 until cutover completes.
- D-001 -- @priya -- Atlas replaces the legacy store. No dual-write period.
(1 earlier decision superseded; ask /daikenja:decisions for the history.)

Open items -- 4 open, 2 resolved
- O-006 -- @unassigned -- Decide who is on call during the cutover window.
- O-005 -- @sam -- Confirm the 30-day replica cost with finance.
- O-004 -- @priya -- Write the rollback runbook and dry-run it once.
- O-001 -- @unassigned -- Agree the success criteria for calling the migration done.

Context links (2)
- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md
```

**Empty sections.** Say so plainly ("No open items.") rather than omitting the
heading -- an empty section is information, not nothing to report.

## Step 4: name what was used

If the project was unregistered, or `daikenja.yaml` was absent, say so in one
line per `reading.md` § Notices, shared wording -- someone new to the project
should know whether they are looking at the registered ledger or a
best-effort default location.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on ledger defaults. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:log`. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
