---
name: project-log
description: Records decisions and open items in a project's Daikenja ledger. Use when the user says "log this", "record this decision", "add this to the ledger", "capture the open items", "note that we agreed X", or pastes a thread or a plain description and asks for what was settled to be written down. Not for a meeting transcript -- that is /daikenja:meeting-review, which classifies it in two passes before handing entries to this skill. Also use when a project has no ledger yet and one is asked for. This is the only skill that writes ledger content -- every other Daikenja skill reads it. It proposes entries and writes nothing without approval.
metadata:
  owner: Carlos
  version: 1
  writes: <project>/.daikenja/ledger.md
---

# Log

The ledger is the project's memory. This skill is the only thing that writes it.

## Hard rules

**Never write without approval.** Show the exact lines first, wait for the user
to say yes, then write. "Yes" means the user said so in this conversation. An
approval of one proposal does not carry to the next one.

**Never invent an entry.** Everything written comes from the material the user
gave you. If something is implied but not said, put it in the proposal as a
question, not as an entry.

**Never repair a broken ledger on your own initiative.** Report the problem,
name the line, and stop. Repair is a separate write and needs its own approval.

**Never write the ledger from any other skill.** Another skill that needs an
entry runs this one. The Changelog then records the writer as
`project-log via <skill>`.

## Step 0: read the contracts

Read these two files before writing anything. They are binding, and they are the
only place their detail lives. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- section names, entry grammar,
  IDs, tails, Changelog, and the reading rules.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` -- where the config lives, how
  a project and its ledger are resolved, and what to do when config is missing.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Proposed ledger lines stay in file grammar; the talk around them
  follows this.

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

Follow `config-contract.md` § Resolution order exactly. In short:

1. Read `~/.claude/daikenja/daikenja.yaml`. Absent is not fatal here -- this
   skill works on defaults. Malformed YAML **is** fatal: report the first line
   that does not parse and stop.
2. Match the current directory against the `projects:` entries by `path`,
   normalized and longest prefix wins. The project key is a label and is never
   matched on.
3. Resolve the ledger: the matched project's `ledger:` key, otherwise
   `.daikenja/ledger.md` under the project root.

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

**Refuse outright** when the current directory is the user's home directory
(the real OS home, e.g. `~`) or `~/.claude`. Say so in one line and stop. Do
not scaffold, and do not fold this into the Step 5 proposal -- there is
nothing to propose:

```
Won't create a ledger in <path> -- that's your home directory, not a project.
Run this from the project you mean to log.
```

**Otherwise, if the directory is neither a VCS root** (no `.git`) **nor
already holds a `.daikenja/`**, it still is not obviously a project. Ask,
naming the exact absolute path, before doing anything else -- this
confirmation is separate from the Step 5 write approval, because it settles
whether a ledger belongs here at all, not what goes in it:

```
<path> doesn't look like a project (no .git, no .daikenja/). Create a ledger
there anyway?
```

Wait for a yes before continuing. A no ends the run here; say nothing was
written.

**Otherwise** (a VCS root, or a directory that already has `.daikenja/`), say
so plainly before doing anything else:

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

## Step 5: build the proposal

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

When you cannot tell, ask. One line, one question. Do not resolve the ambiguity
yourself and do not log both readings.

### Attribute correctly

The owner is `@` plus one token, no spaces, lowercase.

- A person named in the material owns the entry (`@priya`).
- The user owns what the user says is theirs. Use the first token of
  `profile.name` from the config.
- Nobody identifiable means `@unassigned`. Write it out; never leave the field
  empty. An unowned decision is normal. An unowned open item is what
  `project-gaps` reports.

Never merge two people's positions into one entry.

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

Questions before I write:
- <anything you could not classify, one line each>
```

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
  again. A changed line is a new proposal.
- **Rejected.** Write nothing. Say nothing was written.

Silence is not approval. Neither is the user replying about something else.

## Step 7: write

Insert every new entry **directly under its H2 heading**. That is the single
insert rule and it is the same in every section, including the Changelog.

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

Then confirm in one or two lines: what was written, where, and the IDs --
topic first, ID in parentheses, per `response-format.md`.

```
Wrote 2 entries to C:/GitHub/atlas/.daikenja/ledger.md -- the pipeline
decision (D-006), and resolved who is on call (O-003).
```

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, then continue on the defaults (`.daikenja/ledger.md`, owner `@unassigned` unless the user names one). Do not stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| Ledger missing and the current directory is the home directory or `~/.claude` | **Stop.** Refuse to scaffold. Name the path and say why. |
| Ledger missing and the current directory is neither a VCS root nor already has `.daikenja/` | One question, naming the absolute path, before scaffolding. Wait for yes before continuing. |
| Project unregistered | One line naming `/daikenja:setup-project`, per Step 2, then carry on with the ledger. |
| Ledger path unreadable or not writable | **Stop.** Name the path and the error. Do not fall back to another location and do not write the entries somewhere else. |
| Ledger missing a required H2 section | **Stop.** Name the missing section. Offer to add the empty heading as its own approved write. Do not write entries into a file whose shape you had to guess. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. A line indented two or more spaces with no list marker is a continuation, not an error. |
| A Changelog ID resolves to no entry | One line saying so, then continue. Somebody deleted an entry by hand. Do not rewrite the Changelog. |
| Supersession marked on only one of the two entries | Report the mismatch, naming both IDs. The tail is authoritative. Do not repair it as a side effect of another write. |
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
