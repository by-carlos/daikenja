# Config resolution

Daikenja reads user configuration from **one YAML file** outside the plugin
directory. This document is the resolution core: where that file lives, how a
skill finds the current project and its ledger, how the `writing_style` and
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
falls through to the directory.

#### By key, when the user named one

1. Compare the given key against every `projects:` key, case-insensitively.
2. **Exactly one match: use it.** Directory resolution does not run at all --
   the current directory is irrelevant to the rest of the run.
3. **No match: say so and stop.** Name the key that was given, list the
   registered keys, and write nothing. **Never fall back to the current
   directory.** Silently answering about a different project than the one
   named is the failure this route exists to remove, and it is worse than no
   answer, because the reply looks correct.

The skills that accept a key argument are the five read skills, per
[`reading.md`](reading.md) section Step A0, and `project-list`, whose whole job
is to report them. `project-log` and `setup-project` resolve by directory only;
they write inside a project root, and a name alone does not say which root.

#### By directory, otherwise

1. Normalize the current directory: forward slashes, no trailing slash,
   case-insensitive comparison. (Windows paths compare case-insensitively and
   arrive in both slash styles; normalizing first avoids both traps.)
2. Compare against **every path of every `projects:` entry**, normalized the
   same way. An entry's paths are its `paths` list, or its `path` scalar read
   as a one-element list. An entry with no paths is skipped -- it is reachable
   only by key, and that is a legal state, not a match failure.
3. Take the **longest matching prefix**, across all paths of all entries. The
   entry owning that path is the match. Nested projects therefore resolve to
   the innermost one, whichever entry it belongs to, and two paths of the same
   project cannot compete with each other -- they resolve to the same project
   either way.
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

**The project root is the first path in the entry**, not the path that matched.
A project has one ledger, so its root cannot depend on which of its directories
the user happened to be standing in -- resolving relative to the matched path
would give a three-repository project three ledgers and no way to tell which
one holds the decision. The first path is therefore the root from every
direction: from any of the project's own directories, and from the key route,
which has no matched path at all. Order the list deliberately; the first entry
is where a relative `ledger:` lands.

**A project with no paths has no root, so nothing relative resolves against
it.** An **absolute** `ledger:` key resolves normally and is exactly how such a
project keeps a ledger -- see [Resolving `ledger`](#resolving-ledger). Without
one there is no location at all: a skill that needs a ledger says so in one
line and stops, per [Failure behavior](#failure-behavior).

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
| Relative path | `.daikenja/ledger.md` | That path, relative to the **project root** -- the first path in the entry, per [Finding the ledger](#finding-the-ledger). This is the default. An entry with no paths has no root, so a relative pointer cannot resolve on one; use the absolute form. |
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
has nowhere for a relative `ledger:` to be relative *to*. Give it no paths and
an absolute pointer into Daikenja's own configuration directory:

```yaml
projects:
  vendor-onboarding-programme:
    paths: []
    ledger: C:/Users/you/.claude/daikenja/ledgers/vendor-onboarding-programme.md
```

**The two keys do different halves of the same job, and both are needed.**
`paths: []` is what stops the project needing a directory to be resolved from
-- it is reached by name instead, from anywhere. The absolute `ledger:` is what
gives the record a location once there is no root to be relative to. Either one
alone leaves a gap: a pathless project without an absolute `ledger:` has
nowhere to keep its record, and an absolute `ledger:` on an entry that still
carries a scratch-folder `path` means the user has to stand in that folder to
be answered.

The convention is `~/.claude/daikenja/ledgers/<project-key>.md`, alongside every
other file Daikenja manages for the user rather than for a repository. Nothing
about the ledger's own format changes -- it is read and written exactly as
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
The reason is in
[`config-drive.md`](config-drive.md) § Writing replaces the file: every write
creates a new file with a new ID, so a stored ID is wrong the first time the
user's prose changes. The name is the only handle that survives a write.

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
| `daikenja_version` absent, empty, or different from the installed version | One notice line naming both versions and `/daikenja:setup-user`, then continue -- and only when [`upgrading.md`](upgrading.md) names a version later than the recorded one. Never a stop, and never a migration performed by the skill that noticed. See [Version marker and upgrades](config-versioning.md#version-marker-and-upgrades). |
| The installed version cannot be read (`plugin.json` missing or unparsing) | No notice, continue silently. The marker is a diagnostic, and a diagnostic that cannot run is not a failure of the task. |
| `projects:` absent or empty | The project is unregistered. See the resolution order above. `setup-project` is what registers one. |
| A named project key matches no entry | **Stop.** Name the key, list the registered keys, and write nothing. Never fall back to the current directory -- an answer about the wrong project reads exactly like a correct one. |
| A project entry has neither `path` nor `paths`, or an empty `paths` | Not an error. The project is reachable only by key and is skipped by directory resolution. With no root, only an absolute `ledger:` can resolve; without one a skill that needs a ledger stops with one line naming the key. |
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
