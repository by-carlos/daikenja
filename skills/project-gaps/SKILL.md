---
name: project-gaps
description: Audits a project's Daikenja ledger for open items with no owner or that have sat too long. Use when the user says "what's still open", "what needs an owner", "what's stale", "what's falling through the cracks", "audit the open items", or "what should we be worried about". Not for a full project overview (that is /daikenja:project-summary) or a delta since last time (that is /daikenja:project-catchup). An unowned decision is never reported here -- only Open items are in scope. Read-only; writes nothing.
metadata:
  owner: Carlos
  version: 1
---

# Gaps

An audit of the Open items section for exactly two problems: nobody owns it,
or it has sat past the staleness threshold. Nothing else is a gap. In
particular, an unowned **decision** is normal (per `ledger-format.md`) and is
never reported here.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- entry grammar, Open items.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` -- `stale_after_days`
  resolution order.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A and § Step B, then § Step D to resolve
`stale_after_days`: the matched project's value, otherwise the profile's,
otherwise 21. State which was used.

## Step 2: read the ledger

Follow `reading.md` § Step C. Only Open items are in scope for the filter, but
read the whole file the way every read skill does.

## Step 3: filter

From Open items, keep only `- [ ] ` lines -- a resolved item (`- [x] `) is
never a gap, regardless of its owner or age.

For each open line, evaluate two independent conditions:

- **Unowned.** `<owner>` is exactly `@unassigned`.
- **Stale.** Today's date minus the entry's `<date>` field is greater than the
  resolved `stale_after_days`. Age is measured from when the item was raised,
  not from when it was last touched -- the ledger does not track that, per
  `config-contract.md`.

An item can be both, one, or neither. Only items matching at least one
condition are reported.

## Step 4: report

Two groups, an item may appear in both if it qualifies both ways. Sort each
group oldest first -- the longest-standing gap is the one that matters most.

```
Gaps in <project> (stale_after_days: 21, using this project's override)

Unowned (2)
- O-006 -- 2026-08-14 -- Decide who is on call during the cutover window.
- O-001 -- 2026-08-05 -- Agree the success criteria for calling the migration done. (9 days)

Stale (1, older than 21 days)
- O-001 -- 2026-08-05 -- Agree the success criteria for calling the migration done. (9 days, also unowned)
```

If nothing qualifies, say so plainly rather than omitting the report:

```
No gaps. Every open item in <project> has an owner and is within 21 days.
```

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on the 21-day default. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A line inside Open items does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
| A decision has no owner | Not a gap. Do not report it; this skill's scope is Open items only. |
