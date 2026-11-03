---
name: project-gaps
description: Audits a project's Daikenja ledger for open items with no owner or that have sat too long; only Open items are in scope. Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-gaps <key>` reads that project from anywhere.
metadata:
  owner: Carlos
  version: 2
disable-model-invocation: true
---

# Gaps

An audit of the project's open items, in `.daikenja/open.md`, for exactly two
problems: nobody owns it, or it has sat past the staleness threshold. Nothing
else is a gap. `DECISIONS.md` holds no owners or dates to audit, so a decision
is never reported here.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C, § Step D and § Notices, shared wording -- the shared
  resolve-and-parse mechanism Steps 1 and 2 below follow, the staleness-
  threshold resolution Step 1 also needs, and the exact notice text they
  reuse without restating it (a config marked absent or a project left
  unregistered has no literal wording inline in Step A -- only in § Notices,
  shared wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` § Version line, § Section: Open
  items, § `Blocked by:` and § Reading rules for skills -- the item grammar,
  `@unassigned`, the date raised, and the one prefix this report annotates.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` § Field notes -- what
  `stale_after_days` measures.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: the contract's own
  scope says a skill "implements it; it never redefines it" -- every rule in
  the file (tone scaling, the clean-result line, itemised findings) governs
  this skill's replies whether or not Step 4 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B, then § Step D to resolve
`stale_after_days`: the matched project's value, otherwise the profile's,
otherwise 21. State which was used.

**The user may name a project** -- `/daikenja:project-gaps <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C: `open.md` in the home repository and the
`DECISIONS.md` of **every** registered repository, each version line first. Only
`## Open items` is in scope for the filter, but every file is read the way every
read skill reads it, so a malformed line or a newer format version (one warning
per run, then read on) is reported wherever it sits.

## Step 3: filter

Every line in `## Open items` is open: closing an item deletes it, so nothing
there is resolved. For each item, evaluate two independent conditions:

- **Unowned.** `<owner>` is exactly `@unassigned`.
- **Stale.** Today's date minus the item's date raised is greater than the
  resolved `stale_after_days`. Age is measured from when the item was raised,
  not from when it was last touched -- `open.md` does not record that, per
  `config-schema.md`.

An item can be both, one, or neither. Only items matching at least one
condition are reported.

**Those two conditions are the whole filter, and `Blocked by:` does not change
it.** A blocked item is reported exactly as it would be without the prefix:
waiting on something else is not a reason to stop counting the days, and an
item nobody owns is unowned whether or not it could be worked on today. The
prefix changes the *report*, per Step 4, never the filter.

## Step 4: report

Two groups, an item may appear in both if it qualifies both ways. Sort each
group oldest first -- the longest-standing gap is the one that matters most.
Name each item by its words, per `response-format.md`; items carry no IDs:

```
Gaps in <project> (stale_after_days: 30, using this project's override) -- ownership and staleness, not severity

Unowned (2)
- Decide who is on call during the cutover window -- 2026-08-14
- Agree the success criteria for calling the migration done -- 2026-08-05 (9 days)

Stale (1, older than 21 days)
- Agree the success criteria for calling the migration done -- 2026-08-05 (9 days, also unowned)
```

**When a reported item opens with `Blocked by:`, say so on its line** -- "stale
because it is waiting on something also stale" is a different problem from
"stale because nobody picked it up". Match the words inside the prefix against
the other items' text, the way `project-log` finds an item by its words, and
say whether the blocker is still open:

```
- Confirm whether the gateway can skip the shared audit log -- 2026-08-19 (24 days)
  -- blocked by the audit log exemption (still open, since 2026-08-14)
```

A blocker that matches no item has been closed, which is worth more than
either case: the item is not waiting on anything any more and is still
sitting. Say so with the `reading.md` § Notices line for a block naming an item
no longer open, on the item's line. Several items that could match: name the
words and say the match is ambiguous; never pick one. Do not chase a blocker's
own blocker: one hop.

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
| The project has no repository (`paths: []`), or its home has an unmigrated `.daikenja/ledger.md` | **Stop** with the `reading.md` § Notices needs-migration line. Parse nothing. |
| No ledger at the resolved paths | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| `open.md` or a `DECISIONS.md` is a newer format version | Warn once with the § Notices line, then read and report as normal. |
| A line inside Open items does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
| A decision in `DECISIONS.md` | Never a gap. This skill's scope is open items only; an imposed decision's follow-up work is an open item, reported when it is unowned. |
| An open item opens with `Blocked by:` | Report it exactly as the filter says. Being blocked neither exempts an item nor makes it a gap on its own; it goes on the item's line as context, per Step 4. |
