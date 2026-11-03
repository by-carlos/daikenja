# Config schema

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Schema -- project-list "Step 0: read the contracts"
- § Field notes -- preflight "Step 0: read the shared docs", preflight "The `Reviewed:` line is mandatory", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-list "Step 0: read the contracts", self-review "Step 0: read the shared docs", setup-project "Step 3: offer the per-project keys"

The full `daikenja.yaml` shape, key by key, and two worked examples. Companion
to [`config-resolution.md`](config-resolution.md), which holds where the file
lives and how a project, its ledger files and a pointer resolve -- this document only
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
    paths:                            # required (or path), a list of absolute paths
      - <absolute path>               # the first is the home repository
      - <absolute path>
    path: <absolute path>             # the single-value form of paths
    last_checkpoint:                  # optional, written by project-catchup
      <absolute path>: <commit SHA>   # one per registered repository
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

**`last_checkpoint`** is a map from each registered repository path to the
commit SHA `project-catchup` last reported up to in that repository. The next
run reports `git log <sha>..HEAD -- DECISIONS.md .daikenja/open.md` per
repository, so git, not a timestamp, says what changed. Each path is written
exactly as it appears in `paths`. A repository with no entry in the map, or
whose SHA no longer resolves (a rewritten history, a fresh clone), is a first
run for that repository, and the report says so. A scalar value -- the UTC
timestamp written before this layout -- is read the same way: a first run, with
the reason stated. `project-catchup` replaces it with the map on its next
write.

**`paths` is the list of repositories that make up this project**, and `path`
is its single-value form. Every project lives in at least one git repository,
because git is what keeps its ledger's history. A project may have several --
a programme spanning three repositories is one project, not three. The two
legal shapes are:

```yaml
projects:
  atlas:                       # one root, the single-value form
    path: C:/GitHub/atlas

  platform-programme:          # several roots, all resolving to one project
    paths:
      - C:/GitHub/platform-api
      - C:/GitHub/platform-web
      - C:/GitHub/platform-infra
```

**`path` and `paths` mean the same thing and are read as one list.** A `path`
scalar is exactly a one-element `paths`, so every configuration written before
`paths` existed resolves identically after it. Nothing is deprecated and
nothing has to be rewritten. Writing both keys on one entry is a
[failure case](config-resolution.md#failure-behavior): the entry is read as the
union of the two and the run says so, because guessing which one the user meant
is worse than naming the contradiction.

**The first path is the home repository**, which is where the project's one
`.daikenja/open.md` lives, per
[Finding `DECISIONS.md` and `open.md`](config-resolution.md#finding-decisionsmd-and-openmd).
Every path, home included, has its own `DECISIONS.md` at its root. Home is the
first path whichever of the project's directories the run started in, so one
project keeps one `open.md`. `setup-project` asks which repository is home and
writes it first; do not reorder the list afterwards.

**An entry with no paths, and a leftover ledger pointer, are legacy.** Both
come from before every project lived in a repository. A reader reports the
first as needing migration and ignores the second, each in one line pointing at
`setup-user`, per
[Legacy keys and unmigrated ledgers](config-resolution.md#legacy-keys-and-unmigrated-ledgers).
Neither is written any more.

**The `<project-key>` is the project's name, and naming it resolves it.** Call
it whatever reads well -- it is still never matched against a directory. What
changed is that a skill accepts it as an argument, so a project can be read
from anywhere on disk rather than only from inside it. See
[Finding the project](config-resolution.md#finding-the-project).

## Worked example

A filled `daikenja.yaml` with three projects: one single-repository, one that
overrides the global staleness threshold, and one spanning three
repositories.

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
    last_checkpoint:
      C:/GitHub/atlas: 4f9c2e1

  billing-api:
    path: C:/GitHub/billing-api
    stale_after_days: 30
    norms_doc: https://example.com/platform/ways-of-working

  platform-programme:
    paths:
      - C:/GitHub/platform-api
      - C:/GitHub/platform-web
      - C:/GitHub/platform-infra
    last_checkpoint:
      C:/GitHub/platform-api: 9a1b7d3
      C:/GitHub/platform-web: e02c5f8
```

Resolving from `C:\GitHub\atlas\services\ingest`:

1. Normalized: `c:/github/atlas/services/ingest`.
2. `c:/github/atlas` is a prefix; no other path of any entry is.
3. Longest match is `atlas-migration`.
4. Its ledger is `C:/GitHub/atlas/DECISIONS.md` and
   `C:/GitHub/atlas/.daikenja/open.md`.
5. It has no `stale_after_days`, so `project-gaps` uses the profile's 21 days
   and says so.
6. It has no `norms_doc` and neither does the profile, so `self-review` skips
   ROLE CHECK.

Resolving from `C:\GitHub\platform-web\src`:

1. Normalized: `c:/github/platform-web/src`.
2. `c:/github/platform-web` is a prefix, and it is the second path of
   `platform-programme`.
3. The project is `platform-programme`. A read skill reads all three
   `DECISIONS.md` files, one per path. Home is the **first** path,
   `C:/GitHub/platform-api`, so open items are
   `C:/GitHub/platform-api/.daikenja/open.md` -- the same file a run from
   `platform-infra` reads, which is the point of one project having one
   `open.md`.
4. `last_checkpoint` has no entry for `C:/GitHub/platform-infra`, so
   `project-catchup` treats that repository as a first run and says so, while
   reporting the other two from their SHAs.

### Minimal valid file

The least a file can contain and still be usable. Every other key is optional:

```yaml
profile:
  name: Carlos
```

With that file alone, `compose` works with the default voice, `project-log`
scaffolds and writes `DECISIONS.md` and `.daikenja/open.md` in whatever
repository it runs in and
names `setup-project` as the way to register it, `project-gaps` uses the 21-day
default, and `self-review` runs without ROLE CHECK.

It has no `daikenja_version`, so every skill that reads it adds the one-line
version notice until `setup-user` has run once and stamped it. That is the
intended behaviour for a file written by hand, not a defect in the example.
