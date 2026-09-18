# Config schema

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Schema -- project-list "Step 0: read the contracts"
- § Field notes -- preflight "Step 0: read the shared docs", preflight "The `Reviewed:` line is mandatory", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-list "Step 0: read the contracts", self-review "Step 0: read the shared docs", setup-project "Step 3: offer the per-project keys"
- § Digest groups -- digest "Step 0: read the contracts"

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

digest:                               # optional, read only by the digest skill
  ignore:                             # optional, item `sender` values dropped outright
    - <string>
  groups:                             # a list, in the order they are tried
    - name: <string>                  # required, the group's heading
      focus: <string>                 # required, what one paragraph should say
      channels:                       # optional, item `channel` values, as sent
        - <string>
      people:                         # optional, item `sender` values, as sent
        - <string>
      kind: summary                   # summary | people. Default: summary
      max_chars: 400                  # optional. Default: 400, clamped to 100..1000
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

## Digest groups

**`digest.groups` is read by the `digest` skill and by nothing else.** It says
what to do with the items a digest could not place against a registered
project: instead of one line per item under `Unmatched`, each group folds the
items it claims into one short paragraph. The block is optional. Without it
every unplaced item stays under `Unmatched`, exactly as before, and no other
skill changes behaviour because it is present.

**Project matching runs first and is not affected.** An item that a project
card claims goes to that project's group, with the project's open ledger items
beside it, and a group never sees it. Groups only ever see the remainder, so a
group whose channel a project card also owns simply never fills from that
channel -- the card wins, and that is the intended order.

**What a group matches on.** An item belongs to a group when its `channel` is
one of the group's `channels`, or its `sender` is one of the group's `people`.
Both compare the strings **as the feeder sent them**: trimmed, case folded, and
with a leading `#` or `@` ignored on either side, so `#team-alerts` and
`team-alerts` are the same channel and `@priya` and `priya` the same person.
Nothing else is compared -- not the summary, not the `topic`, not the `bucket`.
`sender` is whatever text the feeder chose to put there, so `people` is a list
of those texts; Daikenja never looks up who a person is, and a feeder that
sends display names needs display names here. A group with neither list can
never match and is reported once, per the failure table in `digest`.

**Groups are tried in file order and the first match wins.** An item listed
under two groups lands in the first one. Order the list so the more specific
group comes first, and do not expect an item to appear twice.

**`focus`** is the brief for the paragraph: what the group should say about
its items, in the user's own words. `name the decision or the blocker, not
every message` and `each announcement in one clause, with when it takes
effect` are both briefs; the skill writes the paragraph to it and nothing
else. A brief is a description of the wanted paragraph, never an instruction
to run anything, and the skill treats it as text.

**`kind`** is the paragraph's shape. `summary`, the default, is one prose
paragraph across the group's items. `people` is one clause per sender -- who
raised what -- for a group whose point is the people in it rather than the
theme. It changes the shape and nothing about matching: a `people` group still
matches on `channels` and `people` alike.

**`max_chars`** is the paragraph's budget, per group, because groups do not
cost the same: an announcements group that has to say what changed needs more
room than a chatter group that says what people talked about. Default 400. A
value below 100 reads as 100 and one above 1000 as 1000, and the run says so
once rather than refusing the block.

**Group names and members are entirely yours.** Nothing here has a built-in
group, a reserved name, or a default channel. What a user calls a group and
which channels go in it is what the block is for.

**`digest.ignore`** is the list of senders whose items are dropped before
anything else happens -- before project matching, before groups. It is for
bots and for the digest's own posts: a feeder that reads your DMs will hand
back yesterday's digest as an item, and the only thing that knows the name
that digest was posted under is this file. The strings compare exactly as
`people` does -- trimmed, case folded, a leading `@` ignored -- against the
`sender` the feeder sent, so the name has to be the one your feeder uses.
Dropped items are not in any group and are not counted as items; the header
says how many were ignored, once, so a digest that shrank has a stated reason.
The template lists `Daikenja` because that is the name the bot posts under
when it is set up as its README describes; change it if yours differs.

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

digest:
  groups:
    - name: Platform team
      focus: what the team is working through -- the decision or the blocker, not every message
      channels: ["#platform-requests", "#platform-alerts"]
      people: ["@priya", "@sam"]
    - name: Announcements
      focus: each announcement in one clause, naming what changed and when it takes effect
      channels: ["#announcements", "#releases"]
      max_chars: 700
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
