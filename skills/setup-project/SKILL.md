---
name: setup-project
description: Registers the project you are in with Daikenja, sets its per-project settings, and optionally seeds its ledger from sources the project already has.
metadata:
  owner: Carlos
  version: 4
  writes: ~/.claude/daikenja/daikenja.yaml -- one projects entry, either the one matching the current directory, the one the user names it should join, or a new one; the project card at <home>/.daikenja/project.md, only when none exists or when a migration moves it there; a new git repository, only when the user accepts the git init offer for a plain folder or a migration target; and, in a migration, the old ledger renamed to its dated backup beside it
disable-model-invocation: true
---

# Setup project

Registering a project is a per-project act with a per-project lifetime.
`setup-user` is a per-person act, run once. Keeping them in one skill meant
every new repository cost a full personal-setup run, which is what this skill
exists to end.

**Slash-only on purpose.** It writes `daikenja.yaml`, and its seeding step can
propose dozens of ledger entries. Nothing about "set this up" should make that
fire on its own -- the user runs `/daikenja:setup-project` when they mean to.
`disable-model-invocation: true` is set for that reason.

**This skill never writes ledger content.** The ledger is `DECISIONS.md` at
each registered repository's root and `.daikenja/open.md` in the home
repository. Seeding derives candidate entries and hands them to
`/daikenja:project-log`, which shows the exact lines, waits for approval and
scaffolds either file from its template. `project-log` remains the only writer
of both, per `docs/config-writers.md` § Who writes what.

**Every project lives in a git repository**, because git is where the ledger
keeps its history. A project with no folder cannot be registered.

## Step 0: the preconditions

Read `~/.claude/daikenja/daikenja.yaml`. Three outcomes and no others:

- **It does not exist.** Stop. Say so and name the skill that creates it:

  ```
  Daikenja is not configured yet -- there is no ~/.claude/daikenja/daikenja.yaml.
  Run /daikenja:setup-user first. Nothing was written.
  ```

- **It exists but does not parse.** **Stop.** Name the first line that does not
  parse. Never guess the intent and never rewrite a file you cannot parse --
  the same rule every Daikenja skill follows.

- **It exists but `profile.name` is unset or empty.** Stop. The configuration is
  incomplete, and `setup-user` is what completes it. Say so and name it.

On a file that exists and parses, also check the version marker and emit the
one-line notice if it applies, per `docs/config-versioning.md` § Version marker
and upgrades. It never blocks registration. **This skill does not run the version
upgrade and does not write `daikenja_version`**, even though it writes to the
same file -- the upgrade branch lives in `setup-user` and stays there. The one
migration here, Step 2a, is per project, and `setup-user` hands off to it.

This skill never captures profile data. If the user offers a name, role or tone
here, record nothing and point at `/daikenja:setup-user`.

## Step 1: read what already exists

**A project key given as the argument** (`/daikenja:setup-project atlas`)
names the entry to migrate, for a project no directory can match -- one with
no paths. It goes straight to Step 2a; a key that needs no migration is
treated as if run from its home repository.

Before proposing anything:

- The current directory's **normalized path** -- forward slashes, no trailing
  slash, compared case-insensitively, per `docs/config-resolution.md` § Finding
  the project.
- **Whether it is a git repository**: `git -C <dir> rev-parse --show-toplevel`.
  Read-only; it decides whether Step 2 offers `git init`.
- **Every path of every `projects:` entry** -- its `paths` list, or its `path`
  scalar read as a one-element list -- normalized the same way, and whether any
  is an **exact match** for this directory.
- For a matched entry, which ledger files exist, per `config-resolution.md`
  § Finding `DECISIONS.md` and `open.md`: `DECISIONS.md` at the root of each
  path, and `.daikenja/open.md` in the home repository, the **first** path.
  This decides whether Step 4 is a first seed or a top-up, and it is read-only
  here.

**Ledger files on disk with no matching entry are a normal state.** The files
are the fact and the config is the index: register the project and leave them
exactly as they are. A `DECISIONS.md` another tool wrote, plan-staged-rollout
for one, is adopted the same way, never replaced.

## Step 2: register the project

**Refuse outright** when the current directory is the user's home directory or
`~/.claude`. Neither is a project. Say so and write nothing.

- **An exact path match already exists**, on any path of any entry. Say which
  key it is registered under and leave the entry alone. Registration is
  idempotent, and it is not a place to silently change a key someone chose. Go
  to Step 3 -- an already-registered project can still want its keys set or its
  ledger seeded.

  **A matched entry that needs migration**, per
  `${CLAUDE_PLUGIN_ROOT}/docs/ledger-migration.md` § Which projects need
  migration, goes to Step 2a before anything else.

- **No match.** Ask one question before proposing anything, because there are
  two answers and only the user knows which one is meant:

  ```
  Is this a new project, or another repository of one you already track?
  Registered: <key>, <key>, <key>.
  ```

  - **A new project.** Propose a new entry, key defaulting to the directory's
    own name, and ask in the same round whether the project spans other
    repositories and, if so, **which one is home** -- where `open.md` and the
    project card live. The key is a human label and is never matched against a
    directory, so it may be anything that reads well -- but it is what a read
    skill accepts as an argument, so short and typeable beats decorative. Home
    goes **first** in `paths`, per `config-resolution.md` § Finding
    `DECISIONS.md` and `open.md`; with one repository, it is home:

    ```yaml
    <dir-name>:
      paths:
        - <home repository>
        - <other repository>
    ```

  - **Another repository of an existing project.** Append this path to that
    entry's `paths`, and change nothing else. **Appending never reorders the
    list**: the first path is home, and moving it would silently repoint
    `open.md` and the card at a different folder. Say which repository stays
    home.

    An entry written in the single-value `path:` form is converted to a
    two-element `paths:` list, with the existing value first. Say so in the
    proposal -- it is the same project resolving the same way, but the file
    now looks different from how the user left it.

**Every path written is a git repository.** For each one, Step 1's check
decides:

- **The repository root.** Register it as it stands.
- **Inside a repository, below its root.** Propose the root `rev-parse`
  printed; register the sub-folder only when the user asks for it.
- **Not a git repository** -- a plain folder for non-code work: notes, a
  programme, a bid. Offer `git init` in one line, and take no for an answer:

  ```
  <path> is not a git repository. Daikenja keeps the ledger's history in git,
  so a project has to live in one. Run git init there? Nothing is registered
  otherwise.
  ```

  On a yes, run `git init` in that folder and continue. On a no, write nothing
  and say so. Never register a folder that is not a repository.

**A project with no folder** -- a programme spread across a wiki, a tracker and
a chat space -- gets the same offer for a new folder named after its key. Never
write an entry with no paths, and never invent one.

**A prefix match that is not exact is a nested project.** The current directory
sits inside a registered one. Say which project it resolves to today and ask
before registering a second entry -- resolution takes the longest matching
prefix, so a new inner entry silently takes over every skill run in this
subtree. That is sometimes exactly what the user wants and is never something
to assume. Adding this directory to the outer project instead is the other
answer, and it is often the one meant.

Add the entry with the Edit tool, under `projects:`. **Never write a `ledger:`
key** -- the files sit at fixed paths. **Never rewrite the file.** Hand-added
keys, other projects and the template's comments all survive an edit and none
of them survive a regeneration.

## Step 2a: migrate an old ledger

Read `${CLAUDE_PLUGIN_ROOT}/docs/ledger-migration.md` in full and follow it for
this one project: it is the procedure, and nothing here restates it. In short,
the old ledger's in-force decisions and open items become one batch handed to
`/daikenja:project-log`, shown with the config edit, the card move and the
dated backup, and **nothing is written until the user approves it whole**.

What this skill writes itself, after that yes and in the order the procedure
sets: `git init` in a new target folder, the backup copy, the config edit to
this entry, the card move, and the removal of the old ledger. The entries are
`project-log`'s.

A declined migration writes nothing and leaves the old ledger exactly where it
was; say the project stays unread until it is migrated. After a completed one,
carry on to Step 3 -- Step 4 is reachable again, because the ledger is now
`DECISIONS.md` and `open.md`.

## Step 3: offer the per-project keys

`setup-user` left these unset because it had no idea what the project was. This
skill does, so it offers them once rather than leaving them to be discovered.
Ask in one short round, and take silence as "leave them all unset":

```
Registered. Two optional settings for this project -- skip either or both:

1. stale_after_days -- how long an open item may sit before project-gaps calls
   it stale. Inherits <the profile value> if you skip it.
2. norms_doc -- your team's ways-of-working document, as a path or a URL.
   Setting it turns on self-review's ROLE CHECK, which is off by default.
```

Both are optional and both have a defined default in `docs/config-schema.md`
§ Field notes. **Write only the keys the user answers.** A key written at its
own default value is noise that reads like a deliberate override to the next
person who opens the file.

**Never write `last_checkpoint` here.** It belongs to `project-catchup`, which
sets it after it has actually reported a delta; written at registration, it
would make the first catchup skip everything older than this moment.

State the values you are about to write and wait for a yes, then edit them into
the entry from Step 2.

## Step 3b: offer the project card

The registry entry says where the project is. The **project card** says what
it is about -- one paragraph of scope, the channels, repositories and trackers
it owns, and the people on it -- and it is what lets a thread or a report be
checked against this project from anywhere, per
`${CLAUDE_PLUGIN_ROOT}/docs/project-card.md`. Read that document's § Location
and § Format before proposing one.

The card is `<home>/.daikenja/project.md`, home being the entry's first path,
per `project-card.md` § Location. Then:

- **A card already exists there.** Say so and leave it alone. This skill
  never inspects or rewrites an existing card; the user edits it by hand.
- **No card.** Offer it in one round, and take silence as no:

  ```
  Want a project card? One paragraph on what <key> is about, the channels,
  repos and trackers it owns, and who is on it -- it is what lets a thread be
  matched to this project from anywhere. Answer in prose or skip it.
  ```

  From the answer, fill `${CLAUDE_PLUGIN_ROOT}/templates/project.md` with
  `{{PROJECT}}` replaced by the key, the Scope paragraph in the user's own
  words, one `- <kind>: <handle>` line per handle they named, and one
  `- @handle -- role` line per person. Show the exact file, wait for a yes,
  and write it with the Write tool. A user who wants the card but has nothing
  to say yet gets the blank template, comments and all -- an empty card is a
  place to write, and better than none.

`project-log` does not scaffold the card when it scaffolds `open.md`, and no
read skill does: this step is the only place a card is created.

## Step 4: offer to seed the ledger

Optional, and **reachable on its own.** A project registered months ago can run
`/daikenja:setup-project` purely to seed, and Steps 2 and 3 will both be no-ops
that say so. Offer it in one line and take no for an answer:

```
Want to seed the ledger from what this project already has -- a decision log,
a wiki space, a Slack channel, a README? I will propose entries and write
nothing without your approval. Otherwise we are done.
```

### Step 4a: look for a register the project already keeps

**Do this before asking for sources, not after.** Many projects already keep
architecture decision records, RFCs, a decision log, a numbered question
register or a `DECISIONS.md`, and finding that out on the fifth exchange means
several rounds of entries have already been proposed against a source that
turns out to be superseded.

Look for the usual homes -- `DECISIONS.md` at each registered repository's
root, `docs/adr/`, `doc/adr/`, `docs/decisions/`, `docs/rfc/`, `adr/`,
`decisions/`, or a file whose name says the same thing. This is a scan of file
names in each registered repository, not a read of it for material:
`project-log`'s rule against reading the repository is about inventing
material, and here the user asked and sees the results first.

- **A `DECISIONS.md` already exists.** Say so: it is adopted as it stands, its
  entries are already the ledger's decisions, and seeding adds only what it
  lacks -- `project-log`'s duplicate check enforces that. It is never
  overwritten or reformatted.
- **An ADR folder or a decision register.** Say plainly that the ledger is the
  index and those documents are the depth, because the honest first read of
  such a project is "you may not need Daikenja here":

  ```
  This project already keeps 4 decision records in docs/adr/ and a numbered
  question register. Daikenja does not replace those. What it adds is one place
  that answers "what is settled, what is open, who owns it" across all of them.
  Each decision would be one entry naming the record that holds the detail.
  ```

Three rules follow, and all three have to be settled before the first write:

- **One entry per decision still in force, naming its record.** The entry
  states the rule and its `Source:` names the record (`Source: ADR-0004`), the
  newest on the subject only. A record another one replaced is history and is
  not proposed: `DECISIONS.md` is current-only, per
  `${CLAUDE_PLUGIN_ROOT}/docs/decisions-format.md` § Current only. When
  `project-log` creates the `DECISIONS.md`, it adds the `ADRs:` line for an ADR
  folder.
- **A question the register records as answered is not an open item.** The
  decision that answered it is the entry; the question is not proposed.
- **Do not edit the source documents.** Keeping a status index in two places
  means they drift, and stripping the duplicate from the source is usually the
  right follow-up -- but it is the user's call and it is outside this skill.
  Say it once, as a recommendation, and touch nothing.

### Step 4b: name the sources

Ask for them **one category at a time**, in this order, because each answer
changes what is worth asking for next:

1. Repositories, READMEs and design or decision documents.
2. Wiki pages -- Confluence, Notion, an internal handbook.
3. Chat -- a Slack channel, specific threads, an email chain.

For each source, fetch what the session's connectors can actually reach.

**A source this session cannot reach is one notice line, then continue.** Never
hard-stop, and never make any part of this skill conditional on a connector:

```
No Slack connector in this session, so I cannot read #harbor-rollout. Paste the
messages you want covered, or skip it and we carry on with the rest.
```

Sources also become **Context links** in `open.md`, which are ledger content and
therefore go through `project-log` like everything else. A source the user
pasted rather than linked has no URL and is not a context link.

### Step 4c: propose in tranches, through `project-log`

A seed run has more material than an ordinary log run, and that changes how the
proposal is shaped -- it does not change who approves it. **Seeding adds no
second approval gate.** `project-log`'s contract is the gate, per
`${CLAUDE_PLUGIN_ROOT}/docs/project-log-reference.md` § A batch handed over by
another skill: it shows the exact lines grouped by file, scaffolds a missing
file inside the same approval, extends an existing `DECISIONS.md` and never
overwrites it, and accepts partial approval.

What seeding adds is a bound on how much is shown at once: forty-one entries
in one message make "just the first two" unusable.

- **One tranche at a time, in this order** -- decisions, then open items, then
  context links. Hand each to `project-log`, which proposes it and waits.
- **Name the repository for each decision** in a multi-repository project: the
  one whose code it constrains, or home for a project-wide one. Where the
  material does not say, `project-log` asks.
- **Restate any outstanding proposal before opening a new one.** If the previous
  tranche was not answered, or was answered about something else, say what is
  still unwritten before showing anything further. Silence is not approval, and
  neither is the user replying about something else.
- **Split a long tranche by source**, not by count. "The four decision records"
  and "the decision from the rollout channel" are two proposals a person can
  hold in their head. "Entries 1 to 15 of 34" is not.
- **Nothing carries forward.** An approval of one tranche approves that tranche.

The classification rules, the keep rule, the attribution rules and the
duplicate check are all `project-log`'s and are not restated here. Three things
are worth saying because a seed run hits them and a normal log run does not:

- **Date each open item with the date it was actually raised**, not with today,
  per `project-log-reference.md` § Backfilling an existing project. An item
  whose date cannot be established is asked about; an approximation is taken
  and normalized there; an item the user cannot date even roughly is left out,
  and the report names it. No part of this skill licenses inventing a date.
  Decisions carry no date.
- **A decision needs its why and its revisit condition.** Where the source does
  not give them, they are questions in the proposal, never filled in.
- **Anything implied but not stated goes in the proposal as a question**, not as
  an entry. A design document describing a preference is not a decision, and a
  register's open question is an open item rather than a decision about it.

**Say what a backfill does to the audit before the user runs it.** Open items
dated to their true origin are older than `stale_after_days` the moment they
land, so `project-gaps` reports them immediately. That is correct and it still
surprises people:

```
These are dated when they were raised, so anything older than 30 days will show
up as stale in /daikenja:project-gaps straight away. That is the audit working,
not a fault in the entries.
```

## Step 5: confirm

Two or three lines: what was written, where, and what was deliberately left
alone, per `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- the result
leads, and seeded entries are counted, not listed one by one. Say the ledger
files are not committed: `project-log` never commits, and the user commits
them with the work they belong to.

```
Registered this project as `harbor` at C:/GitHub/harbor, with
stale_after_days: 30. Wrote the project card at
C:/GitHub/harbor/.daikenja/project.md. Seeded 4 decisions into DECISIONS.md
and 6 open items into .daikenja/open.md through project-log -- not committed.
Left norms_doc unset, so it uses the default.
```

If seeding was declined or produced nothing, say that plainly and name
`/daikenja:project-log` as the way to add entries later.

## Re-running this skill

Safe at any time, and expected. An exact path match leaves the entry and its
key untouched, Step 3 shows what is already set before asking, and seeding a
project that already has a ledger proposes only what `project-log`'s duplicate
check finds missing. Running it purely to seed is a normal use.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself -- same rule every Daikenja skill follows.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | **Stop.** Name `/daikenja:setup-user`. Never create the file here. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| `profile.name` unset or empty | **Stop.** The configuration is incomplete. Point at `/daikenja:setup-user`. |
| An exact path match already exists | Say which key, leave it alone, and carry on to Steps 3 and 4. Registration is idempotent. |
| The matched or named project needs migration | Step 2a. Declined: nothing written, and the old ledger stays where it was. |
| A migration step fails after the approval | Stop there and say which steps ran. The old ledger is removed last, so the run can be repeated. |
| An entry carries both `path` and `paths` | Read it as the union of the two and say so, naming the key. Offer to fold it into one `paths` list on approval, keeping the first path first; never rewrite it silently. |
| The user names an existing project to add this directory to, and the key does not exist | Ask again, listing the registered keys. Never create a new entry under a key the user only half-remembered. |
| Not a git repository, or no directory at all | Offer `git init` in it, or in a new folder. A no writes nothing; never an entry with no paths. |
| A project card already exists at `<home>/.daikenja/project.md` | Say so and leave it alone. Never inspect or rewrite it -- the user edits the card by hand. |
| `<home>/.daikenja/` does not exist yet | Create the directory as part of the approved card write. `open.md` is still `project-log`'s to scaffold; a `.daikenja/` holding only a card is a normal state. |
| The current directory is inside an already-registered project | Say which project it resolves to and ask before adding a second entry. Never assume a nested registration is wanted. |
| The current directory is the user's home directory or `~/.claude` | **Stop.** Neither is a project. Say so and write nothing. |
| `daikenja.yaml` is not writable | **Stop.** Name the path and the error. Do not write the entry anywhere else. |
| A named source is unreachable, empty, or fails halfway | One notice naming it, then continue with the rest. Never stop, and never guess at content you could not read. |
| The project already keeps its own decision records | Not a failure. Say what was found, offer the index-and-depth shape from Step 4a, and let the user decide whether Daikenja adds anything here. |
| A seed open item has no recoverable date | Ask. If the user cannot supply one, drop that item and name it in the report. Never date it today and never invent one. |
| A tranche goes unanswered | Restate what is still unwritten before proposing anything further. Silence is not approval. |
| `project-log` refuses or stops -- a newer format version, a missing `open.md` section, a line that does not parse | Its failure cases govern. Hand the material over and let it stop; do not repair a ledger file from here. |

## What this skill does not do

- It does not capture profile data, copy `personas.md` or `writing-style.md`, or
  create anything in Google Drive. That is `/daikenja:setup-user`, and it stays
  there.
- It does not write ledger content or commit anything. `/daikenja:project-log`
  writes `DECISIONS.md` and `open.md`, on its own approval, and it is the only
  skill that does; the user commits them.
- It does not edit an existing project card or write `last_checkpoint`.
- It does not edit the project's own documents -- a decision record, a wiki page
  or a README that a seed run read stays exactly as it was found.
- It does not migrate a project on its own initiative: Step 2a runs for the
  project matched or named, after `setup-user` reports it, and only on approval.
