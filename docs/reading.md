# Reading a ledger

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Step A0: did the user name a project? -- project-decisions "Step 0: read the contracts", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts", project-sources "Step 0: read the contracts"
- § Step A: resolve the config -- preflight "Step 3: cycle 0 -- the substance checks", project-decisions "Step 0: read the contracts", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts", project-sources "Step 0: read the contracts"
- § Step B: resolve the ledger path -- preflight "Step 3: cycle 0 -- the substance checks", project-decisions "Step 0: read the contracts", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts", project-sources "Step 0: read the contracts", judgement "Step 3: place the subject"
- § Step C: read and parse -- preflight "Step 3: cycle 0 -- the substance checks", project-decisions "Step 0: read the contracts", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts", project-sources "Step 0: read the contracts", judgement "Step 3: place the subject"
- § Step D: resolve the staleness threshold -- project-gaps "Step 0: read the contracts"
- § Notices, shared wording -- project-decisions "Step 0: read the contracts", project-catchup "Step 0: read the contracts", project-gaps "Step 0: read the contracts", project-summary "Step 0: read the contracts", project-sources "Step 0: read the contracts"

Shared mechanism for the five read skills: `project-catchup`,
`project-summary`, `project-decisions`, `project-gaps`, `project-sources`. All
five take the same optional project-key argument, resolve config, find the
ledger -- the project's `DECISIONS.md` files and its `open.md` -- and parse it
the same way. They differ only in what they filter for
and how they format the result. This document is that shared mechanism,
written once so it cannot drift five ways. `preflight` also reads a ledger
through this document, for lookup only -- it is not one of the five and never
writes.

A read skill implements this document plus its own filter and output shape. It
does not restate parsing rules from `decisions-format.md` and `open-format.md`
or resolution rules from `config-resolution.md` -- those are the contracts.
This document is the recipe
that combines them for a read, not a third contract.

## Step A0: did the user name a project?

All five skills take an **optional project key** as an argument:
`/daikenja:project-summary atlas-migration`. A key may also arrive in prose --
"summarize atlas-migration", "what's open on the platform programme" -- when
the words match a registered key. Treat both the same way.

- **A key was given.** Carry it into Step A, which reads the file, and match it
  there per `config-resolution.md` § Finding the project, by key. It is decisive:
  skip directory matching entirely, and **never fall back to the current
  directory** if the key does not exist. Say which key was not found, list the
  registered ones, and stop.
- **No key was given.** Continue to Step A and resolve by directory, exactly as
  before. This is the ordinary case and it is unchanged.

**Name the project in the answer whenever a key was given**, alongside the
`Ledger:` line from Step B -- the user is reading about a project they are not
standing in, so the reply has to say which one.

## Step A: resolve the config

Read `~/.claude/daikenja/daikenja.yaml`, per `config-resolution.md` §
Resolution order.

- **Absent.** Not fatal for a read. Continue on defaults: `DECISIONS.md` and
  `.daikenja/open.md` under the current directory, `stale_after_days: 21`.
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
  no paths is not a candidate, per `config-resolution.md` § Legacy keys and
  unmigrated ledgers. No match means the project is unregistered: say so in one
  line and name `/daikenja:setup-project` as the skill that registers it, then
  continue -- an unregistered project still has ledger files to read if they
  exist on disk.
- **A legacy key on the matched entry** -- no paths, or a leftover `ledger:`
  -- gets its one line per `config-resolution.md` § Legacy keys and unmigrated
  ledgers. No paths stops the read for that project; a leftover `ledger:` is
  ignored and the read continues.

**Then check the version marker**, per `config-versioning.md` § Version marker
and upgrades. That contract defines when the notice fires and how it is worded; this
step only says that a read skill emits it. It is one line, it never blocks the
read, and a read skill never migrates anything -- `setup-user` is the only skill
that does.

## Step B: resolve the ledger path

Per `config-resolution.md` § Finding `DECISIONS.md` and `open.md`:

1. **`<path>/DECISIONS.md` for every path in the entry**, in `paths` order, plus
   any file a `Moved:` line in one of them names. A read skill reads all of
   them, per § Reading several repositories, not only the one under the current
   directory.
2. **`<home>/.daikenja/open.md`**, where home is the first path in the entry.
3. **No project matched:** both files under the current directory, and files
   found there win over the config.
4. **The legacy check runs first.** `.daikenja/ledger.md` at home with no
   `open.md` beside it means the ledger was never migrated: say so in one line
   per `config-resolution.md` § Legacy keys and unmigrated ledgers, read
   nothing, and stop.

**Name the files before the answer**, every time, success or failure -- one
line, so someone who ran a read skill from the wrong directory can tell which
project's ledger they are looking at without digging. Every path is absolute,
and a file that does not exist yet is marked so rather than left out:

```
Ledger: <path>/DECISIONS.md, <home>/.daikenja/open.md
```

A file of the pair that does not exist is read as empty: a repository with no
`DECISIONS.md` has no decisions recorded, and a missing `open.md` has no open
items, links or sources. When **none** of the files exists, a read skill does
**not** scaffold them. Report:

```
No ledger yet in <home>. Run /daikenja:project-log to create one.
```

and stop -- this notice already names the place, so the `Ledger:` line above
is not repeated. Reading is not the skill that creates the files.

**The project card, when a skill wants it, is beside `open.md`** -- its path
is derived from the home repository per `project-card.md` § Location, and
it is read per § Reading a card. Only the skills that say so read it
(`project-summary` shows it; `thread` matches against it); the other read
skills do not open it, and its absence is never a notice for a skill that did
not ask.

## Step C: read and parse

Read each file whole, version line first, per `open-format.md` § Version line:
a newer version is still read, with one warning per run; no version line reads
as version 1.

**`DECISIONS.md`**, per `decisions-format.md` § Shape: each `##` heading is an
area, its `Paths:` line the repository-relative paths it covers, and each
bullet one decision in force -- the bold rule, its why clause, `Revisit:` and
`Source:`. An area holding only a `Moved:` line has its entries in the file it
names. There are no IDs, dates or markers to parse: an entry is found by its
area and its words, and every entry in the file is in force.

**`open.md`**, per `open-format.md` § Reading rules for skills: locate
`## Open items`, `## Context links` and `## Sources` by their exact headings,
and report a missing one and ask before continuing over what remains. Split
each open item on ` -- ` at most twice into (date raised, owner, text), per §
Section: Open items; a text opening `Blocked by:` names another item in words,
per § `Blocked by:`. Context links and source head lines split once into
(label, target), and a source's field lines are read as `<name>: <value>` --
an absent field means unknown, never a default.

For both files: ignore other comments and blank lines, treat a two-space
indented markerless line as a continuation, and report -- not silently skip --
any other line that does not match its section's grammar.

**Never rewrite the file.** Only `project-log` writes. A read skill that finds a
malformed line reports it in its output and moves on; it does not fix it, even
when the fix is obvious.

## Step D: resolve the staleness threshold

Needed only by `project-gaps`, but the resolution order is shared with everything else
that reads config: the matched project's `stale_after_days`, otherwise the
profile's, otherwise 21. State which was used whenever the answer changes the
output, per `config-resolution.md` § Precedence.

## Notices, shared wording

Use these exact shapes so the five skills read as one system:

```
Ledger: <path>/DECISIONS.md, <home>/.daikenja/open.md
Project: <key>  (only when the user named one)
No project called <key> in daikenja.yaml. Registered: <key>, <key>, <key>.
<key> has no repository in daikenja.yaml and needs migration -- run /daikenja:setup-user.
<key> still has a ledger: key, which is no longer read -- run /daikenja:setup-user.
The ledger at <home>/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
<file> was written by a newer format (version <n>); update the Daikenja plugin.
Daikenja is not configured -- run /daikenja:setup-user.
This project is not in daikenja.yaml. Using the ledger files under <path> anyway.
No ledger yet in <home>. Run /daikenja:project-log to create one.
<file>, line <n>: <what is wrong>. Skipped.
"<item>" is blocked by "<words>", which names an item no longer open.
Using this project's <N>-day staleness threshold.
daikenja.yaml was written by Daikenja <recorded>; <installed> is installed -- run /daikenja:setup-user.
daikenja.yaml predates version tracking; <installed> is installed -- run /daikenja:setup-user.
```

## What each skill adds on top of this

| Skill | Filter | Output |
|---|---|---|
| `project-catchup` | `git log <sha>..HEAD -- DECISIONS.md .daikenja/open.md` per repository, from `last_checkpoint`, plus uncommitted changes to both files | what changed since the last report, per repository, then proposes advancing each SHA |
| `project-summary` | everything | oriented overview, no assumed context |
| `project-decisions` | every `DECISIONS.md`, matched against a query by area, `Paths:` and words | the entries in force, each naming its repository, with their history from git |
| `project-gaps` | Open items that are `@unassigned` or older than the staleness threshold | audit list, each reported item naming what it is `Blocked by:` if it says |
| `project-sources` | Sources section | staleness report -- which sources moved, comparing each stored `modified:` against what the source's system reports now; offers to record a re-read through `project-log` |
