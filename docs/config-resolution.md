# Config resolution

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Resolution order -- preflight "Step 0: read the shared docs"
- § Finding the project -- project-list "Step 0: read the contracts", setup-project "Step 1: read what already exists"
- § Finding `DECISIONS.md` and `open.md` -- project-list "Step 0: read the contracts"
- § Legacy keys and unmigrated ledgers -- project-list "Step 0: read the contracts", setup-project "Step 2: register the project"
- § Resolving `writing_style` and `personas` -- preflight "Step 0: read the shared docs", setup-user "Offering Google Drive, without ever requiring it"
- § Failure behavior -- preflight "Step 0: read the shared docs", self-review "Step 0: read the shared docs"
- § Voice and writing style -- judgement "Voice in the message form"

Daikenja reads user configuration from **one YAML file** outside the plugin
directory. This document is the resolution core: where that file lives, how a
skill finds the current project and its ledger files, how the `writing_style` and
`personas` pointers resolve, precedence between project and profile settings,
and what a skill does when something is missing or broken.

Nothing parses this file programmatically. Claude reads it as text and edits it
with the Edit tool. YAML is the format because it takes comments and reads well
at a glance, not because anything deserializes it.

Four companion documents hold what this one does not: the full key-by-key
schema is [`config-schema.md`](config-schema.md), which skill writes which key
is [`config-writers.md`](config-writers.md), reading and writing a Google Drive
pointer is [`config-drive.md`](config-drive.md), and the `daikenja_version`
marker and the upgrade path are [`config-versioning.md`](config-versioning.md).
Most skills need only this file.

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
[Who writes what](config-writers.md#who-writes-what).

## Resolution order

### Finding the configuration

1. `~/.claude/daikenja/daikenja.yaml`. There is no search path and no
   project-local config file. One location, always.

### Finding the project

**Two routes, and the named one wins.** A skill resolves which `projects:`
entry applies either from a project key the user named, or from the directory
it is running in. The key route is checked first and is decisive: it never
falls through to the directory. A third route, by content, exists for a
caller that has neither and is described between them; it never outranks
these two.

#### By key, when the user named one

1. Compare the given key against every `projects:` key, case-insensitively.
2. **Exactly one match: use it.** Directory resolution does not run at all --
   the current directory is irrelevant to the rest of the run.
3. **No match: say so and stop.** Name the key that was given, list the
   registered keys, and write nothing. **Never fall back to the current
   directory.** Silently answering about a different project than the one
   named is the failure this route exists to remove, and it is worse than no
   answer, because the reply looks correct.

The skills that accept a key argument freely are the five read skills, per
[`reading.md`](reading.md) section Step A0, and `project-list`, whose whole job
is to report them. `project-log` accepts one too, from any directory: the
entry alone fixes every file it can write, per
[Finding `DECISIONS.md` and `open.md`](#finding-decisionsmd-and-openmd). Which
of several repositories' `DECISIONS.md` a decision lands in is not a location
question; `project-log` asks it per decision, however the project was
resolved. `setup-project` still resolves by directory
only; it registers a *new* entry's own root, and a name alone cannot say what
that root should be.

#### By content, when neither applies

A caller that starts from a thread, a report or a pasted conversation -- with
no key and no useful directory -- resolves the project by matching the content
against every registered project's card. That route is defined in
[`project-card.md`](project-card.md) § Resolving a project by content, and it
never overrides the two above: a named key is decisive, a directory that
resolves is the project the user is standing in, and content decides only when
neither does. It is a read across cards, not a lookup in this file, which is
why it lives with the card's own contract.

#### By directory, otherwise

1. Normalize the current directory: forward slashes, no trailing slash,
   case-insensitive comparison. (Windows paths compare case-insensitively and
   arrive in both slash styles; normalizing first avoids both traps.)
2. Compare against **every path of every `projects:` entry**, normalized the
   same way. An entry's paths are its `paths` list, or its `path` scalar read
   as a one-element list. An entry with no paths is skipped and reported as
   needing migration, per
   [Legacy keys and unmigrated ledgers](#legacy-keys-and-unmigrated-ledgers).
3. Take the **longest matching prefix**, across all paths of all entries. The
   entry owning that path is the match. Nested projects therefore resolve to
   the innermost one, whichever entry it belongs to, and two paths of the same
   project cannot compete with each other -- they resolve to the same project
   either way.
4. No match means the project is unregistered. Every skill says so in one line
   and then continues -- an unregistered project still has ledger files to
   read if they exist on disk, and files on disk win over the config (see
   [Finding `DECISIONS.md` and `open.md`](#finding-decisionsmd-and-openmd)).
   `project-log` additionally names
   `setup-project` as the way to register it. The branch a read skill follows is
   in
   [`reading.md`](reading.md) § Step A.

### Finding `DECISIONS.md` and `open.md`

A project's ledger is two files at fixed paths. No config key moves either one.

1. **`DECISIONS.md` at the root of every path in the entry**, in `paths` order:
   `<path>/DECISIONS.md` for each. A decision belongs with the code it
   constrains, so a project spanning three repositories has three of them.
   Where a root file's area carries a `Moved: <folder>/DECISIONS.md` line, that
   file is read too, per [`decisions-format.md`](decisions-format.md) §
   Splitting.
2. **`.daikenja/open.md` in the home repository only.** The home repository is
   the **first** path in the entry, so a project keeps one `open.md` whichever
   of its directories the run started in. Its grammar is
   [`open-format.md`](open-format.md).
3. **No project matched:** the current directory stands in as the one root, so
   the files are `DECISIONS.md` and `.daikenja/open.md` under it.
4. **Read both files' version lines first**, per
   [`open-format.md`](open-format.md) § Version line: a newer version is still
   read, with one warning per run.
5. **A file that does not exist** is scaffolded by `project-log`, from
   [`../templates/DECISIONS.md`](../templates/DECISIONS.md) or
   [`../templates/open.md`](../templates/open.md), after the user approves. Read
   skills do not scaffold. A registered repository with no `DECISIONS.md` has no
   decisions recorded yet, which is not a notice. When the project has neither
   any `DECISIONS.md` nor its `open.md`, a read skill says in one line that no
   ledger exists yet and names `project-log` as the skill that creates one --
   unless the legacy check below finds an old ledger first.

**Home is the first path, not the path that matched.** The order of `paths` is
therefore part of the contract: `setup-project` asks which repository is home
and writes it first. Do not reorder the list afterwards -- moving another path
to the front moves where `open.md` is looked for.

**Files found on disk win over the config.** This is a rule about an
**unmatched project**. If `DECISIONS.md` or `.daikenja/open.md` exists under the
current directory but no `projects:` entry matches it, those files are used and
`project-log` names `setup-project` as the way to add the missing entry. The
files on disk are the fact; the config is the index.

### Reading several repositories

A read skill reads **every** `DECISIONS.md` of the matched project, not only the
one in the directory it started in: a decision recorded in `platform-infra`
binds a question asked from `platform-web`. When it reports an entry, it names
the repository the entry came from (the last segment of that path is enough),
so the reader knows which file to open. Entries are never merged across files:
two repositories recording the same decision is two entries, reported as found.

A path in `paths` that does not exist on disk is skipped silently, as directory
resolution already does; `project-list` is the skill that reports it. A
repository that is not reachable is never the reason a run stops.

### Legacy keys and unmigrated ledgers

Configuration and files written before this layout are recognised, never acted
on: the migration in `setup-project`, reached from `setup-user`, is the one
place they change.

- **A leftover `ledger:` key** is ignored. The run says so in one line naming
  the key and `/daikenja:setup-user`, then continues with the fixed paths above.
- **A `paths: []` entry**, or one with neither `path` nor `paths`, is
  reported as "needs migration" in one line naming the key and
  `/daikenja:setup-user`, and skipped. Directory resolution never matches it; a
  run that names its key says the same line and stops for that project.
- **An unmigrated ledger at the legacy location.** When the home repository
  (or, with no match, the current directory) has `.daikenja/ledger.md` and no
  `.daikenja/open.md` beside it, the project's ledger has not been migrated,
  whether or not a `DECISIONS.md` exists. A read skill says in one line that the
  project needs migration and names `/daikenja:setup-user`; it does not parse
  the old file. `project-log` refuses to scaffold or write either file over it,
  with the same line.

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
The reason is in
[`config-drive.md`](config-drive.md) § Writing replaces the file: every write
creates a new file with a new ID, so a stored ID is wrong the first time the
user's prose changes. The name is the only handle that survives a write.

**Local paths are the default and stay the default.** The shipped template
points both keys at local files, and a user who never mentions Drive sees
exactly the behavior described everywhere else in this document. Drive buys one
thing: reaching these settings from a machine other than the one that wrote
them. The connector's grant spans machines, so a file created in one Claude
Code session is readable from another (verified 17 August 2026).

**The two keys resolve independently.** Pointing `writing_style` at a Drive file
while `personas` stays on a local file is a normal configuration, not a
half-migrated one. Persona notes are about real colleagues, and keeping them
local while sharing a writing style is a reasonable thing to want.

**Drive is the only remote store.** There is no second backend and no plugin
setting that selects one. A pointer is a path or it is `drive:`.

**How a Drive pointer is actually found and written** -- the `daikenja` folder,
the paging rule that catches a duplicate, and the download-then-replace sequence
a write follows -- is [`config-drive.md`](config-drive.md), which this section
defers to rather than restating.

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

**Stance prose triggers flags, never edits.** Whatever a user's prose says
about stance -- in any section, under any heading -- does not change the
stance of a message. The stance-kept rule in
[`rewrite-rules.md`](rewrite-rules.md) § Stance prose in the writing style
flags, never edits outranks it. Such a line may at most cause a flag, and only
where the stance check below is switched on.

**The stance check: one switch, two role lines.** The prose may carry an
opt-in for `compose`'s role-aligned stance check (its Step 6c). It is two
things, both plain text in the same file:

- **The switch** is a line reading exactly `stance-check: on`, on its own and
  outside a code block, anywhere in the file. Absent means off. Nothing else
  turns the check on: a section that merely talks about stance, such as a
  "senior register" note, is not the switch.
- **The role facts** are a `## Role and stance` section of two free-text
  lines, in the user's own words:

  ```markdown
  stance-check: on

  ## Role and stance

  - What I own or decide: the release schedule, the team's on-call rota.
  - What is usually the reader's to decide: budget, hiring, other teams' roadmaps.
  ```

  The switch with no section, or a section with neither line filled in, runs
  the check against nothing: `compose` says so in one `Comment` line instead
  of guessing a role.

No key in `daikenja.yaml` selects the check; the file is the only place it
lives, so it travels with the prose wherever the `writing_style` pointer
resolves. `setup-user` offers it, `learn-voice` carries it across a rewrite
verbatim, and [`config-writers.md`](config-writers.md) § Who writes what names
both writes.

**Voice-only mode.** Layering is the default, and it is the right default for
anything that goes out under the user's name. A skill may instead declare one
of its outputs **voice-only**: `voice.md` applies in full, both tiers as
shipped, and the user's `writing_style` pointer is **not read** -- not
resolved, not layered, and its absence or failure is not a notice, because
nothing asked for it. `personas` is not read either. The mode is for output
written as an AI pass rather than as the user -- a review summary headed as
one, handed to a reader who was not in the conversation -- where the user's
own greetings and turns of phrase would misattribute it. It is not a user
setting and no key in `daikenja.yaml` selects it: a skill names in its own
`SKILL.md` which of its outputs are voice-only, and every other output stays
layered. `judgement`'s `message` form is the one shipped use.

## Failure behavior

One rule covers the common cases:

> **One notice line, then continue with reduced behavior. Hard-stop only when
> the missing thing is the task itself.**

| Situation | Behavior |
|---|---|
| `daikenja.yaml` absent | Ledger-only skills still work using the defaults (`DECISIONS.md` and `.daikenja/open.md` under the current directory, 21 days). Skills that need the profile say "Daikenja is not configured -- run `/daikenja:setup-user`" and stop. |
| Malformed YAML | **Stop.** Report the first line that does not parse. Never guess the intent, and never rewrite the file -- repair would clobber hand-written content. |
| Valid YAML, missing optional key | Treat as absent, degrade for that key alone with one notice, and continue. One missing optional key never fails a run. |
| Valid YAML, missing `profile.name` | Treat the configuration as incomplete. Say so and point at `setup-user`. `setup-project` stops here rather than continuing, because it has no profile to register a project against. |
| `daikenja_version` absent, empty, or different from the installed version | One notice line naming both versions and `/daikenja:setup-user`, then continue -- and only when [`upgrading.md`](upgrading.md) names a version later than the recorded one. Never a stop, and never a migration performed by the skill that noticed. See [Version marker and upgrades](config-versioning.md#version-marker-and-upgrades). |
| The installed version cannot be read (`plugin.json` missing or unparsing) | No notice, continue silently. The marker is a diagnostic, and a diagnostic that cannot run is not a failure of the task. |
| `projects:` absent or empty | The project is unregistered. See the resolution order above. `setup-project` is what registers one. |
| A named project key matches no entry | **Stop.** Name the key, list the registered keys, and write nothing. Never fall back to the current directory -- an answer about the wrong project reads exactly like a correct one. |
| A project entry has neither `path` nor `paths`, or an empty `paths` | A project kept before every project lived in a repository. One line, "needs migration", naming the key and `/daikenja:setup-user`; skipped by directory resolution, and a run that named its key stops for it. See [Legacy keys and unmigrated ledgers](#legacy-keys-and-unmigrated-ledgers). |
| A project entry still has a `ledger:` key | Ignored. One line naming the key and `/daikenja:setup-user`, then continue with the fixed paths. |
| `.daikenja/ledger.md` at the home repository with no `.daikenja/open.md` beside it | Needs migration. One line naming `/daikenja:setup-user`; read skills do not parse the old file, and `project-log` writes nothing. |
| `DECISIONS.md` or `open.md` carries a newer format version than the plugin knows | Read skills read it and warn once per run; `project-log` refuses the whole batch and asks for a plugin update. See [`open-format.md`](open-format.md) § Version line. |
| A project entry has both `path` and `paths` | Read the entry as the union of the two, and say so in one line naming the key. Do not guess which was meant, and do not rewrite the file to remove one -- `setup-project` is where the user fixes it. |
| A path in `paths` does not exist on disk | Not an error for resolution: a path that matches nothing simply never matches. `project-list` reports it; every other skill stays silent, because a detached network drive is not a configuration mistake. |
| `writing_style` or `personas` is not configured at all | Absent key. One notice, then continue with reduced behavior -- the default voice, or no personas. For a writer skill with an entry to write (`remember-persona`), reduced behavior means the default path itself: if `personas.md` does not exist there yet, it scaffolds the file from the template (per [Who writes what](config-writers.md#who-writes-what)) before writing the entry, rather than treating the absent key as a reason to stop. |
| A local pointer names a path, and that specific file is missing | Not the absent-key case above -- the user pointed here specifically. For a read skill, one notice naming the path, then continue without it. A skill may substitute an equivalent disclosure already required elsewhere in its own report for the standalone notice, when that disclosure covers the same fact (`compose` § personas and `preflight` § the named personas do this); plain silence with nothing said anywhere does not qualify. A writer skill (`learn-voice`, `remember-persona`) does not get this softer treatment -- see the row below. |
| A writer skill's own configured local pointer does not resolve | **Stop.** One notice naming the path, then write nothing -- not to that path, and not to any other. `learn-voice` still shows the derived proposal so the user keeps it; `remember-persona` keeps the entry in the conversation. Never redirect the write to the default path instead: that creates or changes a file the user did not point at, and splits their prose across two files without telling them. Mirrors the Drive row below, and each skill's own "file is not writable" row. |
| A configured `drive:` pointer does not resolve, or its download comes back empty | **Stop.** Name the file and the reason: the connector is not in the session, the `daikenja` folder is missing or duplicated, no file in it carries that name, more than one does, or the download returned nothing. Never treat it as an unconfigured key, and never fall back to a local file. `remember-persona` additionally holds the entry in the conversation (per [Who writes what](config-writers.md#who-writes-what)). |
| `norms_doc` absent | Not an error. `self-review` skips ROLE CHECK silently -- this is the documented default. |

Notices are one line and they name the file. "No `writing-style.md` at
`~/.claude/daikenja/writing-style.md`, composing with the default voice" tells
the user what to fix. "Config incomplete" does not.

**Not configured and configured-but-broken are different situations.** A key the
user never set means they did not ask for that behavior, so continuing without
it is right. A `drive:` pointer -- or a writer skill's own local pointer --
means they did ask, and the request failed; both stop rather than substitute
something the user did not choose. The rows above keep these apart on purpose.

**Read skills keep the older, softer handling for a broken local pointer**,
because a missing local file is a fact you can establish: the path is there or
it is not, and an empty file is a file the user emptied. Continuing without it
costs nothing that was not already optional. Drive gives no such certainty for
anyone, which is why that form always stops. A writer skill cannot take the
same softness for a local pointer either, because "continue" would mean picking
a different file to write to on the user's behalf -- which is exactly the
undocumented retry this row exists to rule out.
