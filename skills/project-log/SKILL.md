---
name: project-log
description: Records decisions, open items and sources in a project's ledger. Use when the user says "log this", "record this decision", "add this to the ledger", or asks for what was settled to be written down.
metadata:
  owner: Carlos
  version: 1
  writes: DECISIONS.md at a registered repository's root, and .daikenja/open.md in the project's home repository
---

# Log

The ledger is the project's memory: `DECISIONS.md`, the decisions still in
force, at the root of each registered repository, and `.daikenja/open.md`, what
is still unsettled, in the home repository. Git is the history. This skill is
the only thing that writes either file.

## Hard rules

**Never write lines the user has not stated or approved.** For interpreted
material -- threads, pastes, transcripts, anything this skill classifies --
show the exact lines first, as one batch, wait for the user to say yes, then
write. "Yes" means the user said so in this conversation, and an approval of
one batch does not carry to the next one. For a fact the user dictated (Step
5's same-turn path), the dictation is the approval, given in advance -- and it
stays valid only while the written lines add nothing the user did not say.

**Never invent an entry.** Everything written comes from the material the user
gave you. If something is implied but not said, put it in the proposal as a
question, not as an entry.

**Never repair a broken file on your own initiative.** Report the problem,
name the line, and stop. Repair is a separate write and needs its own approval.

**Never commit.** This skill changes the files in the working tree and stops
there. The user commits them with the work they belong to; `project-catchup`
lists them as not committed yet until then.

**Never write either file from any other skill.** Another skill that needs an
entry -- `meeting-review`, `setup-project`'s seed, the migration in
`docs/ledger-migration.md` -- hands its entries to this one, and they go
through Step 2 to Step 8 like any other batch: the refusals, the repository
question and the duplicate check apply to them too. That is a
`project-log via <skill>` run.

## Step 0: read the contracts

Read these before writing anything. They are binding, and they are the only
place their detail lives. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/decisions-format.md` -- the `DECISIONS.md` format:
  what gets kept, areas and `Paths:`, the entry shape, current-only.
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` -- the `open.md` grammar, the
  `Blocked by:` prefix, closing an item, and the version rule for both files.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- where the config lives,
  how a project and its files are resolved, and the legacy keys.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-versioning.md` -- the version-marker notice
  this skill emits and never migrates.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply is shaped.
  Proposed lines stay in file grammar; the talk around them follows this.

Two more, read only when the run needs them:

- `${CLAUDE_PLUGIN_ROOT}/docs/config-drive.md`, for a `drive:` pointer. Step 5's
  owner check is the only thing here that reads `personas.md`.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-log-reference.md`, this skill's
  branch-only sections. Every rule there binds exactly as if it sat here, and
  each step below names its section at the moment that branch opens.

If they ever disagree with this skill, the contract wins and you say so.

## Step 1: get the material

- **A link was given.** Fetch it with whatever tool is connected. Get the whole
  thread, not the preview.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **A plain description was given** ("log that we picked Postgres"). That is
  enough material.
- **Nothing was given.** Ask what to log. Do not search for it, and do not read
  the repository to guess what happened.
- **Entries handed over by another skill.** Use them as that skill classified
  them. They were classified, not dictated.

If a fetch fails, say what failed in one line and ask for a paste. Never guess
at the content of something you could not read.

## Step 2: resolve the config, the project and the files

Follow `config-resolution.md` § Resolution order exactly. In short:

1. Read `~/.claude/daikenja/daikenja.yaml`. Absent is not fatal -- this skill
   works on defaults. Malformed YAML **is** fatal: report the first line that
   does not parse and stop.
2. **A project key was named.** Match it per `config-resolution.md` § By key.
   No match: say so, list the registered keys, stop. A match: refuse in one
   line, naming the key and saying that logging against it means running from
   one of its own directories. Never fall back to directory matching -- a
   named key is decisive. **No key was named:** match the current directory
   against every path of every entry, longest prefix wins.
3. Resolve the files per `config-resolution.md` § Finding `DECISIONS.md` and
   `open.md`: `DECISIONS.md` at the root of every path in the entry, and
   `.daikenja/open.md` in the home repository, which is the **first** path.
   No match: the current directory is the one root.
4. Apply `config-resolution.md` § Legacy keys and unmigrated ledgers. A
   leftover `ledger:` key gets its one line and the run continues. A
   `paths: []` entry is "needs migration": its line, and stop. **An old ledger
   at `<home>/.daikenja/ledger.md` with no `open.md` beside it** is refused --
   whether or not a `DECISIONS.md` exists. Write that line, write nothing, and
   scaffold nothing -- unless the batch is the migration's own, per
   `project-log-reference.md` § A batch handed over by another skill:

   ```
   The ledger at <home>/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
   ```

5. Emit the version-marker notice if it applies, per `config-versioning.md`.
   It never blocks a write, and this skill never migrates anything.

**A file on disk wins over the config.** If `DECISIONS.md` or
`.daikenja/open.md` exists under the current directory but no project matches,
use it. Then say so in one line and name the skill that registers it -- you do
not write `daikenja.yaml` yourself:

```
This project is not in daikenja.yaml. The ledger still works. To register it,
run /daikenja:setup-project -- it adds the entry for this directory.
```

## Step 3: scaffold the ledger when it is missing

**Only for a file the batch writes to that does not exist yet.** Read
`project-log-reference.md` § Step 3: scaffold the ledger when it is missing and
follow it -- it owns the refusals, the is-this-a-project check, the copy from
the template, and how the scaffold folds into the Step 5 approval.

**A `DECISIONS.md` that exists is adopted, whoever wrote it** -- another
plugin, a person, an earlier run. New entries go into it. It is never
overwritten, re-scaffolded or reformatted.

## Step 4: read what is already there

Read every file the batch could touch before proposing anything.

**The version lines first**, per `open-format.md` § Version line. **A newer
version than this plugin knows, in any file the batch would write, refuses the
whole batch** -- nothing is written to any file, not even the entries for the
others.
Name the file and the version, ask for a plugin update, and stop:

```
<file> was written by a newer format (version <n>); update the Daikenja plugin
before logging. Nothing was written. The version rule is in
${CLAUDE_PLUGIN_ROOT}/docs/open-format.md.
```

A file with no version line is read as version 1, and the proposal adds the
line.

**The sections.** In `open.md`, locate each of the three H2 headings by exact
name; a missing one stops the run per `project-log-reference.md` § Failure
cases. In each `DECISIONS.md`, read the areas and their `Paths:` lines.

**The existing entries.** You are checking whether what the user is logging is
already recorded. Compare by meaning, not by wording. Nothing carries an ID: a
decision is found by its area and its words, an open item by its words.

## Step 5: build the proposal

### The same-turn path for dictated facts

When the material is a fact the user dictated, skip the proposal: write
immediately, then show the exact written lines verbatim, under the file they
went to. The dictation is the approval of that batch. A correction afterwards
("change the owner to @sam") is an ordinary edit, and the uncommitted change is
there in the diff for the user to see.

A run takes this path only when **all four** of these hold. Fail any one and
the run follows propose-then-wait below.

1. **The material is the user's own statement, typed as the request itself.**
   A link, a paste or a transcript never qualifies, even when the user wrote
   parts of it.
2. **The user's phrasing settles the classification.** The user names the kind
   ("log the decision that...", "add an open item...") or the statement
   classifies without judgement.
3. **Every field resolves without a question.** For an open item: the date is
   today or an exact date the user gave, the owner is who the user named, the
   user for their own call, else `@unassigned`. For a decision: the rule, the
   why and the revisit condition are all in the user's words, and the
   repository and area follow without judgement (below). **An approximate date
   drops the run.** So does a decision with no stated why or revisit
   condition -- asking for it is a question.
4. **The operation is byte-determined.** New entries, and changes the user
   names exactly ("close the item about the alert thresholds"). The duplicate
   check still runs first: a hit the user did not name drops the run. At most
   about three entries -- more is a batch to propose. A `Blocked by:` prefix
   counts only when the user stated the block and named an item that is in the
   file.

Scaffolding a missing file, repairs, and every `project-log via <skill>` run
never take this path.

### Classify before you write

Getting this wrong pollutes the ledger, and the ledger is what every other skill
reads.

- A **decision** is something settled: someone with standing said it, or the
  group converged and nobody objected. It goes to a `DECISIONS.md`.
- An **open item** is a named thing that is not settled: a question, a task
  with no owner or no answer, a dependency. It goes to `open.md`.
- A **suggestion nobody agreed to is neither.** Leave it out, or raise it as an
  open item if it is a real unanswered question. A question or a proposal is
  not a decision.
- A **document to track is a source**; a useful address is a **context link**.
  Both go to `open.md`. When the material does not say which, ask. Read
  `project-log-reference.md` § Record a source when the run records one.

**Apply the keep rule to every decision drawn from interpreted material**, per
`decisions-format.md` § What gets kept. One that meets none of its three tests
goes in the proposal under "Not kept", with the reason, and is written only if
the user asks for it. A decision the user dictated was kept by the user.

Two branches open here, each in `project-log-reference.md`:

- **A decision made outside this group that binds it** -- a published standard,
  a policy, a contract term. Read § Mark a decision that was imposed.
- **The material states that one open item blocks another.** Read § Record a
  relationship only where the source says so.

When you cannot tell, ask -- but never serially. Collect every clarifying
question the run needs and ask them all in one round, one line each, in the
proposal's "Questions before I write" block. A question the user answered, or
that the material or config already answers, is never asked again in the run.
One follow-up is allowed only when the user's own answer created a new
ambiguity, and it names that answer as the cause. Do not resolve an ambiguity
yourself and do not log both readings.

### Place each decision

**Which repository.** A single-repository project has one `DECISIONS.md`. In a
multi-repository project, a decision goes to the repository whose code it
constrains, and a project-wide one -- scope, commitments, people -- to the
home repository. When the decision's paths do not say which, ask which
repository's `DECISIONS.md` it belongs in. Never guess and never write it to
two.

**Which area.** Use the area whose `Paths:` covers what the decision
constrains. When none does, propose a new area with its heading and `Paths:`
line, per `decisions-format.md` § Shape. When two could, ask.

**The entry** is the shared shape, with its em dash: `**<rule now in force>** —
<why>. Revisit: <condition, or "never">. Source: <link, issue, pull request or
thread>.` State the rule, not its history. A why or revisit condition the
material does not give is a question, never filled in. `Source:` names the
link, issue or thread the material came from, and is left out when it has
none -- never invented.

### Attribute correctly

Only open items carry an owner. `DECISIONS.md` entries have none. The owner is
`@` plus one token, no spaces, lowercase.

- A person named in the material owns the item (`@priya`).
- The user owns what the user says is theirs: the first token of
  `profile.name` from the config.
- Nobody identifiable means `@unassigned`. Write it out; never leave the field
  empty. An unowned item is what `project-gaps` reports.

Never merge two people's positions into one entry.

### Say when a handle is new

A handle is free text, so one colleague can pick up several spellings. This
check surfaces the second spelling as it arrives, when fixing it costs one word.
It is a **notice, not a gate**.

Run it after the duplicate check, over every owner the batch writes: a new
item's, and an owner changed by an edit. Skip `@unassigned`. It does not audit
what is already in the file.

1. **Look in `open.md` first.** A handle that already owns an item there is
   known. Say nothing. This is the common case, and why `personas.md` is
   usually never read.
2. **Otherwise resolve `profile.personas`**, per `config-resolution.md`
   § Resolving `writing_style` and `personas`. The handle is known if it names
   a persona section or appears in one's `Known as` field. Match generously.
3. **In neither, report it** in the proposal, one line per handle, and **name
   the near miss** when a known handle plausibly means the same person:

```
New owner handles:
- @priya.nair -- not in open.md and not in personas.md. open.md already uses
  @priya. Same person?
```

"Same person?" invites a correction; the run never waits on it, so it never
fails the same-turn conditions and never goes in "Questions before I write".
On the same-turn path it is shown beside the written lines. It runs **before**
the write either way. Never rewrite a handle, never merge entries because they
look like one person, and never write `personas.md` -- offering
`/daikenja:remember-persona` is fine. With no personas file configured, say the
comparison was `open.md` alone.

### Check for duplicates first

For each candidate, look for an entry that already records the same fact.

**Same subject is not the same fact.** A standing rule and one project's call
stay separate entries even when they read alike. The test is what would have
to change for the entry to stop being true: if the answers differ, they are two
facts.

- **The same fact, already there.** Propose an edit to that entry, quoting it.
  Do not append a near copy.
- **A decision that replaces one in force.** Propose editing the old entry in
  place, or deleting it and adding the new one. `DECISIONS.md` is current-only:
  nothing is marked superseded.
- **A decision that conflicts with one in force without clearly replacing it.**
  Ask which one holds. The answer is written; the conflict never is.
- **An open item the material settles.** Propose deleting its line, and the
  `DECISIONS.md` entry when it was settled by a decision, in the same batch.
  When another item's `Blocked by:` names it, offer to drop that prefix too.
- **Genuinely new.** Propose a new entry.

Two more branches open here, each in `project-log-reference.md`, and both set
the date on the open items this run writes:

- **Most items are older than the run** -- recording a project that has
  history. Read § Backfilling an existing project.
- **The run is `project-log via meeting-review`.** Read § A meeting date handed
  over by `meeting-review`.

### Show the proposal

Show exactly what will be written, verbatim, grouped by file, in one fenced
block. Every line the user approves lands in the file byte for byte.

```
C:/GitHub/atlas/DECISIONS.md
  ## Delivery  (new area)
  Paths: `pipelines/`
  + - **The reload runs as a pipeline, never as a manual script.** — a manual
      run skipped the row-count check twice. Revisit: never. Source:
      https://example.com/atlas/thread/88

C:/GitHub/atlas/.daikenja/open.md  (creating it from the template)
  Open items
  + - 2026-08-14 -- @carlos -- Confirm the reload window with the data team.
  - - 2026-08-09 -- @carlos -- Decide whether the reload is scripted or a pipeline.

Not kept:
- <decision> -- <which keep test it fails>

New owner handles:
- <handle> -- not in open.md and not in personas.md. <near miss, if any>

Questions before I write:
- <anything you could not settle, one line each>
```

`+` marks a line added, `-` a line deleted, and an edit shows both. Drop any
block that is empty rather than writing a heading with nothing under it. Get
today's date from the environment -- `date +%Y-%m-%d`, the **local** date --
never from memory.

Keep the proposal to what the material supports. Five clean entries beat twelve
padded ones.

## Step 6: wait

Stop and wait for the user.

- **Approved.** Write it.
- **Partly approved** ("just the first two"). Write only what was approved. Do
  not argue for the rest.
- **Edited** ("change the owner to @sam"). Show the corrected block and wait
  again. It re-opens no settled question.
- **Rejected.** Write nothing. Say nothing was written.

Silence is not approval. Neither is the user replying about something else.

## Step 7: write

- **A new open item, context link or source** goes directly under its heading.
- **Closing an item** deletes its line and its continuation lines.
- **A new decision** goes at the end of its area, or a new area at the end of
  the file, unless the user placed it.
- **An edit** changes the line in place. Nothing moves.
- **A missing version line** is added as the file's first line, as the
  proposal showed.

Touch nothing else. Do not reorder, reformat or tidy either file, and do not
normalize a line a human wrote by hand.

## Step 8: confirm

Confirm in one or two lines: what was written, to which files, topic first.
Then say the change is not committed:

```
Wrote 2 entries -- the reload decision to C:/GitHub/atlas/DECISIONS.md, and
the reload-window item to .daikenja/open.md. Not committed: commit them with
the work they belong to.
```

When a written entry names another document in the project, offer the
follow-up: "The reload decision points at docs/reload.md -- update it to
match?" Updating it is outside this skill's write scope, so it happens only on
the user's yes, as its own change.

## Failure cases

`project-log-reference.md` § Failure cases. Read it the moment a run meets a
situation the steps above do not settle, and before improvising a way through
one.

## What this skill does not do

`project-log-reference.md` § What this skill does not do. Read it when a run is
about to do something no step above told it to.
