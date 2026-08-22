# Reading and writing a Drive pointer

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § One folder, always -- setup-user "Offering Google Drive, without ever requiring it"
- § Writing replaces the file -- learn-voice "Step 7: write", remember-persona "Step 5: write"

The Google Drive-specific mechanics for a `drive:` pointer: finding the
`daikenja` folder, reading a file safely, and the replace sequence a write
follows. Companion to
[`config-resolution.md`](config-resolution.md) § Resolving `writing_style` and
`personas`, which defines the three pointer forms and defers the Drive-specific
detail here.

A Drive pointer is reached through the Google Drive connector, in the user's own
session under their own Google account. Daikenja holds no Google credential and
stores nothing on anyone else's infrastructure.

**Daikenja can only see files it created.** The connector's access covers the
files the app itself created and nothing else. A document the user uploads,
writes in Drive by hand, or has shared with them is invisible here, however
widely it is shared. One rule follows and it is not negotiable: **there is no
"point at a file you already have" path.** Either `setup-user` creates the file,
or the key stays on a local path. A pointer typed by hand at a file Daikenja did
not create will never resolve.

## One folder, always

Daikenja's Drive files live in a single folder named **`daikenja`**, created by
`setup-user` in the user's own Drive. This mirrors `~/.claude/daikenja/`
locally, and it is fixed for the same reason that path is: one location, always,
with no search path to reason about. Nothing Daikenja writes to Drive is left
loose at the top level.

**The folder is not part of the pointer.** A pointer stays a bare file name --
`drive:personas.md`, never `drive:daikenja/personas.md`. The folder is implied
because it is fixed, and writing it into the value would make a pointer a path
again, which is exactly what the name-only rule exists to avoid.

**Resolution searches by name, inside that folder.** First find the `daikenja`
folder among the files Daikenja created, then search it for the exact name in
the pointer. Both searches follow the paging rule below, and the folder obeys
the same match rules as a file: exactly one `daikenja` folder resolves, none or
several does not.

- **Exactly one match.** That file is the target.
- **No match.** The pointer does not resolve. So does a missing folder: if the
  folder is gone, there is nothing to search and the pointer fails as a whole
  rather than falling back to a top-level search.
- **More than one match.** The pointer does not resolve. Two files sharing a
  name means an earlier write was interrupted between its create and its trash
  step. Which copy to keep is the user's call and never a guess.

**Pass an explicit page size and read every page.** The search tool's default
page size is **one**. Measured 17 August 2026: a name carried by two files
returned only the older one under the default, and the duplicate appeared only
once `pageSize` was set explicitly. Counting matches from a default-sized first
page therefore misses duplicates and resolves silently to the stale copy --
which is the exact outcome the "more than one match" rule exists to prevent, and
after an interrupted write it is the copy missing the user's newest entry. A
page token comes back even when there is only one match, so its presence never
means "more results"; page until the response is empty.

**Reading downloads the file's bytes.** Use the connector's file-download tool
(`download_file_content`), never its content-reading or natural-language
extraction tool (`read_file_content`).

Measured 17 August 2026, both tools against the same 171-byte Markdown file:
`download_file_content` returned it byte-exact, while `read_file_content`
returned a lossy rendering -- Markdown syntax backslash-escaped (`\#`,
`\- \[ \]`, `\[link\]`) and trailing hard-break spaces added. **That text is not
the file.** Reading it would misreport the user's prose, and splicing an entry
into it and writing it back, per the sequence below, would permanently corrupt
prose the user wrote by hand. The extraction tool is built to describe a
document to a reader, not to round-trip one.

## Writing replaces the file

The connector cannot update a file's content. Its update tool changes the title
and the parent folder only. A write is therefore a replacement, in this order:

1. Download the current content.
2. Build the new full content in memory, as the downloaded content with the
   change spliced into it.
3. Create a new file with the same name and that content, **in the `daikenja`
   folder**, and **with conversion to Google's own document types disabled**.
4. Download the new file back and confirm it holds what was written.
5. Only then move the old file to the trash.

**The replacement goes in the same folder as the file it replaces.** A create
that omits the parent lands at the top level instead, where a folder-scoped
resolution will not find it. Trashing the old file at step 5 would then strand
the user's prose: the new file exists, holds everything, and no longer resolves.

**Disabling the conversion is not optional.** Measured 17 August 2026: a
203-byte Markdown upload without that flag was stored as a Google Doc and came
back from step 4 at 205 bytes, with trailing hard-break spaces added. The same
upload with the flag set came back byte-identical. Prose that gains characters
on every write is corrupted by degrees, and step 4 is what catches it -- a
read-back that does not match what was written fails the write.

**Never trash first.** A create that fails after a successful trash destroys
prose the user cannot get back. If any step before 5 fails, the old file is
still there and still the one the name resolves to: report the failure and write
nothing further.

**Splice, never regenerate.** The content written in step 2 is the bytes that
came back in step 1 with the change made to them. Never rebuild the file from
memory of what it said. A whole-file replace over prose the user wrote by hand
has no undo, and the only thing keeping it safe is that everything except the
change is carried across untouched.

Between steps 3 and 5 two files carry the name. A run that dies there leaves the
ambiguous state above, and the next resolution stops rather than guessing. That
is the intended outcome: the user deletes the older copy and the name resolves
again.

Only `remember-persona` and `learn-voice` write prose content, and the
pointer's form does not change that; see
[Who writes what](config-writers.md#who-writes-what).

**The pointer names one ordinary file.** Daikenja reads the file it resolved and
follows nothing out of it -- no folders, no linked documents, no second file.

**A configured Drive pointer that fails is a stop, not a degrade.** If the
connector is not in the session, the `daikenja` folder is missing or duplicated,
the name does not resolve to exactly one file inside it, or the download comes
back empty, the run stops and names the file. This is the
one place a pointer's form changes the behavior.

The reason is that none of those failures can be told apart from "this user has
no personas recorded." Continuing would mean drafting in the default voice while
the user believes their own style was applied, and saying nothing about it. **An
empty download is included deliberately, and it is the cautious call**: a read
that returns nothing is either a genuinely empty file or a failed read, and
nothing available here distinguishes them. Treating it as an empty file costs a
`remember-persona` write that replaces the user's prose with a file holding one
entry. Treating it as a failure costs one run. See
[Failure behavior](config-resolution.md#failure-behavior). There is no offline
cache.
