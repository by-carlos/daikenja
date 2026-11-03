---
name: project-sources
description: Reports which of a project's tracked sources moved since they were last read, by comparing each source's stored last-modified value against what its system reports now. Read-only against the ledger; recording a re-read goes through /daikenja:project-log. Accepts an optional project key -- `/daikenja:project-sources <key>` reads that project from anywhere.
metadata:
  owner: Carlos
  version: 2
disable-model-invocation: true
---

# Sources

Answers the question `project-catchup` cannot: not "what did Daikenja write
since I looked" but "what moved in the documents this project is tracked
from". For a project that consists largely of tracking documents other people
own, this is the difference between one check and re-reading everything.

The check is cheap by design: a source stores the last-modified value its own
system reported when it was last read, and this skill compares that against
what the system reports now. Different means moved. No content is diffed, no
date arithmetic is done, and nothing is re-read until the user asks.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, plus the exact notice text they reuse
  without restating it (a config marked absent or a project left unregistered
  has no literal wording inline in Step A -- only in § Notices, shared
  wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` § Version line, § Section:
  Sources and § Reading rules for skills -- the head line, the fields and the
  baseline rule. The Sources section lives in the home repository's
  `.daikenja/open.md`.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 4 explicitly
  follows § The answer comes first and § A clean result is one line, but the
  contract's own scope
  says a skill "implements it; it never redefines it" -- every rule in the
  file governs this skill's replies whether or not Step 4 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-sources <key>`, or the
key in prose. `reading.md` § Step A0 is the whole rule: a named key resolves
that project from anywhere on disk and never falls back to the current
directory. Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C: `open.md` in the home repository and the
`DECISIONS.md` of every registered repository, each version line first (a
newer version warns once per run and is still read). `## Sources` in `open.md`
is what this skill is for; the rest is read so a malformed line or a version
warning is reported, not to be reported on.

- **The section is empty.** One line and stop -- there is nothing to check:
  "No sources tracked. /daikenja:project-log records the first source."
- **No `## Sources` heading.** The section is required, so this is a defect,
  reported by name per `open-format.md` § Reading rules for skills, naming
  `/daikenja:project-log` as the repair path. With no section there is nothing
  to check, so stop.

## Step 3: check each source

For every source, ask the system its target lives in what last-modified value
it reports **now**, using whatever tool is connected -- a wiki or ticket
connector, an MCP server, a web fetch that returns a meaningful last-modified.
Batch where the system allows it: wiki and ticket systems commonly report
last-modified for a whole tree in one call, and one call beating twenty is the
point of storing the value at all.

Rules, all of them the contract's:

- **Never invent a value.** A system that reports nothing usable yields "could
  not check", not a guess, not a fetch date, and not silence.
- **A missing connector is one notice line, then reduced behaviour.** The
  affected sources are reported as unchecked; every source that can be checked
  still is. Never make the run conditional on any connector, and never
  hard-stop on one being absent.
- **Reading metadata is not reading content.** This step establishes whether a
  source moved, nothing more. Do not fetch and summarize a source's content
  unless the user asks (Step 5).

Classify each source by comparison:

| Stored vs reported | Meaning |
|---|---|
| `modified:` present, reported value differs | **Moved** since it was last read. |
| `modified:` present, reported value identical | **Unchanged** since `read:`. |
| No `modified:` stored | **No baseline** -- nothing can say whether it moved, only when it was last read. Say so; do not treat it as moved or unchanged. |
| System unreachable, no connector, or no usable value reported | **Could not check** -- name which and why in one line. |

## Step 4: report

Answer first, per `response-format.md`: lead with what moved. Name each source
by its label; sources carry no IDs. Group in this order and drop any empty
group -- moved, no baseline, could not check, unchanged (a count is enough for
unchanged unless the user asks):

```
Ledger: C:/GitHub/atlas/DECISIONS.md, C:/GitHub/atlas/.daikenja/open.md

2 of 6 sources moved since you last read them:
- Platform standards page -- read 2026-08-11; its system now reports 2026-08-19T14:02Z, stored 2026-08-10T09:12Z.
- Rollout epic -- read 2026-08-15; now reports revision 41, stored revision 37.

No baseline:
- Vendor evaluation sheet -- read 2026-08-15, no modified value stored, so there is nothing to compare.

Could not check:
- On-call rota -- no connector for example-chat is available in this session.

3 sources unchanged.
```

A clean result is one line: "No source has moved. All 6 report the values
stored when you last read them." Include each source's `does not answer:`
field only when the user's question is about where to find something -- the
field exists to stop a re-read, so surface it when it would.

## Step 5: offer, then record on approval

Two offers, each once, neither acted on without a yes:

1. **For what moved:** offer to open the moved sources and report what
   actually changed. That is ordinary reading with the session's tools, and it
   is what makes a re-read recordable.
2. **For what was just re-read:** offer to record the refresh -- the value the
   system reported at this read, and today as `read:` -- for exactly the
   sources whose content the user has now seen (in this session, or because
   they say they read it). Never for sources that merely moved: updating
   `modified:` without a re-read erases the staleness signal, per
   `open-format.md` § Section: Sources. A source with no baseline gets its
   first `modified:` the same way -- the offer names it as establishing the
   baseline.

On a yes, hand the exact field updates to `/daikenja:project-log`, naming each
source by its label, which shows the lines and writes them to `open.md` in one
approved batch. This skill never writes the ledger itself, and never registers
a new source -- that is `/daikenja:project-log` directly.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on the default file locations. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory. |
| The project has no repository (`paths: []`), or its home has an unmigrated `.daikenja/ledger.md` | **Stop** with the `reading.md` § Notices needs-migration line. Parse nothing. |
| No ledger at the resolved paths | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| An empty `## Sources` section | One line per Step 2 and stop. Not an error. |
| No `## Sources` heading in `open.md` | Report the missing section by name, naming `/daikenja:project-log`, and stop, per Step 2. |
| `open.md` or a `DECISIONS.md` is a newer format version | Warn once with the § Notices line, then read and check as normal. |
| A source head line that does not parse | Report it -- name the line and what is wrong -- then continue with the rest, per `open-format.md` § Reading rules for skills. |
| A connector is missing, or a target is unreachable | One line naming which sources could not be checked and why, then continue with the ones that can be. Never a hard stop. |
| The system reports no last-modified for a target | That source is "could not check" this run; the stored fields are left alone. Never substitute a fetch date. |

## What this skill does not do

- It does not write the ledger. Recording a refresh goes through
  `/daikenja:project-log`, and registering or removing a source is
  `/daikenja:project-log` directly.
- It does not report what Daikenja wrote since last time. That is
  `/daikenja:project-catchup`, the mirror-image question.
- It does not update the documents a source points at, and it does not offer
  to. The one offer of that kind lives in `project-log` § Step 8, where an
  entry names a document, and this skill does not duplicate it.
- It does not audit open items for owners or staleness. That is
  `/daikenja:project-gaps`; a stale *source* and a stale *entry* are different
  facts.
- It does not summarize source content on its own initiative. Opening a moved
  source is Step 5's offer, taken only on a yes.
