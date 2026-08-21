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
`setup-user` owns `profile:` and `daikenja_version`, `setup-project` owns a
project's entry under `projects:`, and `project-catchup` owns `last_checkpoint`
alone. Nothing else writes this file. See
[Who writes what](#who-writes-what).

## Schema

```yaml
daikenja_version: 0.5.1       # optional, written by setup-user. See below.

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
    ledger: .daikenja/ledger.md        # optional, pointer -- relative (default) or absolute
    last_checkpoint: 2026-08-14T09:12Z  # optional, written by project-catchup
    stale_after_days: <int>           # optional, overrides the profile value
    norms_doc: <path or url>          # optional, overrides the profile value
```

### Field notes

**`daikenja_version`** records which version of Daikenja last wrote this file.
`setup-user` stamps it on every successful run and nothing else ever writes it.
It exists so that a release which changes something already on a user's disk can
be detected and handled; the full rule is
[Version marker and upgrades](#version-marker-and-upgrades).

It sits at the **top level**, not under `profile:`, because it describes the
file rather than the person -- a profile key would imply it is a setting the
user chose, and it is not. That makes it a third top-level key alongside
`profile:` and `projects:`, which is the smaller cost of the two.

**An absent or empty `daikenja_version` is a legal state**, not an error. It
means "written before this key existed", which is a handleable answer and is
exactly what every file written before this key shipped will say. The two cases
are not distinguished: a key with no value means the same thing as no key, and
both take the same path.

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

**`ledger`** is a **pointer**, not a fixed path. A pointer is a relative path or
an absolute path -- the same two forms `writing_style` and `personas` accept,
minus the `drive:` form. The full rule, including the recommended location for
a project with no repository of its own, is
[Resolving `ledger`](#resolving-ledger).

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

1. **The matched project has a `ledger:` key.** Resolve it per its pointer
   form -- see [Resolving `ledger`](#resolving-ledger) -- and use that path.
   The default filename below is not consulted; an explicit key is
   authoritative, not a hint to check alongside it.
2. **The matched project has no `ledger:` key**, or no project matched at all.
   Use `.daikenja/ledger.md` under the project root (or under the current
   directory, when nothing matched).
3. If the resolved file does not exist, `project-log` scaffolds it from
   [`../templates/ledger.md`](../templates/ledger.md) after the user approves.
   Read skills do not scaffold; they report that no ledger exists and name the
   skill that creates one.

**A ledger found on disk wins over the config.** This is a rule about an
**unmatched project**, not about overriding an explicit `ledger:` key. If
`.daikenja/ledger.md` exists under the current directory but no `projects:`
entry matches it, that file is used and `project-log` names `setup-project` as
the way to add the missing entry. The file on disk is the fact; the config is
the index. Once a project *is* matched and carries a `ledger:` key -- relative
or absolute -- that key's resolved path is the ledger, full stop; there is no
second, on-disk probe to fall back to if it happens to be missing.

### Resolving `ledger`

`ledger` is a pointer, reusing the grammar defined in
[Resolving `writing_style` and `personas`](#resolving-writing_style-and-personas)
minus its Drive form. Two forms are legal:

| Form | Example | Resolves to |
|---|---|---|
| Relative path | `.daikenja/ledger.md` | That path, relative to the project's `path`. This is the default and today's only behavior, unchanged. |
| Absolute path | `C:/Users/you/daikenja-ledgers/harbor.md` | That path, verbatim -- it may be anywhere, including outside the project directory entirely. |

**`ledger` deliberately does not accept the `drive:` form.** Two reasons, both
from this document's own Drive rules above. First, write frequency: a ledger
is written on every `project-log` run, while `personas.md` is appended rarely
-- the replacement sequence's brief two-file window between create and trash
is a rare risk for personas and a routine one for a ledger. Second, "a ledger
found on disk wins over the config" has no meaning for a file that is not on
disk, and that interaction needs its own design rather than an assumption. If
Drive support for the ledger is wanted later, it is its own change.

**A project with no repository of its own** -- work tracked across a wiki, a
chat space, a ticket system, with no folder that is naturally "the project" --
has nowhere for a relative `ledger:` to be relative *to* in spirit, even though
`path` still requires some directory. The recommended convention is an absolute
pointer into Daikenja's own configuration directory:

```yaml
projects:
  vendor-onboarding-programme:
    path: C:/Users/you/daikenja-projects/vendor-onboarding-programme
    ledger: C:/Users/you/.claude/daikenja/ledgers/vendor-onboarding-programme.md
```

`path` is still required and still what resolution matches the current
directory against, so a repository-less project needs some directory to be
"in" when a skill runs -- typically a scratch folder created for the purpose.
The `ledger:` key is what keeps the record itself out of that folder and inside
`~/.claude/daikenja/ledgers/<project-key>.md`, alongside every other file
Daikenja manages for the user rather than for a repository. Nothing about the
ledger's own format changes -- it is read and written exactly as
[`ledger-format.md`](ledger-format.md) specifies, regardless of where it lives.

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

## Version marker and upgrades

A release can change something that already exists on a user's disk -- the shape
of a key here, the grammar of a ledger entry, the name of a skill. Nothing on
the user's side records which version wrote what they have, so without a marker
there is no way to tell an affected install from an unaffected one. That is what
`daikenja_version` is for, and this section is the whole rule.

**Two versions are compared.** The **recorded** version is `daikenja_version` in
`daikenja.yaml`. The **installed** version is the `version` field of
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, which ships with the plugin
and is therefore always the version currently running.

**Compare them as semver, field by field, numerically** -- never as strings.
`0.10.0` is later than `0.9.0`, and string order says the opposite.

### The mismatch notice

**Every skill that reads `daikenja.yaml` emits one notice line when the recorded
version is out of date, then continues.** This is what makes the upgrade path
get reached at all: nobody re-runs setup after an upgrade unless something tells
them to.

That is binding on all of them, and most do not restate it -- a rule copied into
a dozen skills is a rule that drifts a dozen ways. The three places it is named
again say something the contract does not: [`reading.md`](reading.md) § Step A
places it in the read recipe's order, and `project-log` and `setup-project` also
*write* to this file, so each states that it still does not migrate.

A skill emits the notice when **both** of these hold:

1. The recorded version differs from the installed one, or is absent or empty.
2. [`upgrading.md`](upgrading.md) names at least one version **later than the
   recorded one**. An absent recorded version makes every section later than it.
   Sections under an `## [Unreleased]` heading do not count -- an unreleased
   note is not a version anyone can be on.

The second condition is what stops the line becoming noise. Most releases change
nothing on disk and add no section, and a notice that fires on every patch bump
teaches the user to ignore the one that matters. If `upgrading.md` cannot be
read at all, fall back to noticing on any difference -- erring toward telling the
user is the safe direction.

The wording is one line, and it names both versions and the skill:

```
daikenja.yaml was written by Daikenja 0.4.0; 0.6.0 is installed -- run /daikenja:setup-user.
daikenja.yaml predates version tracking; 0.6.0 is installed -- run /daikenja:setup-user.
```

**A skill never migrates anything and never edits configuration because it saw a
mismatch.** The notice is the whole of a reading skill's part in this. Migration
happens in `setup-user`, on the user's deliberate say-so, and nowhere else.

**Malformed YAML outranks all of the above.** A file that does not parse is a
hard stop naming the first unparsing line, per
[Failure behavior](#failure-behavior). Never attempt to read a version out of a
file you could not parse, and never migrate one.

### What `upgrading.md` is for

[`upgrading.md`](upgrading.md) holds one section per version that requires user
action: what changed on disk, what happens if the user does nothing, the exact
edit, whether `setup-user` can make it, and whether it is reversible. A release
that changes nothing on a user's disk adds nothing to it.

It does not duplicate `CHANGELOG.md`. The changelog records *what changed*; this
records *what you must do about it*. Two files holding the same fact drift; two
files holding different facts do not.

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
| `daikenja.yaml` -- `daikenja_version` | `setup-user` | Stamped on every successful run, in the same approved write as whatever else that run changed. No other skill writes it, and no skill writes it because it noticed a mismatch. See [Version marker and upgrades](#version-marker-and-upgrades). |
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
import or convert anything from another tool or from any pre-plugin layout.

**It does apply Daikenja's own documented upgrade steps**, and it is the only
skill that does. When the recorded `daikenja_version` is behind the installed
one, its upgrade branch reads [`upgrading.md`](upgrading.md), proposes the exact
edits for the versions in between, and writes them on approval -- the same
propose-then-approve shape as everything else it does. That is a different act
from importing a foreign layout, which it still refuses. See
[Version marker and upgrades](#version-marker-and-upgrades).

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
| `daikenja_version` absent, empty, or different from the installed version | One notice line naming both versions and `/daikenja:setup-user`, then continue -- and only when [`upgrading.md`](upgrading.md) names a version later than the recorded one. Never a stop, and never a migration performed by the skill that noticed. See [Version marker and upgrades](#version-marker-and-upgrades). |
| The installed version cannot be read (`plugin.json` missing or unparsing) | No notice, continue silently. The marker is a diagnostic, and a diagnostic that cannot run is not a failure of the task. |
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
daikenja_version: 0.5.1

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

It has no `daikenja_version`, so every skill that reads it adds the one-line
version notice until `setup-user` has run once and stamped it. That is the
intended behaviour for a file written by hand, not a defect in the example.
