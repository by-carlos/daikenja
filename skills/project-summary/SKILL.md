---
name: project-summary
description: Gives a full-state overview of a project's Daikenja ledger, written for someone with no prior context. Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-summary <key>` reads that project from anywhere.
metadata:
  owner: Carlos
  version: 2
context: fork
background: false
disable-model-invocation: true
---

# Summary

The whole ledger, read for someone who was not in the room. No assumed
context, no "since last time" framing -- that is `project-catchup`'s job.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, and the exact notice wording Step 4
  reuses without restating it.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § Section: Decisions, §
  Section: Open items, § Section: Context links, § Section: Sources, §
  Body markers and § Reading rules for skills -- this is the one read skill
  that genuinely wants every section's own grammar, plus the markers it
  carries through unresolved.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-card.md` § Location, § Format and
  § Reading a card -- the project card beside the ledger, which this overview
  opens with when it exists.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 3 explicitly
  follows only § Entries are named topic-first, ID in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 3 names it.

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

**Also read the project card**, at the path derived from the ledger path per
`project-card.md` § Location, when it exists. Someone with no prior context
needs "what is this project about" before "what was decided in it", and the
card is the only place the first question is answered. No card is one line
per `project-card.md` § Reading a card, then the overview continues without
it.

## Step 3: build the overview

**Scope, first.** When a card was read, its Scope paragraph opens the
overview, followed by the Owns handles on one line each. People are left out
here -- the ledger's owners already say who is doing what. With no card there
is no Scope block; the one-line notice from Step 2 stands in for it.

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
Card: C:/GitHub/atlas/.daikenja/project.md

Scope
Atlas replaces the legacy order store for the payments team. It covers the
data migration, the cutover and the 30-day fallback window; it does not
cover the reporting warehouse, which stays on the legacy store.
- channel: #atlas-migration
- repo: northwind/atlas
- tracker: ATL

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
| No project card beside the ledger | One line per `project-card.md` § Reading a card, naming `/daikenja:setup-project`, then the overview without a Scope block. Never a stop. |
| The card is missing a section or has a line that does not parse | Report it -- name the heading or the line -- then show what the card does have. Never rewrite it. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. |
| A `Blocked by` or `Contradicts` marker names an ID with no entry | Report it -- which entry carries it, which ID it names -- then continue, per `ledger-format.md` § Reading rules, rule 6. |
