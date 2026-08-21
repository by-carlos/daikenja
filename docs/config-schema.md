# Config schema

The full `daikenja.yaml` shape, key by key, and two worked examples. Companion
to [`config-resolution.md`](config-resolution.md), which holds where the file
lives and how a project, a ledger and a pointer resolve -- this document only
fixes what each key means and what it defaults to.

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
    ledger: .daikenja/ledger.md        # optional, relative to path
    last_checkpoint: 2026-08-14T09:12Z  # optional, written by project-catchup
    stale_after_days: <int>           # optional, overrides the profile value
    norms_doc: <path or url>          # optional, overrides the profile value
```

### Field notes

**`daikenja_version`** records which version of Daikenja last wrote this file.
`setup-user` stamps it on every successful run and nothing else ever writes it.
It exists so that a release which changes something already on a user's disk can
be detected and handled; the full rule is
[Version marker and upgrades](config-versioning.md#version-marker-and-upgrades).

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
[Resolving `writing_style` and `personas`](config-resolution.md#resolving-writing_style-and-personas),
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
