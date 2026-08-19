---
name: setup-project
description: Registers the project you are in with Daikenja, sets its per-project settings, and optionally seeds its ledger from sources the project already has. Use when the user says "register this project", "add this repo to Daikenja", "set this project up", or "seed the ledger from our Confluence space". Run explicitly with /daikenja:setup-project -- it never fires on its own. Personal setup stays in /daikenja:setup-user and is not repeated here. Seeding writes nothing itself -- proposed entries go to /daikenja:project-log, which shows the exact lines and waits for approval.
metadata:
  owner: Carlos
  version: 1
  writes: ~/.claude/daikenja/daikenja.yaml -- the projects entry for the current directory only
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

**This skill never writes ledger content.** Seeding derives candidate entries
and hands them to `/daikenja:project-log`, which shows the exact lines and waits
for approval. `project-log` remains the only writer of a ledger, per
`docs/config-contract.md` § Who writes what.

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

This skill never captures profile data. If the user offers a name, role or tone
here, record nothing and point at `/daikenja:setup-user`.

There is no environment gate in this skill. `setup-user` ran Step 0 already, and
its config file could not exist otherwise.

## Step 1: read what already exists

Before proposing anything:

- The current directory's **normalized path** -- forward slashes, no trailing
  slash, compared case-insensitively, per `docs/config-contract.md` § Finding
  the current project.
- Every `projects:` entry's `path`, normalized the same way, and whether any is
  an **exact match** for this directory.
- Whether a ledger already exists on disk at the resolved path -- the matched
  project's `ledger:` key, otherwise `.daikenja/ledger.md` under the project
  root. This decides whether Step 4 is a first seed or a top-up, and it is
  read-only here.

**A ledger on disk with no matching `projects:` entry is a normal state**, not
an error. The file on disk is the fact and the config is the index. Register the
project and leave the ledger exactly as it is.

## Step 2: register the project

- **An exact path match already exists.** Say which key it is registered under
  and leave the entry alone. Registration is idempotent, and it is not a place
  to silently change a key someone chose. Go to Step 3 -- an already-registered
  project can still want its keys set or its ledger seeded.

- **No match.** Propose a new entry, key defaulting to the directory's own name,
  and ask if the user wants a different label. The key is a human label and is
  never matched on, so it may be anything that reads well:

  ```yaml
  <dir-name>:
    path: <normalized absolute path>
  ```

**A prefix match that is not exact is a nested project.** The current directory
sits inside a registered one. Say which project it resolves to today and ask
before registering a second entry -- resolution takes the longest matching
prefix, so a new inner entry silently takes over every skill run in this
subtree. That is sometimes exactly what the user wants and is never something
to assume.

Add the entry with the Edit tool, under `projects:`. **Never rewrite the file.**
Hand-added keys, other projects and the template's comments all survive an edit
and none of them survive a regeneration.

## Step 3: offer the per-project keys

`setup-user` left these unset because it had no idea what the project was. This
skill does, so it offers them once rather than leaving them to be discovered.
Ask in one short round, and take silence as "leave them all unset":

```
Registered. Three optional settings for this project -- skip any or all:

1. ledger -- where the ledger file lives, relative to the project root.
   Default .daikenja/ledger.md.
2. stale_after_days -- how long an open item may sit before project-gaps calls
   it stale. Inherits <the profile value> if you skip it.
3. norms_doc -- your team's ways-of-working document, as a path or a URL.
   Setting it turns on self-review's ROLE CHECK, which is off by default.
```

Every one of these is optional and every one has a defined default in
`docs/config-contract.md` § Field notes. **Write only the keys the user
answers.** A key written at its own default value is noise that reads like a
deliberate override to the next person who opens the file.

**Never write `last_checkpoint` here.** It belongs to `project-catchup`, which
sets it after it has actually reported a delta. Writing it at registration would
claim a report that never happened, and the first `project-catchup` run would
then skip everything older than the moment of registration.

State the values you are about to write and wait for a yes, then edit them into
the entry from Step 2.

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
architecture decision records, RFCs, a decision log or a numbered question
register, and finding that out on the fifth exchange means several rounds of
entries have already been proposed against a source that turns out to be
superseded.

Look for the usual homes -- `docs/adr/`, `docs/decisions/`, `docs/rfc/`,
`adr/`, `decisions/`, or a file whose name says the same thing. This is a scan
of file names in the project, not a read of the repository for material.
`project-log`'s rule against reading the repository to guess what happened is
about inventing material for an ordinary log entry; here the user has asked for
exactly this and the results are shown before anything is proposed.

**When the project already keeps one, the ledger is the index and those
documents are the depth.** Say so plainly, because the honest first read of such
a project is "you may not need Daikenja here":

```
This project already keeps 11 decision records in docs/adr/ and a numbered
question register. Daikenja does not replace those. What it adds is one place
that answers "what is settled, what is open, who owns it" across all of them.
Each entry would be one line pointing at the record that holds the detail.
```

Three rules follow, and all three have to be settled before the first write:

- **Entry bodies are one line pointing at the source.** No narrative, no
  history, no summary of the record's reasoning. That is the same rule
  `project-log` already applies to every entry body -- nothing about the format
  changes to support this.
- **Carry the source identifier across.** People cite `ADR-0007` and `Q-04` in
  chat and in standups, and a migration that drops those references breaks every
  one of them. Propose entries in ascending source-identifier order so that
  `project-log`'s sequential allocation lands `ADR-0007` on `D-007` where the
  source numbering allows it. Where it cannot -- gaps in the source sequence,
  two sources feeding one section, or a ledger that already holds entries --
  the body opens with the source identifier instead. **Decide which before the
  first write.** A written entry is never renumbered, so this cannot be
  corrected afterwards.
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

Sources also become **Context links**, which are ledger content and therefore go
through `project-log` like everything else. A source the user pasted rather than
linked has no URL and is not a context link.

### Step 4c: propose in tranches, through `project-log`

A seed run has more material than an ordinary log run, and that changes how the
proposal is shaped -- it does not change who approves it. **Seeding adds no
second approval gate.** `project-log`'s contract is the gate: it shows the exact
lines, waits, and accepts partial approval.

What seeding adds is a bound on how much is put in front of the user at once.
Forty-one entries in one message makes "just the first two" unusable, and a
tranche the user answers around is a tranche nobody approved.

- **One tranche at a time, in this order** -- decisions, then open items, then
  context links. Hand each to `project-log`, which proposes it and waits.
- **Restate any outstanding proposal before opening a new one.** If the previous
  tranche was not answered, or was answered about something else, say what is
  still unwritten before showing anything further. Silence is not approval, and
  neither is the user replying about something else.
- **Split a long tranche by source**, not by count. "The eleven decision records"
  and "the four decisions from the rollout channel" are two proposals a person
  can hold in their head. "Entries 1 to 15 of 34" is not.
- **Nothing carries forward.** An approval of one tranche approves that tranche.

The classification rules, the attribution rules, the duplicate check and the
insert rule are all `project-log`'s and are not restated here. Four things are
worth saying because a seed run hits them and a normal log run does not:

- **Date each entry with the date it was actually decided or raised**, not with
  today. That is what the date field means, and a backfill is the one situation
  where the two differ for every entry.
- **An entry whose date cannot be established is not proposed.** Ask the user
  for it. If they cannot supply one either, leave the entry out and say which
  ones were dropped and why. The date field is required and absolute, and no
  part of this skill licenses inventing one.
- **Anything implied but not stated goes in the proposal as a question**, not as
  an entry. A design document describing a preference is not a decision, and a
  register's open question is an open item rather than a decision about it. A
  question the register records as **answered** is a resolved open item naming
  the decision that answered it, not a decision in its own right.
- **A partial approval can break a supersession pair.** Approving a decision
  that supersedes another while dropping the one it supersedes leaves a body
  claiming `Supersedes` with nothing to point at, and the ledger's rule is that
  the marking lives on both entries. Say so before the write and let the user
  choose -- keep both, or write the surviving decision without the `Supersedes`
  clause. Never write half a pair and never repair it afterwards.

**Say what a backfill does to the audit before the user runs it.** Entries dated
to their true origin are older than `stale_after_days` the moment they land, so
`project-gaps` reports them immediately. That is correct and it still surprises
people:

```
These are dated when they were raised, so anything older than 21 days will show
up as stale in /daikenja:project-gaps straight away. That is the audit working,
not a fault in the entries.
```

## Step 5: confirm

Two or three lines: what was written, where, and what was deliberately left
alone, per `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- the result
leads, and seeded entries are counted as ranges, not listed one by one.

```
Registered this project as `harbor` at C:/GitHub/harbor, with
stale_after_days: 30. Seeded 11 decisions and 6 open items through
project-log -- D-001 to D-011, O-001 to O-006. Left `ledger` and `norms_doc`
unset, so they use the defaults.
```

If seeding was declined or produced nothing, say that plainly and name
`/daikenja:project-log` as the way to add entries later.

## Re-running this skill

Safe at any time, and expected. An exact path match leaves the entry and its key
untouched, Step 3 shows what is already set before asking, and seeding a project
that already has a ledger proposes only what is not already recorded --
`project-log`'s duplicate check is what enforces that, and an entry it matches
comes back as a proposed edit rather than a near copy.

Running it purely to seed an already-registered project is a normal use, not a
workaround.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself -- same rule every Daikenja skill follows.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | **Stop.** Name `/daikenja:setup-user`. Never create the file here. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| `profile.name` unset or empty | **Stop.** The configuration is incomplete. Point at `/daikenja:setup-user`. |
| An exact path match already exists | Say which key, leave it alone, and carry on to Steps 3 and 4. Registration is idempotent. |
| The current directory is inside an already-registered project | Say which project it resolves to and ask before adding a second entry. Never assume a nested registration is wanted. |
| The current directory is the user's home directory or `~/.claude` | **Stop.** Neither is a project. Say so and write nothing. |
| `daikenja.yaml` is not writable | **Stop.** Name the path and the error. Do not write the entry anywhere else. |
| A named source is unreachable this session | One notice naming the source and what is missing, then continue with the rest. Never stop, and never make the skill conditional on a connector. |
| A source is reachable but empty, or the fetch fails halfway | One notice, then continue. Never guess at the content of something you could not read. |
| The project already keeps its own decision records | Not a failure. Say what was found, offer the index-and-depth shape from Step 4a, and let the user decide whether Daikenja adds anything here. |
| A seed entry has no recoverable date | Ask. If the user cannot supply one, drop that entry and name it in the report. Never date it today and never invent one. |
| A tranche goes unanswered | Restate what is still unwritten before proposing anything further. Silence is not approval. |
| The ledger is missing a required H2 section, or a line does not parse | `project-log`'s failure table governs. Hand the material over and let it stop; do not repair a ledger from here. |

## What this skill does not do

- It does not capture profile data, copy `personas.md` or `writing-style.md`, or
  create anything in Google Drive. That is `/daikenja:setup-user`, and it stays
  there.
- It does not write ledger content. `/daikenja:project-log` does, on its own
  approval, and it is the only skill that does.
- It does not write `last_checkpoint`. That is `/daikenja:project-catchup`.
- It does not edit the project's own documents -- a decision record, a wiki page
  or a README that a seed run read stays exactly as it was found.
- It does not migrate or convert anything from a previous Daikenja layout.
