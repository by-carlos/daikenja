---
name: project-sources
description: Reports which of a project's tracked sources moved since they were last read, by comparing each source's stored last-modified value against what its system reports now. Use when the user says "what changed in the sources", "did any of the docs I track move", "are my sources stale", "check the sources", "refresh the sources", or asks whether a tracked page, epic or thread has changed since they last read it. The mirror image of /daikenja:project-catchup, which reports what Daikenja itself wrote -- this skill reports what moved outside, in documents other people own. Read-only against the ledger -- recording a re-read goes through /daikenja:project-log on the user's approval, and registering a new source is /daikenja:project-log directly. Accepts an optional project key -- `/daikenja:project-sources <key>` reads that project from anywhere, without being in its directory.
metadata:
  owner: Carlos
  version: 1
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

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § Section: Sources -- the head
  line, the fields, the baseline rule, and the Changelog verbs.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. The report in Step 4 follows it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-sources <key>`, or the
key in prose. `reading.md` § Step A0 is the whole rule: a named key resolves
that project from anywhere on disk and never falls back to the current
directory. Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C. The Sources section is what this skill is for;
the rest of the file is read so the report can note nothing else, not to be
reported on.

- **No `## Sources` heading, or the section is empty.** One line and stop --
  there is nothing to check:

  ```
  This ledger has no Sources section. /daikenja:project-log records the first source.
  ```

  (For a heading that is present but empty: "No sources tracked." -- same
  outcome, worded for what is actually there.)

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

Answer first, per `response-format.md`: lead with what moved. Topic first, ID
in parentheses. Group in this order and drop any empty group -- moved, no
baseline, could not check, unchanged (a count is enough for unchanged unless
the user asks):

```
Ledger: C:/GitHub/atlas/.daikenja/ledger.md

2 of 6 sources moved since you last read them:
- Platform standards page (S-001) -- read 2026-08-11; its system now reports 2026-08-19T14:02Z, stored 2026-08-10T09:12Z.
- Rollout epic (S-004) -- read 2026-08-15; now reports revision 41, stored revision 37.

No baseline:
- Vendor evaluation sheet (S-002) -- read 2026-08-15, no modified value stored, so there is nothing to compare.

Could not check:
- On-call rota (S-005) -- no connector for example-chat is available in this session.

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
   `ledger-format.md` § Section: Sources. A source with no baseline gets its
   first `modified:` the same way -- the offer names it as establishing the
   baseline.

On a yes, hand the exact field updates to `/daikenja:project-log`, which shows
the lines and writes on approval, one run, one Changelog line, `~S-nnn` per
source touched, writer `project-log via project-sources`. This skill never
writes the ledger itself, and never registers a new source -- that is
`/daikenja:project-log` directly.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on ledger defaults. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory. |
| The named project has no path and no absolute `ledger:` | **Stop.** One line: "`<key>` has no path and no absolute ledger in daikenja.yaml, so its ledger has no location." |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| No `## Sources` heading, or an empty section | One line per Step 2 and stop. Not an error, and not a defect in the ledger. |
| A source head line that does not parse | Report it -- name the line and what is wrong -- then continue with the rest, per `ledger-format.md` § Reading rules. |
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
