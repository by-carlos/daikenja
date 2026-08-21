# Reading a ledger

Shared mechanism for the four read skills: `project-catchup`, `project-summary`,
`project-decisions`, `project-gaps`. All four take the same optional project-key
argument, resolve config, find a ledger, and parse it the same way.
They differ only in what they filter for and how they format the result. This
document is that shared mechanism, written once so it cannot drift four ways.

A read skill implements this document plus its own filter and output shape. It
does not restate parsing rules from `ledger-format.md` or resolution rules from
`config-contract.md` -- those are the contracts. This document is the recipe
that combines them for a read, not a third contract.

## Step A0: did the user name a project?

All four skills take an **optional project key** as an argument:
`/daikenja:project-summary atlas-migration`. A key may also arrive in prose --
"summarize atlas-migration", "what's open on the platform programme" -- when
the words match a registered key. Treat both the same way.

- **A key was given.** Carry it into Step A, which reads the file, and match it
  there per `config-contract.md` § Finding the project, by key. It is decisive:
  skip directory matching entirely, and **never fall back to the current
  directory** if the key does not exist. Say which key was not found, list the
  registered ones, and stop.
- **No key was given.** Continue to Step A and resolve by directory, exactly as
  before. This is the ordinary case and it is unchanged.

**Name the project in the answer whenever a key was given**, alongside the
`Ledger:` line from Step B -- the user is reading about a project they are not
standing in, so the reply has to say which one.

## Step A: resolve the config

Read `~/.claude/daikenja/daikenja.yaml`, per `config-contract.md` § Resolution
order.

- **Absent.** Not fatal for a read. Continue on defaults: ledger at
  `.daikenja/ledger.md` under the current directory, `stale_after_days: 21`.
  A key given in Step A0 has nothing to resolve against: say the configuration
  is missing, name `/daikenja:setup-user`, and stop.
- **Malformed YAML.** Stop. Name the first line that does not parse. Never
  guess the intent and never rewrite the file.
- **Present and valid, with a key from Step A0.** The project is already
  resolved. Go to Step B.
- **Present and valid, no key.** Match the current directory against every
  path of every `projects:` entry -- its `paths` list, or its `path` scalar
  read as a one-element list -- normalized (forward slashes, no trailing slash,
  case-insensitive) and longest-prefix-wins across all of them. An entry with
  no paths is not a candidate; it is reachable only by key. No match means the
  project is unregistered: say so in one line and name
  `/daikenja:setup-project` as the skill that registers it, then continue -- an
  unregistered project still has a ledger to read if one exists on disk.

**Then check the version marker**, per `config-contract.md` § Version marker and
upgrades. That contract defines when the notice fires and how it is worded; this
step only says that a read skill emits it. It is one line, it never blocks the
read, and a read skill never migrates anything -- `setup-user` is the only skill
that does.

## Step B: resolve the ledger path

1. The matched project's `ledger:` key, resolved relative to its **project
   root** -- the first path in its `paths`, or its `path` scalar. Not the path
   that matched: one project has one ledger, per `config-contract.md` §
   Finding the ledger.
2. Otherwise `.daikenja/ledger.md` under the project root, or under the current
   directory when no project matched.
3. **A ledger found on disk wins over the config.** Check the resolved path
   even when the project did not match.
4. **A project with no paths has no root.** There is nowhere to resolve a
   ledger, so stop with one line and read nothing:

   ```
   <key> has no path in daikenja.yaml, so its ledger has no location yet.
   ```

**Name the resolved path before the answer**, every time, success or failure
-- one line, so someone who ran a read skill from the wrong directory can
tell which project's ledger they are looking at without digging:

```
Ledger: <path>
```

If the file does not exist, a read skill does **not** scaffold it. Report:

```
No ledger at <path>. Run /daikenja:project-log to create one.
```

and stop -- this notice already names the path, so the `Ledger:` line above
is not repeated. Reading is not the skill that creates the file.

## Step C: read and parse

Read the whole ledger. Locate each of the four H2 sections by its exact
heading, per `ledger-format.md` § Reading rules. Apply those rules verbatim:
ignore comments and blank lines, treat a two-space indented markerless line as
a continuation, and report -- not silently skip -- any other line that does
not match the entry grammar.

Parse every Decisions and Open items entry into its four fields (date, id,
owner, body) plus tail, per `ledger-format.md` § Entry grammar. Parse the
Changelog into (timestamp, writer, summary) per § Section: Changelog.

**Never rewrite the file.** Only `project-log` writes. A read skill that finds a
malformed line reports it in its output and moves on; it does not fix it, even
when the fix is obvious.

## Step D: resolve the staleness threshold

Needed only by `project-gaps`, but the resolution order is shared with everything else
that reads config: the matched project's `stale_after_days`, otherwise the
profile's, otherwise 21. State which was used whenever the answer changes the
output, per `config-contract.md` § Precedence.

## Notices, shared wording

Use these exact shapes so the four skills read as one system:

```
Ledger: <path>
Project: <key>  (only when the user named one)
No project called <key> in daikenja.yaml. Registered: <key>, <key>, <key>.
<key> has no path in daikenja.yaml, so its ledger has no location yet.
Daikenja is not configured -- run /daikenja:setup-user.
This project is not in daikenja.yaml. Using the ledger at <path> anyway.
No ledger at <path>. Run /daikenja:project-log to create one.
Line <n>: <what is wrong>. Skipped.
Using this project's <N>-day staleness threshold.
daikenja.yaml was written by Daikenja <recorded>; <installed> is installed -- run /daikenja:setup-user.
daikenja.yaml predates version tracking; <installed> is installed -- run /daikenja:setup-user.
```

## What each skill adds on top of this

| Skill | Filter | Output |
|---|---|---|
| `project-catchup` | Changelog lines newer than `last_checkpoint` | delta by ID, then proposes advancing the checkpoint |
| `project-summary` | everything | oriented overview, no assumed context |
| `project-decisions` | Decisions section, matched against a query | dated entries with links |
| `project-gaps` | Open items with `- [ ] ` and (`@unassigned` or older than the staleness threshold) | audit list |
