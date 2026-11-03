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

The whole ledger, read for someone who was not in the room: every
`DECISIONS.md` of the project and its `.daikenja/open.md`. No assumed context,
no "since last time" framing -- that is `project-catchup`'s job.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, and the exact notice wording Step 4
  reuses without restating it.
- `${CLAUDE_PLUGIN_ROOT}/docs/decisions-format.md` § Shape -- areas, `Paths:`
  lines, `Moved:` lines and the shape of an entry in force.
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` § Version line, § Section: Open
  items, § `Blocked by:`, § Section: Context links, § Section: Sources and §
  Reading rules for skills -- this is the one read skill that genuinely wants
  every section's own grammar.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` § Reading several
  repositories -- every repository's `DECISIONS.md` is read, and each entry
  names the repository it came from.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-card.md` § Location, § Format and
  § Reading a card -- the project card beside `open.md`, which this overview
  opens with when it exists.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: the contract's own
  scope says a skill "implements it; it never redefines it" -- every rule in
  the file (tone scaling, the clean-result line, itemised findings) governs
  this skill's replies whether or not Step 3 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-summary <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C, in full: the `DECISIONS.md` of **every**
registered repository, in `paths` order, plus any file a `Moved:` line names,
and all three sections of `open.md`. Each file's version line comes first; a
newer version is warned about once per run and still read.

**Also read the project card**, at the path derived from the home repository
per `project-card.md` § Location, when it exists. Someone with no prior context
needs "what is this project about" before "what was decided in it", and the
card is the only place the first question is answered. No card is one line
per `project-card.md` § Reading a card, then the overview continues without
it.

## Step 3: build the overview

**Scope, first.** When a card was read, its Scope paragraph opens the
overview, followed by the Owns handles on one line each. People are left out
here -- the open items' owners already say who is doing what. With no card
there is no Scope block; the one-line notice from Step 2 stands in for it.

**Decisions.** Every entry in every `DECISIONS.md` is in force, so list them
all, grouped by repository and then by area, in file order. Each line is the
bold rule reworded plainly, then its why clause when it says who imposed the
decision. A repository with no `DECISIONS.md` yet gets one line saying no
decisions are recorded there. History -- what a decision replaced, and when
-- is `/daikenja:project-decisions`'s job, from git.

**Open items.** Every line in `## Open items` is open; closed ones are gone
from the file. List each with its owner and date raised. An item opening with
`Blocked by:` keeps that prefix in its reworded line; this overview reports
what the item says, not the blocker check `project-gaps` makes.

**Context links.** List them all; there is no volume problem here.

**Sources.** List each source's label and target, with its `read:` date
("never read" when the field is absent). Whether a source *moved* is
`/daikenja:project-sources`'s job -- do not query any connector from this
overview, and do not report staleness here.

**Shape.** Keep each file's own order. Do not silently reorder or group by
owner -- that is a presentation choice `project-gaps` makes, not this skill.
Name entries and items by their words, per `response-format.md`; neither file
carries IDs.

```
Ledger: C:/GitHub/atlas/DECISIONS.md, C:/GitHub/atlas-infra/DECISIONS.md, C:/GitHub/atlas/.daikenja/open.md
Card: C:/GitHub/atlas/.daikenja/project.md

Scope
Atlas replaces the legacy order store for the payments team. It covers the
data migration, the cutover and the 30-day fallback window; it does not
cover the reporting warehouse, which stays on the legacy store.
- channel: #atlas-migration
- repo: northwind/atlas
- tracker: ATL

Decisions in force (4)
atlas -- Cutover
- Cut over on a Saturday, not a weekday evening
- Atlas replaces the legacy store, with no dual-write period
atlas -- Schema
- Freeze schema changes from 2026-08-20 until cutover completes
atlas-infra -- Replica
- Keep the legacy read replica online for 30 days after cutover

Open items (3)
- Decide who is on call during the cutover window -- @unassigned, raised 2026-08-14
- Confirm the 30-day replica cost with finance -- @sam, raised 2026-08-12
- Blocked by: the rollback runbook. Agree the success criteria for calling the migration done -- @unassigned, raised 2026-08-05

Context links (2)
- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md

Sources (1)
- Cutover plan -- https://example.com/atlas/cutover-plan -- read 2026-08-18
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
| `daikenja.yaml` absent | One notice, continue on the default file locations. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The project has no repository (`paths: []`), or its home has an unmigrated `.daikenja/ledger.md` | **Stop** with the `reading.md` § Notices needs-migration line. Parse nothing. |
| No ledger at the resolved paths | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A file is a newer format version | Warn once with the § Notices line, then read and summarize as normal. |
| No project card beside `open.md` | One line per `project-card.md` § Reading a card, naming `/daikenja:setup-project`, then the overview without a Scope block. Never a stop. |
| The card is missing a section or has a line that does not parse | Report it -- name the heading or the line -- then show what the card does have. Never rewrite it. |
| A line inside a section does not match the grammar | Report it -- name the file, the line and what is wrong -- then continue with the rest. |
