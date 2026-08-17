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
file somewhere else or a Notion page. See
[Resolving `writing_style` and `personas`](#resolving-writing_style-and-personas).

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

**`tone`** sets how much the skills explain themselves. `direct` is terse,
`guided` walks through its reasoning, `standard` is the middle and the default.

**`writing_style` and `personas`** are **pointers**, not fixed paths. A pointer
may be a relative path, an absolute path, or a Notion page URL. A pointer that
does not resolve is treated as an absent key, with a notice. The three forms and
what each one means are in
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
4. No match means the project is unregistered. Read skills say so in one line
   and stop. `project-log` offers to register it.

### Finding the ledger

1. The matched project's `ledger:` key, resolved relative to its `path`.
2. Otherwise `.daikenja/ledger.md` under the project root.
3. If the file does not exist, `project-log` scaffolds it from
   [`../templates/ledger.md`](../templates/ledger.md) after the user approves.
   Read skills do not scaffold; they report that no ledger exists and name the
   skill that creates one.

**A ledger found on disk wins over the config.** If `.daikenja/ledger.md` exists
but no `projects:` entry matches, the ledger is used and `project-log` offers to
add the missing entry on its next write. The file on disk is the fact; the config
is the index.

### Resolving `writing_style` and `personas`

These two keys are pointers. A pointer says where the prose lives; it does not
say which skill may write it. Three forms are legal, and a pointer is exactly
one of them:

| Form | Example | Resolves to |
|---|---|---|
| Relative path | `./personas.md` | That path, relative to `daikenja.yaml`'s own directory. |
| Absolute path | `C:/Users/you/notes/personas.md` | That path. |
| Notion page URL | `https://www.notion.so/Personas-24f1c0e3...` | That Notion page, read through the Notion connector. |

A value starting `https://` on a `notion.so` or `notion.site` host is a Notion
pointer. Anything else is a path.

**Local paths are the default and stay the default.** The shipped template
points both keys at local files, and a user who never mentions Notion sees
exactly the behavior described everywhere else in this document. Notion buys one
thing: reaching these settings from a machine or a session other than the one
that wrote them.

**The two keys resolve independently.** Pointing `writing_style` at a Notion
page while `personas` stays on a local file is a normal configuration, not a
half-migrated one. Persona notes are about real colleagues, and keeping them
local while sharing a writing style is a reasonable thing to want.

#### Reading and writing a Notion pointer

A Notion pointer is reached through Notion's official remote MCP server at
`https://mcp.notion.com/mcp`, connected in the user's own session under their
own Notion account. Daikenja holds no Notion credential and stores nothing on
anyone else's infrastructure.

- **Reading** fetches the page body and reads it as the same prose the local
  file would have held. The page's own title and Notion properties are not part
  of the content.
- **The round-trip is faithful in content, not byte-identical.** Notion returns
  its own Markdown variant: headings, `**bold**` and paragraphs survive
  unchanged, but blank lines between blocks are stripped, and a set of
  characters is escaped. Nothing Daikenja reads depends on that whitespace, so
  the prose means the same thing either way -- but a skill matching against the
  page's text must match what the fetch actually returned, never what it
  believes it wrote earlier.
- **Writing** updates that page. Only `remember-persona` writes prose content,
  and the pointer's form does not change that; see
  [Who writes what](#who-writes-what).
- **The page is one ordinary page**, not a database, a view, or a tree of
  subpages. Daikenja reads the page it was pointed at and follows nothing out of
  it.

**No connector, no resolution.** If the Notion connector is not available in the
session, or the page cannot be reached -- offline, deleted, permission
withdrawn -- the pointer does not resolve. That is the same failure the contract
already defines for a path that does not resolve: an absent key, one notice
naming the pointer, then continue. There is no new failure mode and no offline
cache.

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
| `daikenja.yaml` -- `last_checkpoint` | `project-catchup` | Proposes advancing it after reporting; writes on approval. |
| `personas.md` -- creating the file | `setup-user`, and `remember-persona` on absence | Both copy the blank template if and only if no file exists, and neither inspects or overwrites content. `setup-user` does this proactively on every run; `remember-persona` does it only when it has an entry to write and finds the file missing, folding the scaffold into that write's report. Copying the template twice is idempotent, so the two never conflict. |
| `personas.md` -- content | the user by hand, and `remember-persona` | Appends an entry for a person the user described. Any other skill that needs a persona recorded runs it. Amending prose the user wrote by hand is proposed, never silent. |
| `writing-style.md` | the user, by hand | Daikenja reads it and never edits it. |
| `<project>/.daikenja/ledger.md` | `project-log`, and only `project-log` | `meeting-review` writes through `project-log`. Every other skill reads. |

**The table names the local defaults, and who may write does not change with
where the prose lives.** When `personas` or `writing_style` points at a Notion
page, the same skill writes the same content to that page instead of to a file.
Two rules follow from the fact that a Notion page cannot be created from
nothing the way a local file can:

- **`setup-user` is the only skill that creates a Notion page**, and only when
  the user chooses Notion during setup and the connector is present. It writes
  the blank template into the new page and puts that page's URL in the pointer.
- **`remember-persona` does not create Notion pages, and never redirects a
  write.** Its scaffold-on-absence rule covers local files only. If `personas`
  is a Notion pointer that does not resolve, it writes nothing, says so, and
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
| A pointed-at prose file is missing | One notice naming the path, then continue without it. The exception is `remember-persona`: when it has an entry to write and `personas.md` is missing, it scaffolds the file from the template (per Who writes what) rather than treating the file as unreadable. |
| A pointer names a Notion page and the connector is not in the session | Treat the key as absent. One notice naming the page and saying the Notion connector is not connected, then continue. Never fall back to a local file. |
| A pointer names a Notion page that cannot be reached | Same: absent key, one notice naming the page. Offline, deleted and permission-withdrawn are one case, because from here they look alike. Read skills continue reduced; `remember-persona` writes nothing and holds the entry (per Who writes what). |
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
offers to register it, `project-gaps` uses the 21-day default, and
`self-review` runs without ROLE CHECK.
