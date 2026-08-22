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
    paths:                            # optional, a list of absolute paths
      - <absolute path>
      - <absolute path>
    path: <absolute path>             # optional, the single-value form of paths
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
Because it reads the date field, **a backfilled item dated to its true origin is
usually stale the moment it is written**, and `project-gaps` reports it on the
very first run after a seed. That is the threshold working as specified rather
than a fault in the entries, and `setup-project` warns about it before seeding.

**`last_checkpoint`** is `YYYY-MM-DDThh:mmZ`, UTC, minute precision -- the same
timestamp format the ledger's Changelog uses. It marks how far `project-catchup` has
already reported.

**`paths` is the list of directories that resolve to this project**, and `path`
is its single-value form. A project may have several roots -- a programme
spanning three repositories is one project, not three -- and it may have none.
The three legal shapes are:

```yaml
projects:
  atlas:                       # one root, the single-value form
    path: C:/GitHub/atlas

  platform-programme:          # several roots, all resolving to one project
    paths:
      - C:/GitHub/platform-api
      - C:/GitHub/platform-web
      - C:/GitHub/platform-infra

  q4-planning:                 # no root at all, reachable only by key
    paths: []
    ledger: C:/Users/you/.claude/daikenja/ledgers/q4-planning.md
```

**`path` and `paths` mean the same thing and are read as one list.** A `path`
scalar is exactly a one-element `paths`, so every configuration written before
`paths` existed resolves identically after it. Nothing is deprecated and
nothing has to be rewritten. Writing both keys on one entry is a
[failure case](config-resolution.md#failure-behavior): the entry is read as the
union of the two and the run says so, because guessing which one the user meant
is worse than naming the contradiction.

**The first path is the project root**, which is what a relative `ledger:`
resolves against, per
[Finding the ledger](config-resolution.md#finding-the-ledger). It is the root
whichever of the project's directories the run started in, so one project keeps
one ledger. Order the list deliberately, and do not reorder it afterwards.

**A project with no roots is legal, not malformed.** `paths: []`, an empty
`paths:`, or neither key present all mean the same thing: this project is
reachable only by name. That is what a programme with no directory of its own
needs -- a body of work that lives across a wiki, a tracker and a chat space
has no folder to be, and before this it had to be recorded against whichever
folder happened to be open. Directory resolution skips such an entry silently;
it is not a match failure and never a warning. Give it an **absolute**
`ledger:`, since with no root there is nothing for a relative one to resolve
against; the convention is in
[Resolving `ledger`](config-resolution.md#resolving-ledger).

**The `<project-key>` is the project's name, and naming it resolves it.** Call
it whatever reads well -- it is still never matched against a directory. What
changed is that a skill accepts it as an argument, so a project can be read
from anywhere on disk rather than only from inside it. `project-log` accepts
one too, but only when the named entry has no paths -- the one case a key
alone is enough to say where a *write* belongs; naming a key that has paths is
refused rather than falling back to the directory you are standing in. See
[Finding the project](config-resolution.md#finding-the-project).

**`ledger`** is a **pointer**, not a fixed path. A pointer is a relative path or
an absolute path -- the same two forms `writing_style` and `personas` accept,
minus the `drive:` form. The full rule, including the recommended location for
a project with no repository of its own, is
[Resolving `ledger`](config-resolution.md#resolving-ledger).

## Worked example

A filled `daikenja.yaml` with four projects: one single-root, one that
overrides the global staleness threshold and points its ledger somewhere other
than the default, one spanning three repositories, and one with no repository
at all.

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

  platform-programme:
    paths:
      - C:/GitHub/platform-api
      - C:/GitHub/platform-web
      - C:/GitHub/platform-infra

  q4-planning:
    paths: []
    ledger: C:/Users/you/.claude/daikenja/ledgers/q4-planning.md
```

Resolving from `C:\GitHub\atlas\services\ingest`:

1. Normalized: `c:/github/atlas/services/ingest`.
2. `c:/github/atlas` is a prefix; no other path of any entry is.
3. Longest match is `atlas-migration`.
4. It has no `ledger:` key, so the ledger is `C:/GitHub/atlas/.daikenja/ledger.md`.
5. It has no `stale_after_days`, so `project-gaps` uses the profile's 21 days
   and says so.
6. It has no `norms_doc` and neither does the profile, so `self-review` skips
   ROLE CHECK.

Resolving from `C:\GitHub\platform-web\src`:

1. Normalized: `c:/github/platform-web/src`.
2. `c:/github/platform-web` is a prefix, and it is the second path of
   `platform-programme`.
3. The project is `platform-programme`. Its root is the **first** path,
   `C:/GitHub/platform-api`, so the ledger is
   `C:/GitHub/platform-api/.daikenja/ledger.md` -- the same file a run from
   `platform-infra` reads, which is the point of one project having one ledger.

Resolving `q4-planning` by name, from anywhere:

1. The key matches, so directory resolution never runs.
2. The entry has no paths, so nothing relative could resolve; its absolute
   `ledger:` is what gives it a location, and that is the file read.
3. `project-log q4-planning` writes there the same way: the entry has no
   paths, so the key is unambiguous, and the same absolute `ledger:` is what
   the entry lands in.

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
