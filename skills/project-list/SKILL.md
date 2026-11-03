---
name: project-list
description: Lists every project registered in daikenja.yaml, says which one the current directory resolves to, and reports whether each project's ledger actually exists. Read-only; it never repairs what it reports.
metadata:
  owner: Carlos
  version: 2
disable-model-invocation: true
---

# Project list

The index, read back. Every other skill resolves one project and gets on with
the job; this one shows the whole `projects:` block, what each entry resolves
to, and where that disagrees with what is on disk.

**It writes nothing and repairs nothing.** A wrong path, a missing ledger and
an unregistered ledger are all reported here and fixed elsewhere -- by
`/daikenja:setup-project` for the config, by `/daikenja:project-log` for a
ledger that does not exist yet. Naming the skill that fixes a finding is part
of the report; performing the fix is not.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` -- § Schema and § Field notes.
  The shapes a `projects:` entry may take are what this skill reports back.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- § Finding the project,
  § Finding `DECISIONS.md` and `open.md` and § Legacy keys and unmigrated
  ledgers. This skill reports what that
  document defines; it does not define anything itself.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-versioning.md` -- the version-marker notice
  this skill emits and never acts on.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply is shaped.

## Step 1: read the configuration

Read `~/.claude/daikenja/daikenja.yaml`.

- **Absent.** Say so, name `/daikenja:setup-user`, and stop. There is no index
  to list.
- **Malformed YAML.** **Stop.** Name the first line that does not parse. Never
  guess the intent and never rewrite the file -- the same rule every Daikenja
  skill follows.
- **Present and valid.** Also check the version marker and emit the one-line
  notice if it applies, per `config-versioning.md` § Version marker and
  upgrades.

**`projects:` absent or empty is not a failure.** Say there are no registered
projects and name `/daikenja:setup-project`, then still run Step 3 -- an
unregistered ledger on disk is exactly what the user needs to hear about in
that state.

## Step 1a: did the user name a project?

**The user may name a project** -- `/daikenja:project-list <key>`, or the key
in prose. A key was given: resolve it per `config-resolution.md` § Finding the
project, by key -- decisive, skip directory matching entirely, and never fall
back to the current directory. No match: say which key was not found, list the
registered keys, and stop -- Step 2 does not run and no report follows.

A key that resolves narrows the rest of this skill to that one entry: Step 2
runs only against it and the directory resolution it otherwise performs does
not run at all -- the key is decisive and the current directory is irrelevant,
per `config-resolution.md` -- and Step 3's scan is rooted at the entry's own
paths instead of the current directory, per Step 3 below. No key given:
continue exactly as before.

## Step 2: resolve every entry

**When a key was given (Step 1a), this step runs only for that one entry** --
skip every other entry, including their disk and ledger checks, since they
will not appear in the report.

For each entry, in the order the file lists them, work out four facts and
nothing more:

1. **Its paths** -- the `paths` list, or the `path` scalar read as a
   one-element list. An entry with both keys is read as the union of the two
   and flagged; see the failure table. **An entry with no paths** (`paths: []`,
   or neither key) is not a project this layout can hold: report it as "needs
   migration" with the `reading.md` § Notices line naming the key and
   `/daikenja:setup-user`, and skip the other three facts for it.
2. **Whether each path exists on disk.** A path that does not exist is
   reported, not corrected. It is often a detached drive or a machine the
   config is shared with, and neither is a mistake.
3. **Its ledger files** -- `<path>/DECISIONS.md` for every path, and
   `<home>/.daikenja/open.md`, where home is the **first** path, per
   `config-resolution.md` § Finding `DECISIONS.md` and `open.md`. A leftover
   `ledger:` key is not read: say so on the entry, per § Legacy keys and
   unmigrated ledgers.
4. **Whether each of those files exists.** A home with `.daikenja/ledger.md`
   and no `open.md` beside it is an unmigrated ledger: report the entry as
   needing migration, naming `/daikenja:setup-user`, whether or not a
   `DECISIONS.md` exists.

Then resolve the current directory the ordinary way -- longest matching prefix
across every path of every entry -- and mark which entry it lands in. Marking
the current project is the point of running this from a terminal at all.
**Skip this directory resolution entirely when a key was given** -- the entry
is already decided, and the current directory plays no further part in the
run.

**Never open a ledger.** Existence is the whole question here. Reading content
is what the five read skills are for, and this skill has no business knowing
what is inside.

## Step 3: look for unregistered ledgers

A ledger on disk with no entry pointing at it is the single most useful thing
this skill finds: it is what a person has when they logged decisions from the
wrong directory and then could not find them again.

**The scan is bounded, and the report says where it looked.** There is no
whole-disk search -- it would be slow, it would surprise, and it would read
directories nobody asked about. Look in exactly two places:

- The current directory tree, to a depth of **three directories**, for
  `.daikenja/open.md` and the legacy `.daikenja/ledger.md`.
- The VCS root of the current directory, if it is above the current directory,
  and the same three levels beneath it.

Report every hit that no registered project's home already accounts for. A
legacy `ledger.md` with no `open.md` beside it is reported as needing
migration, naming `/daikenja:setup-user`. A `DECISIONS.md` alone is never a
hit: other tools write that file, so its presence does not mean a Daikenja
project lives there. If the scan found nothing, say so in one line -- "no unregistered ledgers
under `<dir>`" is a result, and it tells the user the search happened.

**When a key was given (Step 1a), scope the scan to the named entry's own
paths instead.** The run may not be standing anywhere near the project it was
asked about, so the current directory has nothing to do with this. For each of
the entry's paths, scan to the same three-directory depth for the same two
files, and report any hit that is not the `open.md` already resolved for it in
Step 2. Skip the VCS-root leg entirely -- there is no VCS root relationship to
a directory this run never visited.

## Step 4: report

One block, per `response-format.md`. The current project is marked, the
findings are itemised, and nothing that resolved cleanly gets more than its
line:

```
Daikenja knows about 4 projects. You are in atlas-migration.

atlas-migration  <- you are here
  path    C:/GitHub/atlas
  ledger  C:/GitHub/atlas/DECISIONS.md
          C:/GitHub/atlas/.daikenja/open.md

platform-programme
  paths   C:/GitHub/platform-api        (home)
          C:/GitHub/platform-web
          C:/GitHub/platform-infra      missing on disk
  ledger  C:/GitHub/platform-api/DECISIONS.md
          C:/GitHub/platform-web/DECISIONS.md    not created yet
          C:/GitHub/platform-api/.daikenja/open.md

billing-api
  path    C:/GitHub/billing-api
  ledger  none yet -- run /daikenja:project-log to create one

q4-planning
  q4-planning has no repository in daikenja.yaml and needs migration -- run /daikenja:setup-user.

Unregistered ledger found under C:/GitHub:
  C:/GitHub/scratch-notes/.daikenja/open.md
  -- run /daikenja:setup-project in that directory to register it.
```

**Findings get a named next step; clean lines get nothing.** A project with no
ledger files names `/daikenja:project-log`, a missing directory or an
unregistered ledger names `/daikenja:setup-project`, an entry needing migration
names `/daikenja:setup-user`, and an entry that resolves says only what it
resolves to. A repository with no `DECISIONS.md` yet is marked so on its line
and is not a finding: it has no decisions recorded. A report where every line carries advice is a report nobody
finishes reading.

**Say when nothing is wrong.** "All 4 projects resolve, and every ledger
exists" is the answer to the question the user actually asked, and it belongs
at the top when it is true.

**When a key was given (Step 1a), the report covers only that entry.** No
project count, no "You are in" framing -- there is no current directory in
play -- and no `<- you are here` marker. Lead with `Project: <key>`, then the
one entry's block exactly as Step 2 produces it, then Step 3's scoped scan
result:

```
Project: harbor-migrator

harbor-migrator
  path    C:/GitHub/harbor/tools/migrator
  ledger  none yet -- run /daikenja:project-log to create one

no unregistered ledgers under C:/GitHub/harbor/tools/migrator
```

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Say so, name `/daikenja:setup-user`, stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| `projects:` absent or empty | Not a failure. Say there are none, name `/daikenja:setup-project`, and still run the Step 3 scan. |
| An entry has both `path` and `paths` | Report it as one finding naming the key, list the union, and name `/daikenja:setup-project` as where it is fixed. Never rewrite the file. |
| A path in `paths` does not exist on disk | Report it beside that path. Not an error -- a detached drive and a shared config both look like this. |
| An entry has no paths (`paths: []`) | Report it as needing migration with the § Notices line naming `/daikenja:setup-user`. It is never listed as reachable by name. |
| An entry still has a `ledger:` key | Note on the entry that the key is no longer read, naming `/daikenja:setup-user`, and report the fixed-path files as normal. |
| The home has `.daikenja/ledger.md` and no `open.md` | Report the entry as needing migration, naming `/daikenja:setup-user`, whether or not a `DECISIONS.md` exists. Never open the old file. |
| A ledger file is unreadable (permissions) | Report the error text beside the ledger line and carry on to the next entry. One bad entry never ends the listing. |
| The Step 3 scan cannot read a directory | Skip it silently and say the scan was partial. Never stop the report for it. |
| The user names one project | Step 1a resolves it by key and Step 4 reports just that entry, in the same shape. An unknown key stops with the registered keys listed, per `config-resolution.md` § Finding the project. |
