---
name: project-log
description: Records decisions and open items in a project's Daikenja ledger. Use when the user says "log this", "record this decision", "add this to the ledger", "capture the open items", "note that we agreed X", or pastes a thread or a plain description and asks for what was settled to be written down. Not for a meeting transcript -- that is /daikenja:meeting-review, which classifies it in two passes before handing entries to this skill. Also use when a project has no ledger yet and one is asked for. This is the only skill that writes ledger content -- every other Daikenja skill reads it. A short fact the user dictates is written in the same turn and shown verbatim; everything else is proposed first and written only on approval.
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
  IDs, tails, Changelog, and the reading rules.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- where the config lives, how
  a project and its ledger are resolved, and what to do when config is missing.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-versioning.md` -- the version-marker notice
  this skill emits and never migrates.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Proposed ledger lines stay in file grammar; the talk around them
  follows this.

One more, read only when the run actually needs it:
`${CLAUDE_PLUGIN_ROOT}/docs/config-drive.md`, for the download mechanics behind
a `drive:` pointer. Step 5's owner check is the only thing here that reads
`personas.md`, and it reads it only when a run carries a handle this ledger does
not already know.

If they ever disagree with this skill, the contract wins and you say so.

## Step 1: get the material

- **A link was given.** Fetch it with whatever tool is connected (Slack, email,
  a web fetch, an MCP server). Get the whole thread, not the preview.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **A plain description was given** ("log that we picked Postgres"). That is
  enough material. Use it.
- **Nothing was given.** Ask what to log. Do not search for it, and do not go
  reading the repository to guess what happened.

If a fetch fails, say what failed in one line and ask for a paste. Never guess
at the content of something you could not read.

## Step 2: resolve the config, the project and the ledger

Follow `config-resolution.md` § Resolution order exactly. In short:

1. Read `~/.claude/daikenja/daikenja.yaml`. Absent is not fatal here -- this
   skill works on defaults. Malformed YAML **is** fatal: report the first line
   that does not parse and stop.
2. Match the current directory against **every path of every `projects:`
   entry** -- its `paths` list, or its `path` scalar read as a one-element
   list -- normalized and longest prefix wins across all of them. An entry with
   no paths is skipped; it is reachable only by key, and this skill does not
   resolve by key.
3. Resolve the ledger: the matched project's `ledger:` key if it has one --
   relative or absolute, per `config-resolution.md` § Resolving `ledger` -- and
   that resolved path is authoritative. Otherwise `.daikenja/ledger.md` under
   the project root. **The root is the first path in the entry**, not the path
   that matched -- a project spanning three repositories has one ledger, in the
   first of them.
4. Check the version marker and emit the one-line notice if it applies, per
   `config-versioning.md` § Version marker and upgrades. It never blocks a write,
   and this skill never migrates anything -- `/daikenja:setup-user` does that.

**This skill resolves by directory only, and takes no project key.** The read
skills take one because reading is location-free; writing is not. A key names a
project, and a project may have three roots or none, so a key alone does not
say where a ledger entry belongs. To log against a project you are not in, go
to it first.

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

If the ledger file does not exist, check first whether this directory is
plausibly a project. Nothing about a missing ledger says it is -- the current
directory could just as easily be the user's home directory or a scratch
folder they happened to be in.

**The checks below run against the directory the ledger would be created in.**
That is the project root when a `projects:` entry matched, which for a
multi-path project is the first path in the entry and need not be the
directory you are standing in. Name that directory in every question and every
refusal, so nobody approves a write to a folder they did not have in mind. A
match does not excuse a check: `daikenja.yaml` is hand-editable and matching
takes the longest prefix, so a matched project is not evidence that the
directory is one.

**Refuse outright** when the current directory is the user's home directory
(the real OS home, e.g. `~`) or `~/.claude`. Say so in one line and stop. Do
not scaffold, and do not fold this into the Step 5 proposal -- there is
nothing to propose:

```
Won't create a ledger in <path> -- that's your home directory, not a project.
Run this from the project you mean to log.
```

**This refusal is unconditional.** A `projects:` entry matching the home
directory does not license scaffolding there. Matching takes the longest
prefix, so an entry with a path that is the home directory's parent makes the
home directory itself resolve to a project, and `daikenja.yaml` is hand-editable --
so a matched project is not evidence that this directory is one.
`setup-project` refuses to register either path for the same reason.

**Otherwise, if the directory is neither a VCS root** (no `.git`) **nor
already holds a `.daikenja/`**, it still is not obviously a project -- unless
it is **already registered in `daikenja.yaml`**, in which case skip this check
and go straight to the "otherwise" branch below. Registration is a deliberate
act that settles the question these two markers only guess at, and a project
with no repository of its own has neither marker: no `.git`, and no
`.daikenja/` until its first log. Without this exemption such a project is
asked to confirm itself on every first log.

For an unregistered directory carrying neither marker, ask, naming the exact
absolute path, before doing anything else -- this confirmation is separate
from the Step 5 write approval, because it settles whether a ledger belongs
here at all, not what goes in it:

```
<path> doesn't look like a project (no .git, no .daikenja/). Create a ledger
there anyway?
```

Wait for a yes before continuing. A no ends the run here; say nothing was
written.

**Otherwise** (a VCS root, a directory that already has `.daikenja/`, or a
registered project), say so plainly before doing anything else:

```
No ledger at <path>. I will create one from the Daikenja template.
```

Create the parent directory, copy `${CLAUDE_PLUGIN_ROOT}/templates/ledger.md`,
and replace `{{PROJECT}}` with the project's name: the `projects:` key if the
project is registered, otherwise the project directory's name. Change nothing
else in the template. The commented examples stay -- they are the format hint
for whoever opens the file next.

Scaffolding is a write, so it needs approval like any other. Fold it into the
Step 5 proposal: one approval covers creating the file and writing the first
entries.

A scaffolded ledger gets no Changelog line of its own. The first real write
supplies it.

## Step 4: read what is already there

Read the whole ledger before proposing anything. You need three things from it.

**The four sections.** Locate each by its exact H2 heading. If one is missing,
stop and use the failure table below.

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
   batch and follows propose-then-wait.

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
- **Genuinely new.** Propose a new entry with the next ID.

### Backfilling an existing project

A backfill is a run whose entries are mostly older than what the ledger already
holds -- recording a project that has history, usually reached through
`/daikenja:setup-project`. Classification, attribution, the duplicate check and
the approval gate are all unchanged. Three things are specific to it.

**Date each entry when its subject was decided or raised, not today.** That is
what the date field means, and a backfill is the one situation where the two
differ for every entry.

**A date the source never recorded is asked for, never invented.** If the user
can only place it approximately, take their approximation, normalize it to the
first day of the coarsest unit they gave ("March 2026" becomes `2026-03-01`),
and open that entry's body with the literal `Approximate date.` followed by
where the approximation came from. The proposal says which entries this applies
to and what each date was derived from, so the user approves the derivation and
not just the line. If the user cannot approximate it either, the entry is not
written: name the ones dropped and why.

**Say what the dates do to the audit before the write.** Entries dated to their
origin are older than `stale_after_days` the moment they land, so
`/daikenja:project-gaps` reports the open ones on its next run. That surprises
people and it is the audit working.

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

- `date +%Y-%m-%d` -- **local** date, for the entry's date field. That is the
  day the user means by "today".
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
directly under its heading; a context link has no ordering rule and goes there
too.

Insert one line in one place. Do not sort the section, and do not move the
entries around it.

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
IDs.

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

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, then continue on the defaults (`.daikenja/ledger.md`, owner `@unassigned` unless the user names one). Do not stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| Ledger missing and the current directory is the home directory or `~/.claude` | **Stop.** Refuse to scaffold. Name the path and say why. Unconditional -- a matching `projects:` entry does not license it. |
| Ledger missing and the current directory is neither a VCS root nor already has `.daikenja/` | One question, naming the absolute path, before scaffolding. Wait for yes before continuing. Skipped when the directory is a registered project. |
| Project unregistered | One line naming `/daikenja:setup-project`, per Step 2, then carry on with the ledger. |
| Ledger path unreadable or not writable | **Stop.** Name the path and the error. Do not fall back to another location and do not write the entries somewhere else. |
| Ledger missing a required H2 section | **Stop.** Name the missing section. Offer to add the empty heading as its own approved write. Do not write entries into a file whose shape you had to guess. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. A line indented two or more spaces with no list marker is a continuation, not an error. |
| A Changelog ID resolves to no entry | One line saying so, then continue. Somebody deleted an entry by hand. Do not rewrite the Changelog. |
| Supersession marked on only one of the two entries | Report the mismatch, naming both IDs. The tail is authoritative. Do not repair it as a side effect of another write. |
| An entry's date cannot be established | Ask for it. An approximation is a real answer and is written with the `Approximate date.` marker. Never invent one, and never fall back to today. If the user cannot approximate it, drop that entry and say so. |
| An owner handle appears neither in this ledger nor in `personas.md` | One line in the proposal naming the handle, and the near miss if there is one. Never a block, never a rewrite of the handle. |
| `personas` is not configured, or its local file is missing | Check the ledger alone, with one notice saying the comparison was narrower for it. Not an error -- the file is optional prose, not a roster. |
| `personas` is a `drive:` pointer that does not resolve, or reads back empty | **Stop** before writing, per `config-resolution.md` § Failure behavior. Show the proposal so the user keeps it, say nothing was written, and never fall back to a local file. Reached only when a run has a handle this ledger does not already know. |
| Nothing in the material is worth logging | Say so and write nothing. An empty ledger is better than a padded one. |

## What this skill does not do

- It does not summarize a thread for reading. That is `/daikenja:thread`.
- It does not report what changed since last time. That is
  `/daikenja:project-catchup`.
- It does not write `daikenja.yaml`. `/daikenja:setup-user` owns the `profile:`
  block, `/daikenja:setup-project` owns a project's `projects:` entry, and
  `last_checkpoint` belongs to `project-catchup`.
- It does not archive, prune or trim anything on a schedule. Old resolved items
  stay until a human asks for them to go.
- It does not write `personas.md`. It reads that file to check a handle and may
  offer `/daikenja:remember-persona`, which owns every content write to it.
- It does not validate an owner handle. There is no list of legal owners, no
  rejection and no correction -- only the notice in Step 5.
