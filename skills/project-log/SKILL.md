---
name: project-log
description: Records decisions, open items and sources in a project's Daikenja ledger. Use when the user says "log this", "record this decision", "add this to the ledger", "capture the open items", "note that we agreed X", "track this page as a source", or pastes a thread or a plain description and asks for what was settled to be written down -- not a raw meeting transcript (meeting-review classifies those in two passes before handing to this skill), and not a check for whether tracked sources moved. Also use when a project has no ledger yet and one is asked for. This is the only skill that writes ledger content -- every other Daikenja skill reads it. A short fact the user dictates is written in the same turn and shown verbatim; everything else is proposed first and written only on approval. Accepts a project key only when that project has no paths -- `/daikenja:project-log <key>` logs against it from anywhere; a key naming a project that has paths is refused.
metadata:
  owner: Carlos
  version: 1
  writes: the project's ledger, wherever `ledger:` resolves to (default <project>/.daikenja/ledger.md)
---

# Log

The ledger is the project's memory. This skill is the only thing that writes it.

## Hard rules

**Never write lines the user has not stated or approved.** For interpreted
material -- threads, pastes, transcripts, anything this skill classifies --
show the exact lines first, wait for the user to say yes, then write. "Yes"
means the user said so in this conversation, and an approval of one proposal
does not carry to the next one. For a fact the user dictated (Step 5's
same-turn path), the dictation is the approval, given in advance -- and it
stays valid only while the written lines add nothing the user did not say.

**Never invent an entry.** Everything written comes from the material the user
gave you. If something is implied but not said, put it in the proposal as a
question, not as an entry.

**Never repair a broken ledger on your own initiative.** Report the problem,
name the line, and stop. Repair is a separate write and needs its own approval.

**Never write the ledger from any other skill.** Another skill that needs an
entry runs this one. The Changelog then records the writer as
`project-log via <skill>`.

## Step 0: read the contracts

Read these before writing anything. They are binding, and they are the
only place their detail lives. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- section names, entry grammar,
  IDs, tails, body markers, Changelog, and the reading rules.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- where the config lives, how
  a project and its ledger are resolved, and what to do when config is missing.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-versioning.md` -- the version-marker notice
  this skill emits and never migrates.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Proposed ledger lines stay in file grammar; the talk around them
  follows this.

Two more, read only when the run actually needs them:

- `${CLAUDE_PLUGIN_ROOT}/docs/config-drive.md`, for the download mechanics
  behind a `drive:` pointer. Step 5's owner check is the only thing here that
  reads `personas.md`, and it reads it only when a run carries a handle this
  ledger does not already know.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-log-reference.md`, which holds this
  skill's own branch-only sections -- scaffolding a missing ledger, an imposed
  decision, a relationship marker, a source, a backfill, a meeting date handed
  over by `meeting-review`, the failure cases, and what this skill does not do.
  Every rule there binds exactly as if it sat here, and each step below names
  its section at the moment that branch opens.

If they ever disagree with this skill, the contract wins and you say so.

## Step 1: get the material

- **A link was given.** Fetch it with whatever tool is connected (Slack, email,
  a web fetch, an MCP server). Get the whole thread, not the preview.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **A plain description was given** ("log that we picked Postgres"). That is
  enough material. Use it.
- **Nothing was given.** Ask what to log. Do not search for it, and do not go
  reading the repository to guess what happened.
- **Material handed over by another skill** (a `project-log via <skill>` run).
  Use what that skill classified. It was already classified, not dictated.

If a fetch fails, say what failed in one line and ask for a paste. Never guess
at the content of something you could not read.

## Step 2: resolve the config, the project and the ledger

Follow `config-resolution.md` § Resolution order exactly. In short:

1. Read `~/.claude/daikenja/daikenja.yaml`. Absent is not fatal here -- this
   skill works on defaults. Malformed YAML **is** fatal: report the first line
   that does not parse and stop.
2. **A project key was named** ("log this against vendor-onboarding-programme",
   or `/daikenja:project-log <key> ...`). Compare it against every `projects:`
   key, case-insensitively, per `config-resolution.md` § Finding the project,
   by key.
   - **No match.** Say so, name the key, list the registered keys, and stop.
     Never fall back to directory matching -- writing against the wrong
     project is worse than no write.
   - **Matches an entry that has paths** (a `paths` list or a `path` scalar).
     Refuse -- a key alone does not say which of several roots the write
     belongs in, and that is still true here. Name the key in one line and say
     that logging against it means running from one of its own directories.
     Do not fall back to directory matching either: a named key is decisive,
     per `config-resolution.md` § Finding the project.
   - **Matches an entry with no paths.** Use it. This is the one case a key is
     unambiguous -- there is exactly one place the write can go -- and
     directory matching does not run.
   - **No key was named.** Match the current directory against **every path of
     every `projects:` entry** -- its `paths` list, or its `path` scalar read
     as a one-element list -- normalized and longest prefix wins across all of
     them. An entry with no paths is skipped; it is reachable only by key.
3. Resolve the ledger: the matched project's `ledger:` key if it has one --
   relative or absolute, per `config-resolution.md` § Resolving `ledger` -- and
   that resolved path is authoritative. Otherwise `.daikenja/ledger.md` under
   the project root. **The root is the first path in the entry**, not the path
   that matched -- a project spanning three repositories has one ledger, in the
   first of them. **A pathless entry has no root**, so only an absolute
   `ledger:` can resolve for it: a relative or absent `ledger:` on a pathless
   entry is a config error, not a missing default -- stop, name the key, and
   say it has no path and no absolute ledger, per `config-resolution.md` §
   Finding the ledger.
4. Check the version marker and emit the one-line notice if it applies, per
   `config-versioning.md` § Version marker and upgrades. It never blocks a write,
   and this skill never migrates anything -- `/daikenja:setup-user` does that.

**This skill resolves by directory, plus the one narrow key exception above.**
The read skills take a key freely because reading is location-free; writing is
not -- a key names a project, and a project may have several roots, so a key
alone does not say where a ledger entry belongs **unless it has none**. To log
against a rooted project you are not in, go to it first.

**A ledger on disk wins over the config.** If `.daikenja/ledger.md` exists but
no project matches, use it and carry on.

**When the project is unregistered**, say so in one line and name the skill that
registers it. You do not write `daikenja.yaml` yourself:

```
This project is not in daikenja.yaml. The ledger still works. To register it,
run /daikenja:setup-project -- it adds the entry for this directory.
```

Registration is optional. Never block a ledger write on it.

## Step 3: scaffold the ledger when it is missing

**Only when the ledger file does not exist at the resolved path.** Read
`project-log-reference.md` § Step 3: scaffold the ledger when it is missing and
follow it -- it owns the refusals, the is-this-a-project confirmation, the copy
from the template, and how the scaffold folds into the Step 5 approval. Where
the ledger is already there, this step does nothing; go to Step 4.

## Step 4: read what is already there

Read the whole ledger before proposing anything. You need three things from it.

**The sections.** Locate each by its exact H2 heading. If one of the original
four is missing, stop and use the failure table in
`project-log-reference.md` § Failure cases. `## Sources` is the
exception: a ledger without that heading tracks no sources and is complete as
it stands, per `ledger-format.md` § File skeleton -- the heading is added,
directly above `## Changelog`, as part of the approved write that records the
first source, never on its own.

**The existing entries.** You are checking whether what the user is logging is
already recorded. Compare by meaning, not by wording.

**The next IDs.** For each section, take the highest ID **ever used** and add
one. That is the higher of:

- the highest ID present in the section, and
- the highest ID for that section named anywhere in the Changelog.

The Changelog is what makes retirement stick. A deleted entry lowers the
section's maximum but never the Changelog's, and a retired ID is never reissued.

**Never renumber an entry that is already written**, and never allocate to make
the numbers line up with the dates. Allocate in the order the entries appear in
the proposal and let them fall where they fall: a backfilled entry dated last
year sitting on a higher ID than one written today is correct, per
`ledger-format.md` § IDs. Order in the file comes from the insert position in
Step 7, never from the number.

## Step 5: build the proposal

### The same-turn path for dictated facts

When the material is a fact the user dictated, skip the proposal: write
immediately, then show the exact written lines and the Changelog line
verbatim. The dictation is the approval. A correction afterwards ("change the
owner to @sam") is an ordinary edit with its own `~D-nnn` Changelog line, so
nothing is lost -- the Changelog records every write.

A run takes this path only when **all four** of these hold. Fail any one and
the run follows propose-then-wait below.

1. **The material is the user's own statement, typed as the request itself.**
   Of Step 1's four kinds, only "a plain description was given" qualifies. A
   link, a paste, or a transcript never does, even when the user wrote parts
   of that thread -- there this skill selects and interprets.
2. **The user's phrasing settles the classification.** The user names the kind
   ("log the decision that...", "add an open item...") or the statement
   classifies without judgement. If you have to weigh decision against open
   item, it is not dictated.
3. **Every field resolves without a question.** The date is today, or an exact
   date the user gave. The owner is who the user named, the user for their own
   call, else `@unassigned` -- a valid value, not a gap to ask about. The body
   is the user's statement fitted to the line grammar, not rephrased. The
   moment a clarifying question is genuinely needed, drop to
   propose-then-wait. **An approximate date drops the run too**: normalizing
   "some time in March" to a real date is a derivation the user approves, not
   one they are shown afterwards, per `ledger-format.md` § Approximate dates.
4. **The operation is byte-determined.** New entries, and operations the user
   names by ID ("mark O-003 resolved", "delete D-002"). The duplicate check
   below still runs first: a hit the user did not name themselves drops the
   run to propose-then-wait, because merging or superseding is
   interpretation. At most about three entries per dictation -- more is a
   batch and follows propose-then-wait. **A body marker follows the same
   line.** `Blocked by O-007.` written because the user said so, naming an ID
   that resolves in this ledger, is byte-determined; a marker you concluded
   from the material is interpretation and drops the run, as does one whose ID
   resolves to nothing.

Scaffolding a missing ledger, ledger repairs, and every run entered from
another skill (`project-log via <skill>`) never take this path. The Step 3
confirmation settles whether a ledger belongs there at all, which no dictation
can, and material handed over by a skill was classified, not dictated.

### Classify before you write

Getting this wrong pollutes the ledger, and the ledger is what every other skill
reads.

- A **decision** is something settled. Someone with standing said it, or the
  group converged and nobody objected.
- An **open item** is a named thing that is not settled: a question, a task with
  no owner or no answer, a dependency.
- A **suggestion nobody agreed to is neither.** It is discussion. Leave it out,
  or raise it as an open item if it is a real unanswered question.
- A **question is not a decision**, and a **proposal is not a decision**. If the
  material shows a proposal and no agreement, that is an open item at most.
- A **document to track is a source**, not a decision and not an open item --
  it goes in the Sources section per `project-log-reference.md` § Record a
  source. The test: tracked from it and staleness matters, it is a source; a
  useful address, it is a context link. When the material does not say which,
  ask -- it is a field needing judgement, so the run proposes rather than
  dictates.

Three branches open off this classification, each with its own section in
`project-log-reference.md`. Read one only where its condition holds; a run
where none does reads none of them.

- **The material says a decision was made outside this group and binds it** --
  a published standard, a policy, a contract term. Read § Mark a decision that
  was imposed. Never mark one imposed without it, and never conclude imposition
  from which team's document the material came out of.
- **The material states that one entry blocks or contradicts another.** Read
  § Record a relationship only where the source says so. Two entries that
  merely look related to you are not a relationship and never become a marker.
- **The run records a source.** Read § Record a source, the section the
  bullet above already names.

When you cannot tell, ask -- but never serially. Collect every clarifying
question the run needs -- classification, owners, links, anything -- after
Step 4 and the duplicate check, and ask them all in one round, one line each,
in the proposal's "Questions before I write" block. A question the user
answered, or that the material or config already answers, is never asked again
in the run. One follow-up question is allowed only when the user's own answer
created a new ambiguity, and it must name that answer as the cause. Do not
resolve an ambiguity yourself and do not log both readings.

### Attribute correctly

The owner is `@` plus one token, no spaces, lowercase.

- A person named in the material owns the entry (`@priya`).
- The user owns what the user says is theirs. Use the first token of
  `profile.name` from the config.
- Nobody identifiable means `@unassigned`. Write it out; never leave the field
  empty. An unowned decision is normal. An unowned open item is what
  `project-gaps` reports.

Never merge two people's positions into one entry.

### Say when a handle is new

A handle is free text and nothing has ever checked it, so one colleague
accumulates several spellings and neither the audit nor the summary sees a
problem. This is the check that surfaces that, and it is a **notice, not a
gate**. A genuinely new person is the ordinary case. What is worth the user's
attention is the moment a second spelling appears, when fixing it costs one
word.

Run it once the proposal's entries are settled -- after the duplicate check
below, so it sees the handles the run will actually write and not the ones a
merged or superseded candidate would have carried. It covers every handle the
run writes: a new entry's owner, and an owner changed by an edit. Skip
`@unassigned` entirely. That value is never reported: it is the documented way
to say there is no owner, not an unrecognized person.

**It catches drift as it arrives, and does not audit what is already there.** A
ledger that already holds both `@priya` and `@priya.nair` reports nothing on a
run that writes neither -- both are handles this ledger uses. Nothing here is a
sweep of the existing file, and `project-gaps` still does not read owners for
this.

1. **Look in this ledger first.** If the handle already appears as the
   `<owner>` of any entry, in either section -- resolved, superseded, it makes
   no difference -- it is known. Say nothing and stop here. This is the common
   case, and stopping here is why `personas.md` is usually never read at all.
2. **Otherwise resolve `profile.personas` and look there.** It resolves per
   `config-resolution.md` § Resolving `writing_style` and `personas`, and a
   `drive:` pointer is read through `config-drive.md`'s download mechanics. The
   handle is known if it names a persona section, or appears in one's `Known as`
   field. Match generously, the way `remember-persona` matches a heading:
   `Sarah`, `Sarah Kaur` and `@sarah` are one person when the file plainly means
   one person.
3. **In neither, report it** -- one line per handle, in the proposal, naming the
   handle and where it was not found.

**Name the near miss when there is one.** If a handle already in the ledger or
in `personas.md` plausibly means the same person -- one is a prefix or a longer
form of the other, or `Known as` lists a name the new handle is built from --
say which, phrased so it can be corrected in a word. That is the whole point of
the check: `@priya` and `@priya.nair` sitting in one ledger is the failure, and
it is invisible once both are written.

**It reads like a question and is still not one.** "Same person?" invites a
correction; it does not make the run wait. On the propose-then-wait path the
user is already being waited on, so they answer it or they do not. On the
same-turn path the entry is written and a correction afterwards is an ordinary
edit with its own `~D-nnn` Changelog line, exactly as that path already says of
every other correction. Nothing is lost either way, which is why this never
belongs in the "Questions before I write" block.

```
New owner handles:
- @priya.nair -- not in this ledger and not in personas.md. The ledger already
  uses @priya. Same person?
- @dana -- not in this ledger and not in personas.md.
```

**Never resolve it yourself.** Do not rewrite a handle to match an existing one,
do not merge two entries because they look like one person, and do not write
`personas.md` -- `remember-persona` owns every content write to that file, per
`config-writers.md` § Who writes what. Offering it is fine: "`/daikenja:remember-persona`
can record who `@dana` is." Running it is the user's call.

**The check never turns a run into a proposal.** It produces a notice, not a
question, so it does not fail condition 3 of the same-turn path above. A
dictated write still lands in the same turn, and the notice is shown alongside
the written lines. What it does require is that the check runs **before** the
write either way -- a handle reported after the fact is a handle already in the
file.

### Check for duplicates first

For each candidate, look for an entry that already records the same fact.

**Same subject is not the same fact.** A standing rule and a project decision
stay separate entries even when they read alike -- "scripts are never run by
hand against production" is a policy that holds across projects, and "build the
reload as a pipeline rather than a manual script" is one project's call. Merging
them loses which one a later reader is bound by. The test is what would have to
change for the entry to stop being true: if the answers differ, they are two
facts.

- **The same fact, already there.** Propose an edit to that entry, by ID. Do not
  append a near copy.
- **A decision that replaces an older one.** Propose a supersession, and mark it
  on **both** entries per the spec: the new body opens with `Supersedes D-nnn.`
  and the old entry gains its tail.
- **An open item the material settles.** Propose a resolution: flip the box and
  append the tail. Resolved items stay where they are.
- **Something that conflicts with an existing entry without replacing it.**
  That is a `Contradicts <id>.` marker on the new entry, not a supersession.
  Supersession says the old call is out of force; a contradiction says both are
  on record and somebody has to reconcile them, which is exactly the state
  worth recording rather than resolving on the user's behalf. An open item that
  reopens a decision already in force is the common shape here -- the decision
  keeps standing and the item says it is contested.
- **Genuinely new.** Propose a new entry with the next ID.

Two more branches open here, each with its own section in
`project-log-reference.md`, and both change the entry dates this run writes:

- **Most of the entries are older than what the ledger already holds** --
  recording a project that has history, usually reached through
  `/daikenja:setup-project`. Read § Backfilling an existing project.
- **The run was entered as `project-log via meeting-review`.** Read § A meeting
  date handed over by `meeting-review`.

An ordinary run reaches neither and dates every entry today.

### Show the proposal

Show exactly what will be written, verbatim, in a fenced block. Every line the
user approves is a line that lands in the file byte for byte.

```
Ledger: <path>              (creating it from the template)

Decisions -- new
- 2026-08-14 -- D-006 -- @carlos -- <body>

Open items -- resolving who is on call (O-003)
- [x] 2026-08-09 -- O-003 -- @carlos -- <body> -> resolved 2026-08-14, see D-006

Changelog
- 2026-08-14T16:40Z -- project-log -- +D-006, resolved O-003

New owner handles:
- <handle> -- not in this ledger and not in personas.md. <near miss, if any>

Questions before I write:
- <anything you could not classify, one line each>
```

The handles block is a **notice** and the questions block is a **question**: the
first needs no answer and the run proceeds without one, while the second is what
Step 6 waits on. Drop either block entirely when it is empty rather than writing
a heading with nothing under it.

Get both dates from the environment, not from memory:

- `date +%Y-%m-%d` -- **local** date, for an ordinary write's entry date
  field. That is the day the user means by "today". A backfilled date or a
  meeting date handed over by `meeting-review` overrides it, per
  `project-log-reference.md` § Backfilling an existing project and § A meeting
  date handed over by `meeting-review`.
- `date -u +%Y-%m-%dT%H:%MZ` -- **UTC** timestamp, for the Changelog line. The
  contract fixes this one as UTC.

They are not always the same day. Do not derive one from the other.

Keep the proposal to what the material supports. Five clean entries beat twelve
padded ones.

## Step 6: wait

Stop and wait for the user.

- **Approved.** Write it.
- **Partly approved** ("just the first two", "drop the second one"). Write only
  what was approved. Do not argue for the rest.
- **Edited** ("change the owner to @sam"). Show the corrected block and wait
  again. A changed line is a new proposal -- but it re-opens no settled
  question. Ask nothing the run has already resolved.
- **Rejected.** Write nothing. Say nothing was written.

Silence is not approval. Neither is the user replying about something else.

## Step 7: write

Insert every new entry at its **date position**: directly above the first entry
in that section whose date is the same as or older than its own, and at the end
of the section when there is no such entry. See `ledger-format.md` § Ordering.

For an entry dated today -- every ordinary write -- that position is directly
under the H2 heading, which is what the rule used to say. A backfilled entry
sorts into the file instead of piling up on top of newer ones. The Changelog
line is timestamped now, so it is always the newest line and always goes
directly under its heading; a context link or a source has no ordering rule
and goes directly under its heading too.

Insert one line in one place. Do not sort the section, and do not move the
entries around it.

A body carrying markers writes them in the fixed order `ledger-format.md`
§ Body markers sets out -- `Supersedes D-nnn.`, `Imposed.`, relationship
markers, `Approximate date.`, then the body proper. That order is part of the
contract rather than a preference: a reader can find a marker without reading
the whole body only if every entry puts them in the same place.

Edits, resolutions and supersessions change the line in place. Nothing moves.

Deleting an entry, when the user asks for it, removes the line and records
`-D-nnn` or `-O-nnn` in the Changelog. The ID stays retired.

Touch nothing else. Do not reorder, do not reformat, do not tidy the file, and
do not normalize a line a human wrote by hand. Humans reorder Open items on
purpose and this skill restores nothing.

## Step 8: append the Changelog line and confirm

One line per `project-log` run, at the top of the Changelog, naming every
change by ID with one verb each. The verb set and the field grammar are in
`ledger-format.md` § Section: Changelog.

The writer field is `project-log`, or `project-log via <skill>` when another
skill ran this one.

Every change to an entry gets recorded. A write that does not appear in the
Changelog is invisible to `project-catchup`, which reads changelog lines and
never diffs the file. When one run touches several entries, they all go on
that run's single line.

Context links carry no ID, so they are recorded by label instead: `+link
"<label>"` for an addition, `-link "<label>"` for a removal. A run that only
touches links still writes a Changelog line -- it just names links instead of
IDs. A source is named by its ID and takes the three symbol verbs only:
`+S-nnn`, `~S-nnn`, `-S-nnn`.

**A bulk run may compact its summary**, per `ledger-format.md` § Compacting a
long summary: consecutive IDs taking the same verb become a dense range
(`+D-006..D-021`), and a summary too long for one line continues on lines
indented two spaces. Both are lossless and `project-catchup` expands them. Do
not compact a short summary, and never write a sparse range -- if an ID inside
the interval was untouched or took a different verb, write two ranges or list
the IDs.

Then confirm in one or two lines: what was written, where, and the IDs --
topic first, ID in parentheses, per `response-format.md`.

```
Wrote 2 entries to C:/GitHub/atlas/.daikenja/ledger.md -- the pipeline
decision (D-006), and resolved who is on call (O-003).
```

When a written entry names or links another document in the project, offer the
follow-up instead of leaving it to the user to raise elsewhere: "The rollout
decision (D-006) points at docs/rollout.md -- update it to match?" Updating
that document is outside this skill's write scope, so it happens only on the
user's yes, as its own change -- never under the ledger write's approval.


## Failure cases

`project-log-reference.md` § Failure cases. One notice line, then continue with
reduced behavior; hard-stop only when the missing thing is the task itself.
Read the table the moment a run meets a situation the steps above do not settle
-- a config file that will not parse, a key that matches nothing, a ledger that
is missing, unreadable or short a section, a date or an owner that cannot be
established -- and before improvising a way through one.

## What this skill does not do

`project-log-reference.md` § What this skill does not do. Read it when a run is
about to do something no step above told it to.
