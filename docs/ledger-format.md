# Ledger format

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

Four H2 sections, these exact names, always in this order, always all four
present even when empty:

```markdown
# <project> ledger

## Decisions

## Open items

## Context links

## Changelog
```

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
have no ordering rule at all, so a new one goes directly under the heading.

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

| Field | Rule |
|---|---|
| `<marker>` | `- ` in Decisions. `- [ ] ` or `- [x] ` in Open items. |
| `<date>` | `YYYY-MM-DD`, absolute, never relative. The best known date the entry's subject was decided or raised. For an incremental write that is the day it is written; for a backfill it is the original date. See [Approximate dates](#approximate-dates). |
| `<id>` | `D-001` in Decisions, `O-001` in Open items. See [IDs](#ids). |
| `<owner>` | `@` plus one token, no spaces. `@unassigned` when there is none. |
| `<body>` | Free text on one line. May contain `--`. May end with markdown links. |

Every field is always present. A field is never omitted to signal absence --
`@unassigned` is written out, because positional parsing depends on the field
count and because `gaps` searches for exactly that token.

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

`D-` for Decisions, `O-` for Open items, followed by a zero-padded three-digit
number. Sequences are per section and per ledger. They start at `001`, increase
by one, and are **never reused** -- a deleted entry's ID stays retired.

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

When an entry needs this and a supersession marking both, `Supersedes D-nnn.`
comes first: `-- Supersedes D-002. Approximate date. <body>`.

## Section: Decisions

Settled calls. Plain bullets, newest first.

`<owner>` is who the decision is attributed to. `@unassigned` is valid and means
no individual is attributed, which is normal for a group call. It is **not** a
gap: `gaps` reads only the Open items section, so an unowned decision is never
reported.

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
6. Never rewrite the file to normalize it. Only `log` writes.

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
