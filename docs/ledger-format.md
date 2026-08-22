# Ledger format

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Who an owner handle refers to -- remember-persona "The `Known as` field"
- § IDs -- project-catchup "Step 0: read the contracts", project-decisions "Step 0: read the contracts"
- § Body markers -- project-catchup "Step 0: read the contracts", project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts"
- § Relationships between entries -- project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts"
- § A decision imposed from outside -- project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts"
- § Section: Decisions -- project-catchup "Step 0: read the contracts", project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts"
- § Section: Open items -- project-catchup "Step 0: read the contracts", project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts"
- § Section: Context links -- project-catchup "Step 0: read the contracts", project-summary "Step 0: read the contracts"
- § Section: Sources -- project-catchup "Step 0: read the contracts", project-sources "Step 0: read the contracts", project-summary "Step 0: read the contracts"
- § Section: Changelog -- project-catchup "Step 0: read the contracts"
- § Compacting a long summary -- project-catchup "Step 0: read the contracts"
- § Reading rules for skills -- project-catchup "Step 0: read the contracts", project-decisions "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts"

The ledger is the per-project record of what was decided, what is still open,
where the context lives, and what changed it. This document is the contract.
Every Daikenja skill reads a ledger by this spec, and `log` writes one by this
spec. A skill that invents its own shape is a bug.

## Location

`.daikenja/ledger.md` in the project root, by default. **The root is the
first path in the project's entry**, so a project spanning several directories
keeps one ledger, in the first one registered -- not one per directory.

A project may point somewhere else with the `ledger:` key in
`~/.claude/daikenja/daikenja.yaml`, as a relative or an absolute path. See
[`config-resolution.md`](config-resolution.md) § Resolving `ledger` for the
pointer grammar and § Finding the ledger for the lookup order a skill follows.

**A project with no repository of its own** -- work tracked across a wiki, a
chat space or a ticket system rather than a code checkout -- registers with no
directory at all (`paths: []`) and therefore has no root for a relative pointer
to resolve against. Give it an absolute one, by convention
`~/.claude/daikenja/ledgers/<project-key>.md`, alongside every other file
Daikenja keeps for the user rather than for a repository. The two keys are a
pair: `paths: []` is what makes the project reachable by name without a folder,
and the absolute `ledger:` is what gives its record a location. Nothing below this
point changes for a ledger at that location -- the format, the sections, the
entry grammar, and the write rules are the same wherever the file lives.

## File skeleton

Five H2 sections, these exact names, always in this order:

```markdown
# <project> ledger

## Decisions

## Open items

## Context links

## Sources

## Changelog
```

The first three and the Changelog are always present, even when empty.
`## Sources` is the one exception: it is the newest section, and a ledger
written before it existed legitimately lacks the heading. Such a ledger tracks
no sources and reads correctly everywhere -- the absence is not a defect and
no skill reports it as one. `log` adds the heading, directly above
`## Changelog`, as part of the approved write that records the first source;
the heading is never added on its own.

The H1 is free text and carries no meaning. Skills key off the H2 headings.

`log` scaffolds this file when it is missing. The exact bytes it writes are in
[`../templates/ledger.md`](../templates/ledger.md).

## Ordering

**Newest first, in every section.** A new entry is inserted **directly above the
first entry whose date is the same as or older than its own**. When the section
holds no such entry, it goes at the end of the section.

The rule is a *position*, not a location. For an entry dated today -- which is
every entry an ordinary incremental write produces -- that position resolves to
directly under the H2 heading, which is why "insert at the top" reads as the
same rule and is never wrong for that case. It stops being enough only in a
**backfill**, where most entries are older than everything already in the file:
inserting those under the heading would break newest-first on the very first
one. Inserting at the date position keeps the file readable without renumbering
anything.

The Changelog follows the same rule and always resolves to the top, because a
Changelog line is timestamped when the write happens. It is therefore the newest
line in the file whatever the entries it names are dated -- a bulk write of
five-year-old decisions still puts today's Changelog line on top. Context links
and Sources have no ordering rule at all, so a new one goes directly under the
heading.

**No skill may depend on the ordering.** A human is free to reorder Open items
by priority, and `log` restores nothing. Order is a reading convenience; the
date field is the fact. `catchup` in particular gets its delta from the
Changelog, never from position in a section. This is also why the insert rule
above is a scan for one position rather than a sort: `log` inserts a line and
never touches the entries around it, so a section a human has arranged by hand
stays arranged by hand.

## Entry grammar

Decisions and Open items share one line grammar:

```
<marker><date> -- <id> -- <owner> -- <body>
```

The separator is ` -- ` (space, two hyphens, space).

**Strip the marker first, then split.** The marker is a fixed prefix (`- `,
`- [ ] `, `- [x] `) and is not separated by ` -- `, so it comes off before
anything else. What remains is four fields.

**A parser splits on ` -- ` at most three times.** Everything after the third
separator is the body, verbatim. This matters: the body is free text and can
legitimately contain ` -- ` of its own (a parenthetical aside, a quoted
range). Bounding the split at three consumes exactly the three separators
between date, id, owner and body, and leaves anything past them alone.

The body is the last field. The only thing that may follow it is a **tail**, and
there are exactly two:

```
 -> resolved <YYYY-MM-DD>[, see D-nnn]
 -> superseded by D-nnn
```

To find a tail, take the **last** ` -> ` on the line and test whether what
follows matches one of those two forms. If it matches, it is a tail and
everything before it is the body proper. If it does not match, it is ordinary
body text -- a body is free to contain `->` as punctuation.

**Two tails, and no more.** Everything else an entry needs to record about
itself -- that it was imposed from outside, that it is blocked by or
contradicts another entry -- is a **body marker** rather than a third tail
form. See [Body markers](#body-markers).

| Field | Rule |
|---|---|
| `<marker>` | `- ` in Decisions. `- [ ] ` or `- [x] ` in Open items. |
| `<date>` | `YYYY-MM-DD`, absolute, never relative. The best known date the entry's subject was decided or raised. For an incremental write that is the day it is written; for a backfill it is the original date; for a run handed classified material by another skill (`project-log via <skill>`) it is the date that skill established, when it established one. See [Approximate dates](#approximate-dates). |
| `<id>` | `D-001` in Decisions, `O-001` in Open items. See [IDs](#ids). |
| `<owner>` | `@` plus one token, no spaces. `@unassigned` when there is none. |
| `<body>` | Free text on one line. May contain `--`. May end with markdown links. |

Every field is always present. A field is never omitted to signal absence --
`@unassigned` is written out, because positional parsing depends on the field
count and because `gaps` searches for exactly that token.

### Who an owner handle refers to

The grammar above fixes the shape of `<owner>`, not its referent. `@priya` is
one token on a line. Nothing in the ledger says which Priya it is, and nothing
says whether the `@priya.n` three entries down is the same person or a second
one.

**`personas.md` is where that is recorded** -- whatever `profile.personas`
resolves to, per
[`config-resolution.md`](config-resolution.md#resolving-writing_style-and-personas),
under the optional `Known as` field the shipped template describes. It stays
what it already was: the user's own prose about people they write to, kept for
their own reasons. **It is not a roster.** A handle missing from it is the
normal case, no skill treats an unrecorded owner as an error, and nothing here
makes the ledger depend on that file existing.

What it buys is two things, in that order. `meeting-review` **prefers** a
recorded handle: where a transcript's speaker matches a persona, the entry is
attributed to the handle written there rather than to one derived from the
speaker label, so the second spelling is never minted -- see its § Step 4:
attribute. `project-log` then **reports** whatever is left: a handle seen
neither elsewhere in this ledger nor in `personas.md` gets one line inside the
proposal that skill was already showing.

That is the whole mechanism. Nothing is rejected, no handle a user supplied is
rewritten, and `<owner>` stays free text -- the point is to avoid a second
spelling where the file settles it, and otherwise to surface one at the moment
it is one keystroke to fix, not to police the field. `@unassigned` is never
reported: it is the documented value for no owner, not an unrecognized person.

### Continuation lines

An entry may carry detail on following lines indented by two spaces, with no
list marker. The first line must still stand alone as the whole entry in
summary. Skills that list entries show the first line only unless asked for
detail.

```markdown
- 2026-08-14 -- D-004 -- @carlos -- Ship as a plugin, not a junction installer.
  Junctions needed an elevated PowerShell run and broke silently when the repo
  directory was renamed. A plugin directory is copied and versioned by the
  client.
```

### IDs

`D-` for Decisions, `O-` for Open items, `S-` for Sources, followed by a
zero-padded three-digit number. Sequences are per section and per ledger. They
start at `001`, increase by one, and are **never reused** -- a deleted entry's
ID stays retired.

`log` allocates the next ID from the highest one **ever used** in that section,
plus one. That is the higher of the highest ID present in the section and the
highest ID for that section named anywhere in the Changelog. Reading the section
alone is not enough: delete the newest entry and the section's maximum drops,
which would reissue a retired ID. The Changelog names every ID ever created, so
it is what makes retirement stick.

A compacted Changelog line is covered by that scan without special handling. A
range writes both of its endpoints in full and its maximum is always the upper
one, so the highest ID in `+D-004..D-017` is the `D-017` written on the line.
Expanding first is harmless and never necessary here.

**A written entry is never renumbered.** IDs record allocation order, not
chronology, and in a backfill the two come apart: entries dated earlier than
everything already in the file still take the next free IDs, so an old entry
routinely carries a higher number than the newer entries sitting above it. That
is expected and it is not a defect to tidy. Renumbering to restore the
correlation would invalidate every Changelog line, every `Supersedes D-nnn.`
body and every `see D-nnn` tail already naming the old ID -- and a second
backfill arriving later would break it again anyway. **The date field carries
chronology; the ID carries identity.** Order in the file comes from insert
position, per [Ordering](#ordering), never from the number.

Within one run, IDs are allocated in the order the entries appear in the
proposal. Nothing requires that order to be chronological.

Past `999` the number simply grows to four digits.

IDs are what let `log` update an existing entry instead of appending a near
duplicate, and what let the Changelog name precisely what changed.

Context links carry no ID. Nothing updates them by reference.

### Approximate dates

`<date>` is always a real `YYYY-MM-DD` and always the best date known for what
the entry records. A backfill regularly meets a source that never recorded one:
a decision register with no date column, a wiki page whose only timestamp says
when somebody last edited it rather than when the call was made. For those, the
entry's **body opens with the literal `Approximate date.`** and then says where
the approximation came from.

```markdown
- 2026-03-01 -- D-007 -- @unassigned -- Approximate date. Taken from the decision register, which records no dates; that page was first published in March 2026. Pin the vendor SDK to a major version.
```

Three rules make that safe.

**The marker never licenses inventing a date.** It marks a date *the user
supplied* as approximate. `log` does not choose one, does not fall back to
today, and does not read one off a file's modification time. An entry whose date
the user cannot even approximate is still not written -- that rule is unchanged.
What the marker adds is somewhere for a run to go once the user does supply an
approximation, instead of stalling on a date nobody can produce exactly.

**An approximation is normalized to the first day of the coarsest unit given**,
and the proposal says so before anything is written: "March 2026" becomes
`2026-03-01`, "sometime in 2025" becomes `2025-01-01`. That is arithmetic on
what the user said, not a guess at what they meant. Because the derivation has
to be approved rather than announced afterwards, **an approximate date is never
written on `log`'s same-turn dictated path** -- a run that needs this marker
proposes and waits like any other.

**Nothing downstream treats the entry differently.** The marker is ordinary body
text, so every skill already reads and shows it, and an approximate date feeds
`gaps`'s staleness arithmetic exactly like an exact one. Marking it is what
stops a later reader taking a placeholder for a record.

`Approximate date.` is one of five **body markers** that may open a body. When
an entry needs more than one, they run in the fixed order
[Body markers](#body-markers) sets out -- `Supersedes D-nnn.` first and
`Approximate date.` last: `-- Supersedes D-002. Approximate date. <body>`.

### Body markers

Five literal sentences may open a body, ahead of the body proper. Each records
something about the entry that the four fields have nowhere to put.
`Supersedes D-nnn.` and `Approximate date.` are the two this contract has
always carried; the three below them are the newer set.

| Marker | Records | Defined in |
|---|---|---|
| `Supersedes D-nnn.` | This decision replaces an earlier one. | [Section: Decisions](#section-decisions) |
| `Imposed.` | The decision was made outside this group and is binding on it. | [A decision imposed from outside](#a-decision-imposed-from-outside) |
| `Blocked by <id>.` | This entry cannot progress until the named one is settled. | [Relationships between entries](#relationships-between-entries) |
| `Contradicts <id>.` | This entry and the named one cannot both stand as written. | [Relationships between entries](#relationships-between-entries) |
| `Approximate date.` | The date field is the user's approximation. | [Approximate dates](#approximate-dates) |

**A marker is ordinary body text.** It sits inside `<body>`, after the third
` -- `, and nothing about parsing changes: the split is still bounded at three,
the tail forms are still exactly the two above, and a ledger written before any
of this existed reads identically. That is the whole reason a relationship is a
convention rather than a third tail form -- a convention costs nothing in the
grammar, cannot make a previously valid body parse as a tail, and can be
tightened into a parsed form later once real use shows which relationships
actually recur.

**When more than one marker applies, they run in this fixed order:**

1. `Supersedes D-nnn.`
2. `Imposed.`
3. relationship markers, in the order they were recorded
4. `Approximate date.`
5. the body proper

```markdown
- 2026-07-04 -- D-009 -- @unassigned -- Supersedes D-003. Imposed. Contradicts O-007. Approximate date. Taken from the architecture board's standards page, which records no dates; it was published in July 2026. Every service writes to the shared audit log.
```

A fixed order is what lets a reader find a marker without reading the whole
body, and what stops two entries recording the same thing from reading
differently.

### Relationships between entries

Supersession is not the only way two entries relate, and it is the only one
this contract used to be able to express. Two more are recorded as body
markers:

| Marker | Means |
|---|---|
| `Blocked by <id>.` | This entry cannot progress until the named entry is resolved or superseded. |
| `Contradicts <id>.` | This entry and the named one cannot both be acted on as written. Somebody has to reconcile them. |

`<id>` is a `D-nnn` or an `O-nnn` in this same ledger. A marker may name an
entry in either section -- an open item contradicting a decision that is
already in force is the case this exists for -- and one entry may carry several
markers, each written as its own sentence.

**Recorded in one direction only.** The entry that is *constrained* carries the
marker; the entry it names carries nothing. This is deliberately unlike
supersession, which is marked on both entries. Supersession answers "is this
decision still in force?", which a reader has to be able to settle from the one
line in front of them. A relationship answers "what else is in play?", which is
a question about the file rather than about the line, and a reader is already
holding the whole file. One direction also cannot disagree with itself: there
is no second marking to fall out of sync, and no second entry for `log` to edit
under an approval nobody gave it.

**Readers scan both directions.** A skill showing an entry shows the markers on
that entry *and* any entry elsewhere in the ledger naming it. One-directional
in the file is not one-directional in the report.

**Recorded only where the source says so.** A relationship is written when the
material states it, never because two entries look related to whoever is
writing. Inferring a block or a contradiction produces a graph nobody agreed
to, and the no-invention rule outranks the convenience of a richer one.

**A marker naming an ID that resolves to no entry is reported, not repaired.**
Say which entry carries it and which ID it names, then continue -- the same
handling a Changelog ID that resolves to nothing already gets.

```markdown
- [ ] 2026-08-19 -- O-008 -- @sam -- Blocked by O-007. Contradicts D-009. Confirm whether the gateway can be exempted from the shared audit log.
- 2026-07-04 -- D-009 -- @unassigned -- Imposed. Published by the platform programme's architecture board. Every service writes to the shared audit log.
```

**Settling the named entry does not rewrite the marker.** `O-008` still reads
`Blocked by O-007.` after `O-007` is resolved, and a reader takes the block as
lifted from `O-007`'s own checkbox. Nothing sweeps the file to retire markers,
and removing one is an ordinary edit somebody has to ask for. The alternative
is a write that touches entries the user never named, which is the same
objection that keeps relationships one-directional.

### A decision imposed from outside

A body opening with the literal `Imposed.` records that the decision was made
**outside the group keeping this ledger and is binding on it** -- a platform
team's published standard, a security policy, a term in a customer contract.
An entry without the marker was decided by the people keeping the record. There
is no marker for that case: it is the ordinary one, and marking it would mean
editing every entry already written.

The marker is followed by **who imposed it**, in ordinary prose, exactly as
`Approximate date.` is followed by where the approximation came from.

```markdown
- 2026-07-04 -- D-009 -- @unassigned -- Imposed. Published by the platform programme's architecture board. Every service writes to the shared audit log.
```

What it changes is the correct response. A decision this group made can be
reopened by this group; an imposed one can only be complied with, exempted or
escalated. Written without the marker the two read identically -- and for a
project embedded in a programme it does not control, most of the record is the
second kind.

**`<owner>` still means attribution, and `@unassigned` is still not a gap.** An
imposed decision is frequently unowned, because nobody on this side made it;
that is the honest attribution rather than a hole in the record. `gaps` reads
only Open items and that does not change here. What *is* auditable is the work
the decision creates on this side -- comply, seek an exemption, escalate -- and
that work is an Open item, which `gaps` already reports when it is unowned.
`log` offers to raise it and never writes one unasked.

## Section: Decisions

Settled calls. Plain bullets, newest first.

`<owner>` is who the decision is attributed to. `@unassigned` is valid and means
no individual is attributed, which is normal for a group call and normal again
for a decision marked `Imposed.`, where nobody on this side made it. It is
**not** a gap: `gaps` reads only the Open items section, so an unowned decision
is never reported, and attribution is not accountability. See
[A decision imposed from outside](#a-decision-imposed-from-outside).

A decision is never deleted when it is superseded. Supersession is recorded
**on both entries**, so that "is this decision still in force?" is answerable by
looking at that one line:

- The new decision opens its body with the literal `Supersedes D-nnn.`
- The old decision gains the tail ` -> superseded by D-nnn`.

```markdown
- 2026-08-14 -- D-006 -- @carlos -- Supersedes D-002. The ledger lives in .daikenja/, not docs/ -- docs/ is frequently published.
- 2026-08-08 -- D-002 -- @carlos -- The ledger lives in docs/. -> superseded by D-006
```

Marking only the new entry would force a reader to scan every other decision's
body before trusting any single one. The tail is what keeps the check local.

**The tail is authoritative.** If the two markings disagree -- a body claims
`Supersedes D-002.` but `D-002` carries no tail, or a tail names a decision that
does not claim it -- treat the tail as the status and **report the mismatch**,
naming both IDs. Do not repair it. Only `log` writes.

## Section: Open items

Things not yet settled. **Markdown task items**, newest first.

- `- [ ] ` is open.
- `- [x] ` is resolved.

Resolving flips the checkbox and appends a tail to the body:

```
 -> resolved <YYYY-MM-DD>[, see D-nnn]
```

The `see D-nnn` part is present only when the resolution was itself recorded as
a decision. Many items resolve by being done, not by being decided.

Resolved items stay in place. They are not moved to Decisions, not struck
through, and not deleted. The checkbox is the filter: `gaps` and `summary` read
only `- [ ] ` lines.

There is no automatic archiving in v1. To clear out old resolved items, ask
`log` to delete them, so a `-O-nnn` line is written and the Changelog stays
complete.

Nothing stops a human editing the file by hand, and that is fine -- it is a
markdown file, not a database. But a hand deletion leaves the Changelog naming
an entry that no longer exists. **A skill that cannot resolve a Changelog ID to
an entry says so in one line and continues.** It does not fail, and it does not
rewrite the Changelog.

`<owner>` is who is on the hook. `@unassigned` means nobody is, and `gaps`
reports exactly those.

## Section: Context links

A flat reference list. No ID, no date, no owner, no ordering rule.

```
- <label> -- <url or path>
```

Split on ` -- ` **once**: the label is first, the target is everything after. A
label must not contain ` -- `.

This is a convenience index, not a source of truth. A link here may also appear
inside an entry body, and that duplication is expected -- the entry says why the
link mattered on a given date, the index says where to find things.

Context links carry no ID, but their writes are still recorded in the
Changelog. Adding one appends `+link "<label>"`; removing one appends
`-link "<label>"`, quoting the label because -- unlike an ID -- it may contain
a comma and the Changelog summary field is comma-separated. There is no edit
verb: a link's target cannot be updated in place, so changing one is a removal
of the old label and an addition of the new one, in that order.

## Section: Sources

The documents this project is tracked from -- wiki pages, ticket epics,
threads, repositories, usually owned by somebody else -- each with the reading
state a context link has nowhere to put. A source records where a thing is,
when its own system last says it changed, when it was last read, what it
covers, and what it deliberately does not answer.

A source is a **head line** followed by indented **field lines**:

```
- <id> -- <label> -- <url or path>
  modified: <value as reported by the source system>
  read: <YYYY-MM-DD>
  covers: <free text>
  does not answer: <free text>
```

**The head line splits on ` -- ` at most twice**: id, label, target. The
target is the last field, so it may contain ` -- `; the label must not, same
as a context link's. This is deliberately a different line shape from the
entry grammar: a source carries more fields than the three-split bound allows,
and that bound is frozen. Nothing about parsing Decisions or Open items
changes here.

**Field lines are continuation lines** -- indented two spaces, no list marker
-- which is what makes this section safe to add: every reader already treats
such lines as continuations (§ Reading rules, rule 3), so a ledger carrying
sources still reads correctly where nothing knows what a source is. Each field
line is `<name>: <value>`, one per line, these exact names, in this fixed
order, each at most once:

| Field | Holds |
|---|---|
| `modified:` | The last-modified value the source's own system reports, verbatim -- usually a timestamp, a revision or version where that is what the system exposes. |
| `read:` | The date the source's content was last actually read, `YYYY-MM-DD`. |
| `covers:` | What the source answers, one line. |
| `does not answer:` | What the source deliberately does not answer, one line. This is the field that saves the most re-reading: most of it is re-opening a page to rediscover that it never addressed the question. |

**Every field is optional, and an absent field means unknown.** Nothing ever
invents a value to fill one: a system that reports no last-modified leaves
`modified:` unwritten, and a skill says the value is unknown rather than
substituting a fetch date, a guess, or today. This is the no-invention rule
dates already follow, applied to two more facts.

**`modified:` and `read:` move together.** `modified:` is the value the
source's system reported when the source was last read, and `read:` is when
that was -- together they are the baseline a staleness check compares against.
The check is a comparison for difference, not date arithmetic: a source has
moved when the value its system reports now differs from the stored one, which
is also why `modified:` is stored verbatim rather than normalized. Updating
`modified:` without the source actually having been re-read would erase
exactly the signal the field exists to carry, so no skill does it.

A source with no `modified:` has **no baseline**: nothing can say whether it
moved, only when it was last read. The baseline is established the first time
a read is recorded together with the value the system reported at that moment.

Sources are written like everything else in the ledger: by `log`, on the
user's approval, with a Changelog line. Adding one appends `+S-nnn`; editing
one -- including recording a refresh's new `modified:` and `read:` values --
appends `~S-nnn`; deleting one appends `-S-nnn` and retires the ID. `resolved`
and `superseded` never apply to a source: a source is a place, not a question,
so it is either tracked or it is not.

**A source is not a context link, and neither replaces the other.** The
Context links section stays exactly what it is -- a flat convenience index
with no ID and no state. A source is for a document the project is *tracked
from*, where knowing whether it moved is the point. The same target may
legitimately appear in both, and nothing migrates a link into a source: that
is an ordinary pair of user-approved writes, a `+S-nnn` and (only if asked) a
`-link`, each recorded in the Changelog.

```markdown
## Sources

- S-002 -- Rollout epic -- https://example.com/tickets/EPIC-204
  read: 2026-08-15
  covers: delivery order and the dates each phase is committed to.
- S-001 -- Platform standards page -- https://example.com/wiki/standards
  modified: 2026-08-10T09:12Z
  read: 2026-08-11
  covers: the mandatory controls and which services they bind.
  does not answer: rollout timing; the page scopes controls, not schedules.
```

`S-002` has no baseline -- its system reported no last-modified value when it
was read -- so a check can say when it was last read, never whether it moved.

## Section: Changelog

One line per write, newest first:

```
- <timestamp> -- <writer> -- <summary>
```

| Field | Rule |
|---|---|
| `<timestamp>` | `YYYY-MM-DDThh:mmZ`. UTC, minute precision. |
| `<writer>` | The skill that wrote. `project-log`, or `project-log via <skill>` when another skill wrote through it. Ledgers written before 0.3.0 name the writer `log` instead. |
| `<summary>` | Comma-separated changes, **by ID**, one verb each: `+D-009` (created), `~O-003` (edited), `resolved O-004`, `superseded D-002`, `-O-002` (deleted), `+link "<label>"` (context link added), `-link "<label>"` (context link removed). |

Split on ` -- ` **at most twice**. The summary is the last field, so it may
contain `--` like any other body text.

`superseded` is its own verb rather than a plain edit. A decision going out of
force and a typo fix are not the same event, and a reader of the Changelog alone
should be able to tell them apart.

A source is named by its ID like any entry and takes exactly the three symbol
verbs -- `+S-002` (added), `~S-002` (edited), `-S-002` (deleted). `resolved`
and `superseded` never apply to one, per
[Section: Sources](#section-sources).

Naming IDs rather than counts is what makes `catchup` cheap. It reads changelog
lines newer than `last_checkpoint`, collects the IDs, and pulls those entries.
It never has to diff the file.

**The Changelog must be complete.** Every *change to an entry* -- a creation, an
edit, a resolution, a supersession, a deletion -- appears in exactly one
changelog line. Context link additions and removals are recorded the same way,
by label instead of ID; see
[Section: Context links](#section-context-links).
This is per change, not per entry: an entry that is created and later resolved
appears in two lines, one for each event. A change that happened without a line
recording it is a bug, not a shortcut: `catchup` would never report it, and
nothing else would notice. When one `log` run touches several entries, they all
go on that run's single line.

The Changelog is not capped and is never trimmed automatically. Silent trimming
would write to the ledger without a human approving it.

### Compacting a long summary

One line per write is right for an incremental run, and produces for a bulk
write a single unbroken line naming thirty-odd IDs. It parses correctly and it
is unreadable. Two compactions are allowed. **Both are lossless** -- every ID
and every label that would have been listed is still recoverable from the line,
which matters because `catchup` reads this line and never diffs the file.

**Consecutive IDs may be written as a range**, `<verb><first>..<last>`:

```
- 2026-08-21T10:15Z -- project-log via setup-project -- +D-001..D-017, +O-001..O-009
```

- Both endpoints are in the same section, and the range is **inclusive and
  dense**: every ID between them was touched by that same verb in that run. A
  range is never sparse. If one ID in the interval was untouched, or took a
  different verb, write two ranges or list the IDs.
- The endpoints must differ. A single ID is written plainly.
- The word verbs range too: `resolved O-004..O-006`, `superseded D-002..D-004`,
  and so do `~D-001..D-003` and `-O-011..O-013`.
- **Expanding is the reader's job.** `+D-001..D-017` means exactly what
  seventeen comma-separated `+D-nnn` items mean, and a skill reports it that
  way. A range a skill does not expand is a set of changes nobody is told about.

**A summary may continue on continuation lines**, indented two spaces and
carrying no list marker, exactly as an entry's detail does:

```
- 2026-08-21T10:15Z -- project-log via setup-project -- +link "Decision register",
  +link "Rollout channel export", +link "Vendor evaluation sheet",
  +link "On-call rota"
```

A reader strips each continuation line's indent and joins it to the summary with
a single space, then splits on commas as usual. This is what keeps context links
readable: a link is named by its quoted label rather than by an ID, so labels
have no order to range over and would otherwise have no compaction at all.
Continuation lines are already ignored by the grammar check
([Reading rules](#reading-rules-for-skills), rule 3), so nothing already on disk
changes meaning.

Neither compaction is required, and neither belongs on a short line. A run that
names four IDs writes the four IDs.

## Reading rules for skills

1. Locate a section by its exact H2 heading. Do not infer sections by position.
2. Ignore HTML comments (`<!-- ... -->`) and blank lines.
3. A line indented by two or more spaces and carrying no list marker is a
   **continuation** of the entry above it. It is not expected to match the entry
   grammar and must never be reported as malformed.
4. Any other line inside a section that does not match the grammar is
   **reported, not silently skipped**. Say which line and what is wrong, then
   continue.
5. A Changelog summary item that **looks like a range and cannot be expanded**
   -- endpoints in two different sections, or running backwards -- is reported
   the same way, naming the line and what is wrong, then skipped. Rule 4 does
   not reach it: the line itself is well formed, and only the item inside it is
   not. Do not guess at what it meant, and never expand it partially.
6. A **body marker naming an ID that resolves to no entry** -- `Blocked by
   O-014.` where this ledger has no `O-014` -- is reported the same way, naming
   the entry that carries it and the ID it names, then read past. Rule 4 does
   not reach it either: the line is well formed and only the reference inside
   it is not. Do not guess which entry was meant.
7. Never rewrite the file to normalize it. Only `log` writes.
8. A ledger **missing one of the four required H2 sections** (Decisions, Open
   items, Context links, Changelog) is not read past silently. Report which
   heading is missing, then ask the user whether to continue over the sections
   that are present, and wait for the answer before reading any further. A
   "no" ends the run without reading anything else. Name
   `/daikenja:project-log` as the repair path -- it is the only skill that
   writes a missing heading. This rule governs the read skills
   (`project-summary`, `project-gaps`, `project-decisions`, `project-catchup`,
   `project-sources`); `project-log`'s own hard stop on the same defect, in its
   failure table, is unchanged. It does not reach `## Sources`, whose absence
   is never a defect -- see § File skeleton.

## Worked example

A complete ledger exercising every awkward case: unowned entries in both
sections (`D-004`, `O-006`, `O-001`), entries carrying no link (most of them), a
resolved item that links a decision (`O-003`) and one that does not because it
was resolved by being done (`O-002`), continuation lines (`D-003`, `O-004`), a
body containing ` -- ` as punctuation (`D-005`), and a supersession marked on
both entries (`D-005` and `D-002`).

```markdown
# Atlas migration ledger

## Decisions

- 2026-08-14 -- D-005 -- @carlos -- Supersedes D-002. Cut over on a Saturday, not a weekday evening -- the rollback window is four hours and nobody wants that on a work night. [runbook](https://example.com/atlas/runbook)
- 2026-08-12 -- D-004 -- @unassigned -- Keep the legacy read replica online for 30 days after cutover.
- 2026-08-11 -- D-003 -- @priya -- Freeze schema changes from 2026-08-20 until cutover completes.
  Two teams have pending migrations. Both agreed to hold. The freeze is
  announced in the release channel, not enforced by tooling.
- 2026-08-08 -- D-002 -- @carlos -- Cut over on a weekday evening. [thread](https://example.com/t/4417) -> superseded by D-005
- 2026-08-05 -- D-001 -- @priya -- Atlas replaces the legacy store. No dual-write period.

## Open items

- [ ] 2026-08-14 -- O-006 -- @unassigned -- Decide who is on call during the cutover window.
- [ ] 2026-08-13 -- O-005 -- @sam -- Confirm the 30-day replica cost with finance. [budget sheet](https://example.com/atlas/budget)
- [ ] 2026-08-11 -- O-004 -- @priya -- Write the rollback runbook and dry-run it once.
  The dry run needs a full-size dataset. Staging currently holds a 10% sample,
  so this is blocked on a refresh.
- [x] 2026-08-09 -- O-003 -- @carlos -- Pick the cutover day. -> resolved 2026-08-14, see D-005
- [x] 2026-08-07 -- O-002 -- @sam -- Get the legacy store's row counts from ops. -> resolved 2026-08-08
- [ ] 2026-08-05 -- O-001 -- @unassigned -- Agree the success criteria for calling the migration done.

## Context links

- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md

## Changelog

- 2026-08-14T16:40Z -- log -- +D-005, superseded D-002, resolved O-003, +O-006
- 2026-08-13T09:12Z -- log via meeting-review -- +O-005, ~D-003
- 2026-08-12T10:20Z -- log -- +D-004
- 2026-08-11T11:05Z -- log -- +D-003, +O-004
- 2026-08-09T15:30Z -- log -- +O-003
- 2026-08-08T08:30Z -- log -- +D-002, resolved O-002
- 2026-08-07T09:45Z -- log -- +O-002
- 2026-08-05T14:00Z -- log -- +D-001, +O-001
```

What a skill reads out of that example:

- **Five decisions**, `D-001` through `D-005`, of which **four are in force**.
  `D-002` stays in the file carrying a `-> superseded by D-005` tail, so no
  reader has to scan the other four to know its status. `D-004` is unowned,
  which is not a gap. `D-003` carries a continuation block.
- **Six open items**, `O-001` through `O-006`. Four are still open (`O-006`,
  `O-005`, `O-004`, `O-001`) because their boxes are unchecked. Two are resolved
  (`O-003`, `O-002`); only `O-003` names a decision, because `O-002` was
  resolved by being done.
- **Two unowned open items**, `O-006` and `O-001`. That is what `gaps` reports
  as unowned. Whether any of the four is also *stale* depends on
  `stale_after_days` and the date the skill runs.
- `D-005`'s body contains ` -- ` as punctuation. It is still one decision, not
  two fields, because the split stops after `@carlos`.

## Worked example: a bulk backfill

The same ledger a week later, after an existing project's history was recorded
in one run. Four things in it are only well-defined because of the rules above.

```markdown
## Decisions

- 2026-08-14 -- D-005 -- @carlos -- Supersedes D-002. Cut over on a Saturday, not a weekday evening.
- 2026-08-12 -- D-004 -- @unassigned -- Keep the legacy read replica online for 30 days after cutover.
- 2026-06-02 -- D-007 -- @priya -- Atlas runs in eu-west-1 only. No multi-region until after cutover.
- 2026-03-01 -- D-006 -- @unassigned -- Approximate date. Taken from the architecture wiki, which records no dates; the page was created in March 2026. Buy the managed Atlas tier rather than self-hosting.

## Changelog

- 2026-08-21T10:15Z -- project-log via setup-project -- +D-006..D-007, +O-007..O-009,
  +link "Architecture wiki", +link "Vendor evaluation sheet"
- 2026-08-14T16:40Z -- log -- +D-005, superseded D-002, resolved O-003, +O-006
```

- **The two backfilled decisions sort by date, not to the top.** `D-007` lands
  between `D-004` and `D-006` because 2026-06-02 does, which is
  [Ordering](#ordering) read as a position.
- **Their IDs are the highest in the section and their dates the oldest.** That
  decorrelation is the expected outcome of never renumbering, per
  [IDs](#ids). A reader takes chronology from the date field.
- **`D-006` carries the `Approximate date.` marker** because the wiki recorded
  none and the user could only place it in March 2026.
- **The Changelog line is ranged and continued.** Expanded, it says
  `+D-006, +D-007, +O-007, +O-008, +O-009` and two link additions -- nothing is
  lost, and `catchup` reports all seven changes.

Entries dated to their true origin are older than `stale_after_days` the moment
they land, so `gaps` reports the open ones as stale on the next run. That is the
audit working as specified, not a fault in the entries; `setup-project` says so
before a seed run for exactly this reason.
