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

`setup-user` is the only skill that creates or edits configuration keys. The one
exception is `last_checkpoint`; see [Who writes what](#who-writes-what).

## Schema

```yaml
profile:
  name: <string>              # required
  role: <string>              # optional
  org: <string>               # optional
  team: <string>              # optional
  domain: <string>            # optional, the subject matter you work in
  tone: standard              # direct | standard | guided. Default: standard
  writing_style: ./writing-style.md   # optional, path relative to this file
  personas: ./personas.md             # optional, path relative to this file
  norms_doc: <path or url>            # optional, absent by default
  stale_after_days: 21                # optional. Default: 21

projects:
  <project-key>:
    path: <absolute path>             # required
    ledger: .daikenja/ledger.md        # optional, relative to path
    last_checkpoint: 2026-08-14T09:12Z  # optional, written by catchup
    stale_after_days: <int>           # optional, overrides the profile value
    norms_doc: <path or url>          # optional, overrides the profile value
```

### Field notes

**`profile` holds short scalars only.** Identity is a handful of words per
field, so it lives directly in the YAML. Anything long enough to be prose lives
in a `.md` file that the config points at. There is deliberately no second
mechanism -- no `profile.md`, no free-text identity blob. Two ways to say who
you are is one too many.

**`tone`** sets how much the skills explain themselves. `direct` is terse,
`guided` walks through its reasoning, `standard` is the middle and the default.

**`writing_style` and `personas`** are paths, resolved relative to
`daikenja.yaml`'s own directory. An absolute path is also accepted. A path that
does not resolve is treated as an absent key, with a notice.

**`norms_doc`** is the team norms or ways-of-working document that
`self-review`'s ROLE CHECK section needs. It is absent by default, and that
section ships off. Configuring it is what turns the section on.

**`stale_after_days`** is how long an open item may sit before `gaps` calls it
stale. It measures age from the entry's date field, which is when the item was
raised -- not when it was last touched. Daikenja does not track last-touched,
and "this has been open five weeks" is the signal worth having. Default 21 days.

**`last_checkpoint`** is `YYYY-MM-DDThh:mmZ`, UTC, minute precision -- the same
timestamp format the ledger's Changelog uses. It marks how far `catchup` has
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
4. No match means the project is unregistered. Read skills say so in one line
   and stop. `log` offers to register it.

### Finding the ledger

1. The matched project's `ledger:` key, resolved relative to its `path`.
2. Otherwise `.daikenja/ledger.md` under the project root.
3. If the file does not exist, `log` scaffolds it from
   [`../templates/ledger.md`](../templates/ledger.md) after the user approves.
   Read skills do not scaffold; they report that no ledger exists and name the
   skill that creates one.

**A ledger found on disk wins over the config.** If `.daikenja/ledger.md` exists
but no `projects:` entry matches, the ledger is used and `log` offers to add the
missing entry on its next write. The file on disk is the fact; the config is the
index.

### Precedence

**Project overrides global, key by key.** A project supplying
`stale_after_days` uses its own; a project omitting it inherits the profile's.
There is no deep merge beyond this -- keys are scalars.

**A skill states which it used** whenever the answer would change the output.
One clause is enough: "using this project's 30-day staleness threshold."

## Voice and writing style

Daikenja ships a default voice. A user's `writing_style` file **layers on top of
it, and does not replace it**: the default applies except where the user's file
says otherwise.

One rule is not overridable, because it is a frozen decision about all
generated output rather than a matter of taste:

- Absolute dates, never relative ones.

The default voice file itself is **not part of this contract**. It belongs to
`compose`, its main consumer. This document fixes only the layering rule, so
that `compose` does not have to invent one.

## Who writes what

| File | Written by | Notes |
|---|---|---|
| `daikenja.yaml` -- everything except `last_checkpoint` | `setup-user` | Only on user approval. |
| `daikenja.yaml` -- `last_checkpoint` | `catchup` | Proposes advancing it after reporting; writes on approval. |
| `personas.md`, `writing-style.md` | the user, by hand | Daikenja reads them and never edits them. |
| `<project>/.daikenja/ledger.md` | `log`, and only `log` | `meeting-review` writes through `log`. Every other skill reads. |

**The single-writer rule governs the ledger, not `daikenja.yaml`.** This
distinction matters: `catchup`'s job is to report a delta and move the
checkpoint, so it must be able to write that one key. It still never touches
ledger content.

`setup-user` writes a fresh configuration by asking the user. It does not
migrate, import, or convert anything from a previous Daikenja or from any
pre-plugin layout.

## Failure behavior

One rule covers the common cases:

> **One notice line, then continue with reduced behavior. Hard-stop only when
> the missing thing is the task itself.**

| Situation | Behavior |
|---|---|
| `daikenja.yaml` absent | Ledger-only skills still work using the defaults (`.daikenja/ledger.md`, 21 days). Skills that need the profile say "Daikenja is not configured -- run `/daikenja:setup-user`" and stop. |
| Malformed YAML | **Stop.** Report the first line that does not parse. Never guess the intent, and never rewrite the file -- repair would clobber hand-written content. |
| Valid YAML, missing optional key | Treat as absent, degrade for that key alone with one notice, and continue. One missing optional key never fails a run. |
| Valid YAML, missing `profile.name` | Treat the configuration as incomplete. Say so and point at `setup-user`. |
| `projects:` absent or empty | The project is unregistered. See the resolution order above. |
| A pointed-at prose file is missing | One notice naming the path, then continue without it. |
| `norms_doc` absent | Not an error. `self-review` skips ROLE CHECK silently -- this is the documented default. |

Notices are one line and they name the file. "No `writing-style.md` at
`~/.claude/daikenja/writing-style.md`, composing with the default voice" tells
the user what to fix. "Config incomplete" does not.

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
5. It has no `stale_after_days`, so `gaps` uses the profile's 21 days and says
   so.
6. It has no `norms_doc` and neither does the profile, so `self-review` skips
   ROLE CHECK.

### Minimal valid file

The least a file can contain and still be usable. Every other key is optional:

```yaml
profile:
  name: Carlos
```

With that file alone, `compose` works with the default voice, `log` scaffolds
and writes `.daikenja/ledger.md` in whatever project it runs in and offers to
register it, `gaps` uses the 21-day default, and `self-review` runs without
ROLE CHECK.
