---
name: project-gaps
description: Audits a project's Daikenja ledger for open items with no owner or that have sat too long -- not a full project overview or a delta since last time. Use when the user says "what's still open", "what needs an owner", "what's stale", "what's falling through the cracks", "audit the open items", or "what should we be worried about". An unowned decision is never reported here -- only Open items are in scope. Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-gaps <key>` reads that project from anywhere, without being in its directory.
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

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C, § Step D and § Notices, shared wording -- the shared
  resolve-and-parse mechanism Steps 1 and 2 below follow, the staleness-
  threshold resolution Step 1 also needs, and the exact notice text they
  reuse without restating it (a config marked absent or a project left
  unregistered has no literal wording inline in Step A -- only in § Notices,
  shared wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § Section: Open items, §
  Body markers, § Relationships between entries, § A decision imposed from
  outside, § Section: Decisions and § Reading rules for skills -- the
  checkbox/`@unassigned`/resolution grammar, the one-hop blocker chase, and
  why an unowned imposed decision is excluded.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` § Field notes -- what
  `stale_after_days` measures.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 4 explicitly
  follows only § Entries are named topic-first, ID in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 4 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B, then § Step D to resolve
`stale_after_days`: the matched project's value, otherwise the profile's,
otherwise 21. State which was used.

**The user may name a project** -- `/daikenja:project-gaps <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

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
  `config-schema.md`.

An item can be both, one, or neither. Only items matching at least one
condition are reported.

**Those two conditions are the whole filter, and body markers do not change
it.** An item carrying `Blocked by O-007.` is reported exactly as it would be
without the marker: waiting on something else is not a reason to stop counting
the days, and an item nobody owns is unowned whether or not it could be worked
on today. The marker changes the *report*, per Step 4, never the filter.
Likewise a decision marked `Imposed.` is still a decision, and **no decision
enters the filter** -- see the failure table for why an unowned imposed decision
is not a gap. The Decisions section is still read, per Step 2, because a
`Blocked by` may name a `D-nnn` and a broken reference is reported wherever it
sits; being read is not being audited.

## Step 4: report

Two groups, an item may appear in both if it qualifies both ways. Sort each
group oldest first -- the longest-standing gap is the one that matters most.
Topic first with the ID in parentheses, per `response-format.md`:

```
Gaps in <project> (stale_after_days: 30, using this project's override) -- ownership and staleness, not severity

Unowned (2)
- Decide who is on call during the cutover window (O-006) -- 2026-08-14
- Agree the success criteria for calling the migration done (O-001) -- 2026-08-05 (9 days)

Stale (1, older than 21 days)
- Agree the success criteria for calling the migration done (O-001) -- 2026-08-05 (9 days, also unowned)
```

**When a reported item carries `Blocked by <id>.`, say so on its line** -- the
marker is already on the line being read, and "stale because it is waiting on
something also stale" is a different problem from "stale because nobody picked
it up". A blocker whose own entry is already resolved is worth more than either:
the item is not waiting on anything any more and is still sitting. Name the
blocker topic first with its ID, and say whether it is still open:

```
- Confirm whether the gateway can be exempted (O-008) -- 2026-08-19 (24 days)
  -- blocked by getting the audit-log exemption criteria published (O-007,
  still open)
```

Add nothing when the blocker resolves to no entry beyond the one-line report
`ledger-format.md` § Reading rules, rule 6 already requires. Do not chase a
blocker's own blockers: one hop, exactly as `project-decisions` does.

**`Blocked by` is the only marker this report annotates.** A `Contradicts`
marker is a reconciliation somebody owes, not an explanation of why an item sat,
and this report is short on purpose -- `/daikenja:project-decisions` is where a
contradiction surfaces, from both directions.

If nothing qualifies, say so plainly rather than omitting the report:

```
No gaps. Every open item in <project> has an owner and is within 21 days.
```

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on the 21-day default. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The named project has no path and no absolute `ledger:` | **Stop.** One line: "`<key>` has no path and no absolute ledger in daikenja.yaml, so its ledger has no location." A pathless project *with* an absolute `ledger:` resolves normally. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A line inside Open items does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
| A decision has no owner | Not a gap. Do not report it; this skill's scope is Open items only. |
| A decision marked `Imposed.` has no owner | Still not a gap, and this is the common shape for an imposed decision -- nobody on this side made it, so `@unassigned` is the honest attribution rather than a hole. `<owner>` on a decision is attribution, not accountability. What is auditable is the work it creates here -- comply, seek an exemption, escalate -- and that is an Open item this skill already reports when it is unowned. `project-log` offers to raise it at the moment the decision is written. |
| An open item is marked `Blocked by <id>.` | Report it exactly as the filter says. Being blocked neither exempts an item nor makes it a gap on its own; it goes on the item's line as context, per Step 4. |
| A `Blocked by` or `Contradicts` marker names an ID with no entry | Report it -- which entry carries it, which ID it names -- then continue, per `ledger-format.md` § Reading rules, rule 6. |
