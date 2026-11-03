<!-- daikenja-open-format: 1 -->
# `open.md` format

A project's ledger is two files: `DECISIONS.md`, which holds the decisions still
in force, and `open.md`, which holds what is still unsettled, where the
project's context lives and which documents it is tracked from. This document is
the contract for `open.md`, and for the version rule both files follow inside
Daikenja. `DECISIONS.md` itself is specified by
[`decisions-format.md`](decisions-format.md), a byte-identical copy of the
format plan-staged-rollout shares; nothing Daikenja-specific is ever added to
that copy.

Both files record what is true now. Git is the history: neither file carries
IDs, a changelog, or entries kept around after they stop being true.

## Location

**`.daikenja/open.md` in the project's home repository.** The home repository is
the first entry of the project's `paths` in `daikenja.yaml`, so a project
spanning several repositories keeps one `open.md`, in the first one registered.
The path is fixed: there is no config key that moves it.

`DECISIONS.md` sits at the root of **every** registered repository, because a
decision belongs with the code it constrains. A project spanning three
repositories has three `DECISIONS.md` files and one `open.md`.

Every project lives in a git repository. Git is what keeps the history of both
files, so a project with no repository has nowhere to keep one.

## Version line

The first line of `open.md` is its format-version line:

```
<!-- daikenja-open-format: 1 -->
```

The first line of `DECISIONS.md` is `<!-- decisions-format: 1 -->`, as
[`decisions-format.md`](decisions-format.md) § Version sets out. The two numbers
move independently: the shared format changes only when both plugins agree, and
this one changes only when `open.md`'s shape below changes in a way an older
reader would misread.

What a skill does with the line, for either file:

- **The version it knows:** read or write as normal.
- **A newer version than it knows:** a reading skill still reads the file and
  warns **once per run** that it was written by a newer format and the plugin
  needs an update. `project-log` refuses to write that file and asks the user
  to update the plugin first; it writes nothing else in that batch either,
  because a half-applied batch is worse than none.
- **No version line:** the file is read as version 1. `project-log` adds the
  line in its next approved write to that file, and the proposal shows it.
- **A version line that does not parse**, such as one with no number: reported
  as malformed, then the file is read as version 1.

## File skeleton

```markdown
<!-- daikenja-open-format: 1 -->
# <project> open items

## Open items

## Context links

## Sources
```

Three H2 sections, these exact names, always in this order, always present even
when empty. The H1 is free text and carries no meaning. There is no Changelog
section and no Decisions section: decisions go to `DECISIONS.md`, and the record
of what changed is `git log`.

`project-log` scaffolds a missing `open.md` from
[`../templates/open.md`](../templates/open.md), with `{{PROJECT}}` replaced by
the project name, and a missing `DECISIONS.md` from
[`../templates/DECISIONS.md`](../templates/DECISIONS.md) as it stands.

## Section: Open items

Things not yet settled. One bullet per item:

```
- <date raised> -- <owner> -- <text>
```

The separator is ` -- ` (space, two hyphens, space). **Strip the `- ` marker,
then split on ` -- ` at most twice.** Everything after the second separator is
the text, verbatim, so the text may contain ` -- ` of its own.

| Field | Rule |
|---|---|
| `<date raised>` | `YYYY-MM-DD`, absolute, never relative: the best known date the item was raised. Never invented: when nobody can say, `project-log` asks rather than falling back to today. |
| `<owner>` | `@` plus one token, no spaces. `@unassigned` when nobody is on the hook; `project-gaps` reports exactly those. |
| `<text>` | Free text on one line. May end with markdown links. |

Every field is always present. An item may carry detail on following lines
indented by two spaces, with no list marker; the first line must still stand
alone as the item in summary.

```markdown
- 2026-08-19 -- @sam -- Blocked by: the audit log exemption. Confirm whether the gateway can skip the shared audit log.
- 2026-08-14 -- @unassigned -- Decide whether the audit log exemption needs the board's sign-off.
  The board meets monthly; the next agenda closes on the 25th.
```

**An item has no ID.** It is found by its words: `project-log` matches the
item a user names against the text on each line and asks when more than one
could match.

**`<owner>` is a handle, not an identity.** Which person `@priya` means is
recorded, when the user records it, under the `Known as` field of
`personas.md`. A handle missing from that file is the normal case and is never
an error.

### `Blocked by:`

An item that cannot progress until another one is settled opens its text with
the literal prefix `Blocked by:`, then **the other item in words**, then a
period:

```
Blocked by: <the other item, named in words>. <the rest of the text>
```

The prefix runs to the first period followed by a space or the end of the line,
so the name inside it must not contain one. It is ordinary text: the split
above is unchanged, and a reader that knows nothing of the prefix still reads
the item correctly.

The prefix is written only where the source says the item is blocked, never
because two items look related. It is the one marker this format keeps:
`project-gaps` annotates it, and nothing else reads it.

When the named item is no longer in the file, it has been closed: a reader
says the block names an item that is no longer open, and reads on. When
`project-log` closes an item that another item names in its `Blocked by:`, its
proposal offers to drop that prefix in the same batch.

### Closing an item

**Closing an item deletes its line**, with its continuation lines. There is no
checkbox, no resolved tail and nothing kept in place: the deletion is the
record, and `git log -p -- .daikenja/open.md` shows it. When an item closes
because something was decided, `project-log` proposes the `DECISIONS.md` entry
in the same batch as the deletion.

### Ordering

A new item goes directly under the heading. No skill depends on the order, and
a person is free to reorder items by hand; `project-log` inserts a line and
never moves the lines around it.

## Section: Context links

A flat reference list. No date, no owner, no ordering rule.

```
- <label> -- <url or path>
```

Split on ` -- ` **once**: the label is first, the target is everything after.
A label must not contain ` -- `. A link here may also appear inside an item's
text; that duplication is expected.

## Section: Sources

The documents the project is tracked from, each with the reading state a
context link has nowhere to put. A source is a head line, the same shape as a
context link, followed by optional field lines indented two spaces, these exact
names, in this order, each at most once:

```
- <label> -- <url or path>
  modified: <value as reported by the source system>
  read: <YYYY-MM-DD>
  covers: <free text>
  does not answer: <free text>
```

The head line splits on ` -- ` once, as a context link does. Every field is
optional and an absent field means unknown: nothing invents a value to fill
one. `modified:` is stored verbatim, and it and `read:` change together, only
when the source has actually been re-read. A source is a place, not a question:
it is tracked or deleted, never closed.

## Writing

Only `project-log` writes either file, and only in one batch the user approves.
It never commits: the files change in the working tree, and the user commits
them with the work they belong to. `project-catchup` lists uncommitted changes
to either file as not committed yet, so a pending write is never invisible.

`DECISIONS.md` carries no markers of any kind. A decision imposed from outside
says so in its why clause ("imposed by the architecture board"), and a
contradiction is resolved when the entry is written, never recorded.

## Reading rules for skills

1. Read the version line first, per § Version line.
2. Locate a section by its exact H2 heading, never by position.
3. Ignore other HTML comments and blank lines.
4. A line indented by two or more spaces with no list marker continues the item,
   link or source above it, and is never reported as malformed.
5. Any other line inside a section that does not match its grammar is
   **reported, not silently skipped**: say which line and what is wrong, then
   continue.
6. A missing required H2 section is reported by name; ask the user whether to
   continue over the sections present, and name `/daikenja:project-log` as the
   repair path.
7. Never rewrite either file to normalize it. Only `project-log` writes.
