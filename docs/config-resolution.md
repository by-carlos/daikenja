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
| `writing_style` or `personas` is not configured at all | Absent key. One notice, then continue with reduced behavior -- the default voice, or no personas. |
| A pointed-at local prose file is missing | One notice naming the path, then continue without it. The exception is `remember-persona`: when it has an entry to write and `personas.md` is missing, it scaffolds the file from the template (per [Who writes what](config-writers.md#who-writes-what)) rather than treating the file as unreadable. |
| A configured `drive:` pointer does not resolve, or its download comes back empty | **Stop.** Name the file and the reason: the connector is not in the session, the `daikenja` folder is missing or duplicated, no file in it carries that name, more than one does, or the download returned nothing. Never treat it as an unconfigured key, and never fall back to a local file. `remember-persona` additionally holds the entry in the conversation (per [Who writes what](config-writers.md#who-writes-what)). |
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
