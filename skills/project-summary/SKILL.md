---
name: project-summary
description: Gives a full-state overview of a project's Daikenja ledger, written for someone with no prior context. Use when the user says "what's the state of this project", "give me an overview", "summarize this project", "brief a new person on this", "where do things stand", or is opening a project they have not looked at before. Not for a personal delta since last time (that is /daikenja:project-catchup) or a single decision lookup (that is /daikenja:project-decisions). Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-summary <key>` reads that project from anywhere, without being in its directory.
metadata:
  owner: Carlos
  version: 1
---

# Summary

The whole ledger, read for someone who was not in the room. No assumed
context, no "since last time" framing -- that is `project-catchup`'s job.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § Section: Decisions, §
  Section: Open items, § Section: Context links, § Section: Sources, §
  Body markers and § Reading rules for skills -- this is the one read skill
  that genuinely wants every section's own grammar, plus the markers it
  carries through unresolved.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. The overview in Step 3 follows it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-summary <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C. This is the one read skill that genuinely wants
every section, so read them all in full -- the original four, plus Sources
when the ledger has it.

## Step 3: build the overview

**Decisions.** List every decision **currently in force** -- skip an entry
carrying `-> superseded by D-nnn`, since the entry that supersedes it is
already in the list and says so in its own body. State the count of
superseded decisions in one line rather than showing dead ones: "2 earlier
decisions were superseded; ask `/daikenja:project-decisions` for the history."
A decision carrying `Imposed.` is reported as imposed, not as an ordinary
one -- name who imposed it, per `ledger-format.md` § A decision imposed from
outside. A `Blocked by <id>.` or `Contradicts <id>.` marker on an entry shown
here is carried into its reworded line, not dropped -- this overview reports
what the marker says, not the relationship scan `project-decisions` performs.

**Open items.** Two groups: open (`- [ ] `) and resolved (`- [x] `). Lead with
open, since that is what someone new needs to act on. For resolved, a count is
enough unless the user asks for detail -- do not repeat every resolved body.

**Context links.** List them all; there is no volume problem here.

**Sources.** Only when the ledger has the section: list each source's label
and target, with its `read:` date ("never read" when the field is absent).
Whether a source *moved* is `/daikenja:project-sources`'s job -- do not query
any connector from this overview, and do not report staleness here. A ledger
without the section gets no Sources block at all; that is an older ledger,
not an empty section.

**Shape.** Newest first within each group, matching the ledger's own order.
Do not silently reorder or group by owner -- that is a presentation choice
`project-gaps` makes, not this skill. Topic first with the ID in parentheses,
per `response-format.md` -- the ledger line is ID-first, the reply is not.

```
<project> ledger -- C:/GitHub/atlas/.daikenja/ledger.md

Decisions in force (4)
- Cut over on a Saturday, not a weekday evening (D-005) -- @carlos
- Keep the legacy read replica online for 30 days after cutover (D-004) -- @unassigned
- Freeze schema changes from 2026-08-20 until cutover completes (D-003) -- @priya
- Atlas replaces the legacy store. No dual-write period (D-001) -- @priya
(1 earlier decision superseded; ask /daikenja:project-decisions for the history.)

Open items -- 4 open, 2 resolved
- Decide who is on call during the cutover window (O-006) -- @unassigned
- Confirm the 30-day replica cost with finance (O-005) -- @sam
- Write the rollback runbook and dry-run it once (O-004) -- @priya
- Agree the success criteria for calling the migration done (O-001) -- @unassigned

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
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The named project has no path and no absolute `ledger:` | **Stop.** One line: "`<key>` has no path and no absolute ledger in daikenja.yaml, so its ledger has no location." A pathless project *with* an absolute `ledger:` resolves normally. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
| A `Blocked by` or `Contradicts` marker names an ID with no entry | Report it -- which entry carries it, which ID it names -- then continue, per `ledger-format.md` § Reading rules, rule 6. |
