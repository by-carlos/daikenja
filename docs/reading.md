# Reading a ledger

Shared mechanism for the four read skills: `project-catchup`, `project-summary`,
`project-decisions`, `project-gaps`. All four resolve config, find a ledger, and
parse it the same way.
They differ only in what they filter for and how they format the result. This
document is that shared mechanism, written once so it cannot drift four ways.

A read skill implements this document plus its own filter and output shape. It
does not restate parsing rules from `ledger-format.md` or resolution rules from
`config-contract.md` -- those are the contracts. This document is the recipe
that combines them for a read, not a third contract.

## Step A: resolve the config

Read `~/.claude/daikenja/daikenja.yaml`, per `config-contract.md` § Resolution
order.

- **Absent.** Not fatal for a read. Continue on defaults: ledger at
  `.daikenja/ledger.md` under the current directory, `stale_after_days: 21`.
- **Malformed YAML.** Stop. Name the first line that does not parse. Never
  guess the intent and never rewrite the file.
- **Present and valid.** Match the current directory against every
  `projects:` entry's `path`, normalized (forward slashes, no trailing slash,
  case-insensitive) and longest-prefix-wins. No match means the project is
  unregistered: say so in one line and name `/daikenja:setup-project` as the
  skill that registers it, then continue -- an unregistered project still has a
  ledger to read if one exists on disk.

**Then check the version marker**, per `config-contract.md` § Version marker and
upgrades. That contract defines when the notice fires and how it is worded; this
step only says that a read skill emits it. It is one line, it never blocks the
read, and a read skill never migrates anything -- `setup-user` is the only skill
that does.

## Step B: resolve the ledger path

1. The matched project's `ledger:` key, if it has one -- resolved per its
   pointer form (relative or absolute), per `config-contract.md` § Resolving
   `ledger`. An explicit key is authoritative: the default filename in the
   next step is not also checked.
2. Otherwise `.daikenja/ledger.md` under the project root (or under the
   current directory, when nothing matched).
3. **A ledger found on disk wins over the config.** This applies only when no
   project matched at all -- check the default path even then. It does not
   apply to a matched project's explicit `ledger:` key: that key's resolved
   path is the ledger, whether or not a file happens to sit at the default
   location too.

**Name the resolved path before the answer**, every time, success or failure
-- one line, so someone who ran a read skill from the wrong directory can
tell which project's ledger they are looking at without digging. This is
always the fully resolved **absolute** path, even when the configured
`ledger:` value was relative:

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
Changelog into (timestamp, writer, summary) per § Section: Changelog, and
resolve the two summary compactions defined there before reading it: join any
indented continuation lines to the summary, then expand any
`<verb><first>..<last>` range into the individual IDs it stands for. A summary
read without doing both under-reports what a bulk write changed.

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
