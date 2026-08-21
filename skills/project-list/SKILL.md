---
name: project-list
description: Lists every project registered in daikenja.yaml, says which one the current directory resolves to, and reports whether each project's ledger actually exists. Use when the user says "what projects does Daikenja know about", "list my projects", "which project am I in", "why can't it find my ledger", "check my Daikenja setup", or asks anything shaped like a doctor or health check. Also the skill to reach for when a read skill reported a project it did not expect, or reported none. Read-only; writes nothing, and never repairs what it reports.
metadata:
  owner: Carlos
  version: 1
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
  § Finding the ledger and § Resolving `ledger`. This skill reports what that
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

## Step 2: resolve every entry

For each entry, in the order the file lists them, work out four facts and
nothing more:

1. **Its paths** -- the `paths` list, or the `path` scalar read as a
   one-element list, or none. An entry with both keys is read as the union of
   the two and flagged; see the failure table.
2. **Whether each path exists on disk.** A path that does not exist is
   reported, not corrected. It is often a detached drive or a machine the
   config is shared with, and neither is a mistake.
3. **Its ledger path** -- the `ledger:` key resolved per its pointer form,
   relative or absolute, otherwise `.daikenja/ledger.md` under the project
   root. The root is the **first** path in the entry, per
   `config-resolution.md` § Finding the ledger. An entry with no paths has no
   root, so only an **absolute** `ledger:` gives it a path at all; where there
   is neither, say there is no location rather than inventing one.
4. **Whether that ledger file exists.**

Then resolve the current directory the ordinary way -- longest matching prefix
across every path of every entry -- and mark which entry it lands in. Marking
the current project is the point of running this from a terminal at all.

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
  `.daikenja/ledger.md`.
- The VCS root of the current directory, if it is above the current directory,
  and the same three levels beneath it.

Report every hit that no registered project's ledger path already accounts
for. If the scan found nothing, say so in one line -- "no unregistered ledgers
under `<dir>`" is a result, and it tells the user the search happened.

## Step 4: report

One block, per `response-format.md`. The current project is marked, the
findings are itemised, and nothing that resolved cleanly gets more than its
line:

```
Daikenja knows about 4 projects. You are in atlas-migration.

atlas-migration  <- you are here
  path    C:/GitHub/atlas
  ledger  C:/GitHub/atlas/.daikenja/ledger.md

platform-programme
  paths   C:/GitHub/platform-api        (root)
          C:/GitHub/platform-web
          C:/GitHub/platform-infra      missing on disk
  ledger  C:/GitHub/platform-api/.daikenja/ledger.md

billing-api
  path    C:/GitHub/billing-api
  ledger  C:/GitHub/billing-api/.daikenja/ledger.md    no such file

q4-planning
  paths   none -- reachable by name only
  ledger  C:/Users/rimuru/.claude/daikenja/ledgers/q4-planning.md

Unregistered ledger found under C:/GitHub:
  C:/GitHub/scratch-notes/.daikenja/ledger.md
  -- run /daikenja:setup-project in that directory to register it.
```

**Findings get a named next step; clean lines get nothing.** A missing ledger
names `/daikenja:project-log`, a missing directory or an unregistered ledger
names `/daikenja:setup-project`, and an entry that resolves says only what it
resolves to. A report where every line carries advice is a report nobody
finishes reading.

**Say when nothing is wrong.** "All 4 projects resolve, and every ledger
exists" is the answer to the question the user actually asked, and it belongs
at the top when it is true.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Say so, name `/daikenja:setup-user`, stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| `projects:` absent or empty | Not a failure. Say there are none, name `/daikenja:setup-project`, and still run the Step 3 scan. |
| An entry has both `path` and `paths` | Report it as one finding naming the key, list the union, and name `/daikenja:setup-project` as where it is fixed. Never rewrite the file. |
| A path in `paths` does not exist on disk | Report it beside that path. Not an error -- a detached drive and a shared config both look like this. |
| An entry has no paths | Report it as reachable by name only. Its ledger is whatever an absolute `ledger:` points at; with no such key, report that it has no ledger location and name `/daikenja:setup-project`. Not an error either way. |
| A ledger path is unreadable (permissions) | Report the error text beside the ledger line and carry on to the next entry. One bad entry never ends the listing. |
| The Step 3 scan cannot read a directory | Skip it silently and say the scan was partial. Never stop the report for it. |
| The user names one project | Report just that entry, in the same shape. An unknown key stops with the registered keys listed, per `config-resolution.md` § Finding the project. |
