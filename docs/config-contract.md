# Configuration contract

Daikenja reads user configuration from **one YAML file** outside the plugin
directory. This document is the schema, the lookup order every skill follows,
and the behavior when configuration is missing or broken.

Nothing parses this file programmatically. Claude reads it as text and edits it
with the Edit tool. YAML is the format because it takes comments and reads well
at a glance, not because anything deserializes it.

## Location

```
~/.claude/daikenja/daikenja.yaml      configuration and per-project state
~/.claude/daikenja/personas.md       user prose, pointed at by the config
~/.claude/daikenja/writing-style.md  user prose, pointed at by the config
```

**Never inside the plugin directory.** Plugin directories are managed and
overwritten on update, so anything a user filled in there is lost on the next
version. The plugin ships templates; the filled copies live in the path above.

`daikenja.yaml` is always at that one path. The two prose files are only the
default: `writing_style` and `personas` are pointers, and a pointer may name a
file somewhere else or a file in Google Drive. A pointer that names a Drive file
resolves inside one folder, which mirrors the local layout:

```
daikenja/personas.md       in the user's own Google Drive
daikenja/writing-style.md  same folder, created by setup-user
```

See
[Resolving `writing_style` and `personas`](#resolving-writing_style-and-personas).

Three skills write configuration keys, and each owns a different block:
`setup-user` owns `profile:`, `setup-project` owns a project's entry under
`projects:`, and `project-catchup` owns `last_checkpoint` alone. Nothing else
writes this file. See [Who writes what](#who-writes-what).

## Schema

```yaml
profile:
  name: <string>              # required
  role: <string>              # optional
  org: <string>               # optional
  team: <string>              # optional
  domain: <string>            # optional, the subject matter you work in
  tone: standard              # direct | standard | guided. Default: standard
  writing_style: ./writing-style.md   # optional, pointer. Default: local path
  personas: ./personas.md             # optional, pointer. Default: local path
  norms_doc: <path or url>            # optional, absent by default
  stale_after_days: 21                # optional. Default: 21

projects:
  <project-key>:
    path: <absolute path>             # required
    ledger: .daikenja/ledger.md        # optional, relative to path
    last_checkpoint: 2026-08-14T09:12Z  # optional, written by project-catchup
    stale_after_days: <int>           # optional, overrides the profile value
    norms_doc: <path or url>          # optional, overrides the profile value
```

### Field notes

**`profile` holds short scalars only.** Identity is a handful of words per
field, so it lives directly in the YAML. Anything long enough to be prose lives
in a `.md` file that the config points at. There is deliberately no second
mechanism -- no `profile.md`, no free-text identity blob. Two ways to say who
you are is one too many.

**`tone`** scales how much a skill's reply narrates beyond the answer itself.
This document only defines the value and its default; how a skill applies it
to a reply is [`response-format.md`](response-format.md)'s contract, which
every skill's output step follows: `direct` is terse, `guided` adds the
reasoning behind each finding and a closing line, `standard` is the middle and
the default.

**`writing_style` and `personas`** are **pointers**, not fixed paths. A pointer
may be a relative path, an absolute path, or a Google Drive file name. The three
forms, and what happens when one does not resolve, are in
[Resolving `writing_style` and `personas`](#resolving-writing_style-and-personas),
which is the only place the rule is stated -- skills defer to it rather than
restating the branches.

**`norms_doc`** is the team norms or ways-of-working document that
`self-review`'s ROLE CHECK section needs. It is absent by default, and that
section ships off. Configuring it is what turns the section on.

**`stale_after_days`** is how long an open item may sit before `project-gaps` calls it
stale. It measures age from the entry's date field, which is when the item was
raised -- not when it was last touched. Daikenja does not track last-touched,
and "this has been open five weeks" is the signal worth having. Default 21 days.

**`last_checkpoint`** is `YYYY-MM-DDThh:mmZ`, UTC, minute precision -- the same
timestamp format the ledger's Changelog uses. It marks how far `project-catchup` has
already reported.

**The `<project-key>` is a human label and is never used for matching.** Call it
whatever reads well. Matching is by `path`; see below.

## Resolution order

### Finding the configuration

1. `~/.claude/daikenja/daikenja.yaml`. There is no search path and no
   project-local config file. One location, always.

### Finding the current project

A skill resolves which `projects:` entry applies to the directory it is running
in:

1. Normalize the current directory: forward slashes, no trailing slash,
   case-insensitive comparison. (Windows paths compare case-insensitively and
   arrive in both slash styles; normalizing first avoids both traps.)
2. Compare against every `projects:` entry's `path`, normalized the same way.
3. Take the **longest matching prefix**. Nested projects therefore resolve to
   the innermost one.
4. No match means the project is unregistered. Every skill says so in one line
   and then continues -- an unregistered project still has a ledger to read if
   one exists on disk, and a ledger on disk wins over the config (see
   [Finding the ledger](#finding-the-ledger)). `project-log` additionally names
   `setup-project` as the way to register it. The branch a read skill follows is
   in
   [`reading.md`](reading.md) § Step A.

### Finding the ledger

1. The matched project's `ledger:` key, resolved relative to its `path`.
2. Otherwise `.daikenja/ledger.md` under the project root.
3. If the file does not exist, `project-log` scaffolds it from
   [`../templates/ledger.md`](../templates/ledger.md) after the user approves.
   Read skills do not scaffold; they report that no ledger exists and name the
   skill that creates one.

**A ledger found on disk wins over the config.** If `.daikenja/ledger.md` exists
but no `projects:` entry matches, the ledger is used and `project-log` names
`setup-project` as the way to add the missing entry. The file on disk is the
fact; the config is the index.

### Resolving `writing_style` and `personas`

These two keys are pointers. A pointer says where the prose lives; it does not
say which skill may write it. Three forms are legal, and a pointer is exactly
one of them:

| Form | Example | Resolves to |
|---|---|---|
| Relative path | `./personas.md` | That path, relative to `daikenja.yaml`'s own directory. |
| Absolute path | `C:/Users/you/notes/personas.md` | That path. |
| Drive file name | `drive:personas.md` | The file with exactly that name in Daikenja's own `daikenja` folder in Google Drive. |

A value starting `drive:` is a Drive pointer. Anything else is a path. What
follows `drive:` is a **file name** -- not a path, not a URL, and not a file ID.
The reason is in [Writing replaces the file](#writing-replaces-the-file): every
write creates a new file with a new ID, so a stored ID is wrong the first time
the user's prose changes. The name is the only handle that survives a write.

**Local paths are the default and stay the default.** The shipped template
points both keys at local files, and a user who never mentions Drive sees
exactly the behavior described everywhere else in this document. Drive buys one
thing: reaching these settings from a machine or a session other than the one
that wrote them. The connector's grant spans surfaces, so a file created in a
Claude Code session is readable from claude.ai and the other way round
(verified 17 August 2026).

**The two keys resolve independently.** Pointing `writing_style` at a Drive file
while `personas` stays on a local file is a normal configuration, not a
half-migrated one. Persona notes are about real colleagues, and keeping them
local while sharing a writing style is a reasonable thing to want.

**Drive is the only remote store.** There is no second backend and no plugin
setting that selects one. A pointer is a path or it is `drive:`.

#### Reading and writing a Drive pointer

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

##### One folder, always

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

##### Writing replaces the file

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

Only `remember-persona` writes prose content, and the pointer's form does not
change that; see [Who writes what](#who-writes-what).

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
[Failure behavior](#failure-behavior). There is no offline cache.

### Precedence

**Project overrides global, key by key.** A project supplying
`stale_after_days` uses its own; a project omitting it inherits the profile's.
There is no deep merge beyond this -- keys are scalars.

**A skill states which it used** whenever the answer would change the output.
One clause is enough: "using this project's 30-day staleness threshold."

## Voice and writing style

Daikenja ships a default voice. A user's `writing_style` prose **layers on top
of it, and does not replace it**: the default applies except where the user's
own prose says otherwise. This holds wherever that prose lives -- the layering
rule is about content, not about storage.

The default voice sorts its own rules into two tiers, and layering respects
them:

- **Fixed.** A user's prose cannot turn these off. They are frozen decisions
  about all generated output rather than matters of taste. A hard deadline's
  absolute date is one of them.
- **Defaults.** A user's prose may narrow or replace these.

A line in a user's prose that contradicts a Fixed rule is not an override and
has no effect.

Which rule sits in which tier is the voice file's call, not this document's, and
the file itself is **not part of this contract**. It belongs to `compose`, its
main consumer. This document fixes only the layering rule and the fact that the
two tiers exist, so that `compose` does not have to invent either.

## Who writes what

| File | Written by | Notes |
|---|---|---|
| `daikenja.yaml` -- the `profile:` block | `setup-user` | Only on user approval. Never touches `projects:`. |
| `daikenja.yaml` -- a project's entry under `projects:` | `setup-project` | Only on user approval, and only the entry matching the directory it runs in. Registration is idempotent: an exact normalized-path match leaves the existing entry and its key alone. Never writes `last_checkpoint`. |
| `daikenja.yaml` -- `last_checkpoint` | `project-catchup` | Proposes advancing it after reporting; writes on approval. |
| `personas.md` -- creating the file | `setup-user`, and `remember-persona` on absence | Both copy the blank template if and only if no file exists, and neither inspects or overwrites content. `setup-user` does this proactively on every run; `remember-persona` does it only when it has an entry to write and finds the file missing, folding the scaffold into that write's report. Copying the template twice is idempotent, so the two never conflict. |
| `personas.md` -- content | the user by hand, and `remember-persona` | Appends an entry for a person the user described. Any other skill that needs a persona recorded runs it. The append is silent only where the user described the person with nothing pasted; a description that arrived with pasted material is offered once and written on a yes. Amending prose the user wrote by hand is proposed, never silent. |
| `writing-style.md` -- creating the file | `setup-user` on absence | Copies the blank template if and only if no file exists, and never inspects content. Same rule as `personas.md`. |
| `writing-style.md` -- content | the user by hand, and `learn-voice` on approval | `learn-voice` derives a proposal from writing samples the user supplies, shows the exact content it would write -- as a diff whenever the file already holds anything -- and writes only what the user approves. Nothing else edits it. |
| `<project>/.daikenja/ledger.md` | `project-log`, and only `project-log` | `meeting-review` writes through `project-log`. Every other skill reads. |

**The table names the local defaults, and who may write does not change with
where the prose lives.** When `personas` or `writing_style` points at a Drive
file, the same skill writes the same content to that file instead of to a local
one, through the replacement sequence in
[Writing replaces the file](#writing-replaces-the-file). Two rules follow from
the fact that Daikenja can only see Drive files it created itself:

- **`setup-user` is the only skill that creates a Drive file or the `daikenja`
  folder**, and only when the user chooses Drive during setup and the connector
  is present. It creates the folder if it is not already there, writes the blank
  template into a new file inside it, and puts that file's name in the pointer.
  This is not a convention about tidiness. A file Daikenja did not create cannot
  be seen at all, so creating it is the only way one can exist to point at.
- **`remember-persona` does not create Drive files, and never redirects a
  write.** Its scaffold-on-absence rule covers local files only. If `personas`
  is a Drive pointer that does not resolve, it writes nothing, says so, and
  keeps the entry in the conversation. Falling back to the local default would
  split the user's notes across two stores without telling them, which is worse
  than not writing.

**The single-writer rule governs the ledger, not `daikenja.yaml`.** This
distinction matters: `project-catchup`'s job is to report a delta and move the
checkpoint, so it must be able to write that one key. It still never touches
ledger content.

**`personas.md` has two writers doing two different acts, not one job split in
two.** `setup-user` owns *creation* as a standing rule -- existence is its only
test, and a file that is already there is left alone whatever is in it.
`remember-persona` owns every *content* write, and appending an entry is the
only way content reaches the file from Daikenja; because a content write needs
the file to exist, it also scaffolds the same template on absence rather than
stopping to wait for `setup-user`. Creation is now something both skills can
do, but the split that matters is unchanged: `setup-user` never writes
content, and `remember-persona` never inspects or overwrites content on an
existing file. That is the boundary the ledger's stricter single-writer rule
does not transfer here unchanged.

A learned entry is written without asking and reported afterwards, which is
deliberate: an append is additive and reversible, and the report names the file
and shows the exact entry so it can be edited or deleted. That licence covers
new people only. Prose the user wrote by hand is never rewritten silently.

**The licence also stops at the file's own subject: real colleagues.** Where the
description came in with material the user pasted -- a draft, a thread, an
example -- the person may be invented, and nothing in a pasted block has to say
so. `remember-persona` therefore offers those entries and writes them on a yes,
per its Step 1 § Where the description came from. That test lives there and
nowhere else: a skill that routes a description to it reports the outcome and
never re-decides it. **The question never gates the caller** -- a review or a
draft finishes and carries the offer back as one line, the same one line a
silent write would have cost it.

**`writing-style.md` splits the same way, and its content writer asks every
time.** `setup-user` owns creation on the same existence-only test, and
`learn-voice` owns every content write. The two prose files differ only in what
buys the write: an appended persona is additive, so it is silent and reported
afterwards, while a derived writing style replaces the whole file and is
therefore proposed in full, diffed against whatever is already there, and
written only on approval. Neither skill may write the other's file, and
`setup-user`'s never-inspect rule is unchanged -- `learn-voice` reads the file
under its own contract, to show the user what would change.

`setup-user` writes a fresh configuration by asking the user. It does not
migrate, import, or convert anything from a previous Daikenja or from any
pre-plugin layout.

**`setup-project` may propose ledger content but never writes it.** Its optional
seeding step derives candidate decisions and open items from sources the user
names, and hands them to `project-log`, which shows the exact lines and waits.
That keeps the single-writer rule for the ledger intact while letting a project
start with the history it already has.

## Failure behavior

One rule covers the common cases:

> **One notice line, then continue with reduced behavior. Hard-stop only when
> the missing thing is the task itself.**

| Situation | Behavior |
|---|---|
| `daikenja.yaml` absent | Ledger-only skills still work using the defaults (`.daikenja/ledger.md`, 21 days). Skills that need the profile say "Daikenja is not configured -- run `/daikenja:setup-user`" and stop. |
| Malformed YAML | **Stop.** Report the first line that does not parse. Never guess the intent, and never rewrite the file -- repair would clobber hand-written content. |
| Valid YAML, missing optional key | Treat as absent, degrade for that key alone with one notice, and continue. One missing optional key never fails a run. |
| Valid YAML, missing `profile.name` | Treat the configuration as incomplete. Say so and point at `setup-user`. `setup-project` stops here rather than continuing, because it has no profile to register a project against. |
| `projects:` absent or empty | The project is unregistered. See the resolution order above. `setup-project` is what registers one. |
| `writing_style` or `personas` is not configured at all | Absent key. One notice, then continue with reduced behavior -- the default voice, or no personas. |
| A pointed-at local prose file is missing | One notice naming the path, then continue without it. The exception is `remember-persona`: when it has an entry to write and `personas.md` is missing, it scaffolds the file from the template (per Who writes what) rather than treating the file as unreadable. |
| A configured `drive:` pointer does not resolve, or its download comes back empty | **Stop.** Name the file and the reason: the connector is not in the session, the `daikenja` folder is missing or duplicated, no file in it carries that name, more than one does, or the download returned nothing. Never treat it as an unconfigured key, and never fall back to a local file. `remember-persona` additionally holds the entry in the conversation (per Who writes what). |
| `norms_doc` absent | Not an error. `self-review` skips ROLE CHECK silently -- this is the documented default. |

Notices are one line and they name the file. "No `writing-style.md` at
`~/.claude/daikenja/writing-style.md`, composing with the default voice" tells
the user what to fix. "Config incomplete" does not.

**Not configured and configured-but-broken are different situations.** A key the
user never set means they did not ask for that behavior, so continuing without
it is right. A `drive:` pointer means they did ask, and the request failed. The
two rows above keep them apart on purpose. Local paths keep the older, softer
handling because a missing local file is a fact you can establish: the path is
there or it is not, and an empty file is a file the user emptied. Drive gives no
such certainty, which is why only that form stops.

## Worked example

A filled `daikenja.yaml` with two projects, one of which overrides the global
staleness threshold and points its ledger somewhere other than the default:

```yaml
profile:
  name: Carlos
  role: Solutions Architect
  org: Northwind
  team: Platform
  domain: payments and reconciliation
  tone: direct
  writing_style: ./writing-style.md
  personas: ./personas.md
  stale_after_days: 21

projects:
  atlas-migration:
    path: C:/GitHub/atlas
    last_checkpoint: 2026-08-14T09:12Z

  billing-api:
    path: C:/GitHub/billing-api
    ledger: .daikenja/ledger.md
    last_checkpoint: 2026-08-13T17:40Z
    stale_after_days: 30
    norms_doc: https://example.com/platform/ways-of-working
```

Resolving from `C:\GitHub\atlas\services\ingest`:

1. Normalized: `c:/github/atlas/services/ingest`.
2. `c:/github/atlas` is a prefix; `c:/github/billing-api` is not.
3. Longest match is `atlas-migration`.
4. It has no `ledger:` key, so the ledger is `C:/GitHub/atlas/.daikenja/ledger.md`.
5. It has no `stale_after_days`, so `project-gaps` uses the profile's 21 days
   and says so.
6. It has no `norms_doc` and neither does the profile, so `self-review` skips
   ROLE CHECK.

### Minimal valid file

The least a file can contain and still be usable. Every other key is optional:

```yaml
profile:
  name: Carlos
```

With that file alone, `compose` works with the default voice, `project-log`
scaffolds and writes `.daikenja/ledger.md` in whatever project it runs in and
names `setup-project` as the way to register it, `project-gaps` uses the 21-day
default, and `self-review` runs without ROLE CHECK.
