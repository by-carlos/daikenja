# Project-log reference

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Step 3: scaffold the ledger when it is missing -- project-log "Step 3: scaffold the ledger when it is missing"
- § Mark a decision that was imposed -- project-log "Classify before you write"
- § Record a relationship only where the source says so -- project-log "Classify before you write"
- § Record a source -- project-log "Classify before you write"
- § A batch handed over by another skill -- project-log "Hard rules"
- § Backfilling an existing project -- project-log "Check for duplicates first"
- § A meeting date handed over by `meeting-review` -- project-log "Check for duplicates first"
- § Failure cases -- project-log "Failure cases"
- § What this skill does not do -- project-log "What this skill does not do"

The `project-log` sections a run reaches only on some branches. Every rule here
is `project-log`'s own and binding on it exactly as if it sat in `SKILL.md`;
nothing else reads this file.

**This is not a contract two skills agree on**, which is what the rest of
`docs/` holds. It is one skill's instructions, kept here rather than inline so
a run that never reaches a branch never pays to read it.

**The hard rules in `SKILL.md` still govern everything here.** Nothing on this
page licenses a write the user has not stated or approved, an invented entry,
a repair made on this skill's own initiative, a commit, or a write from another
skill.

The two files are specified by [`decisions-format.md`](decisions-format.md) and
[`open-format.md`](open-format.md). This page cites them and never restates
their grammar.

## Step 3: scaffold the ledger when it is missing

A file is scaffolded only when the batch writes to it and it does not exist:
`DECISIONS.md` at the root of the repository the decision was placed in, or
`.daikenja/open.md` in the home repository. A batch of open items alone never
creates a `DECISIONS.md`, and a batch of decisions alone never creates an
`open.md`.

**Never over an unmigrated ledger.** `SKILL.md` Step 2 has already refused a
home repository holding `.daikenja/ledger.md` with no `open.md` beside it. A
`DECISIONS.md` existing there does not lift the refusal, and nothing here
scaffolds around it. The one exception is § A batch handed over by another
skill, for the migration.

**Never over an existing `DECISIONS.md`.** One that exists is adopted, whoever
wrote it: entries go into it, in its own areas, and it is never replaced by the
template. If the repository plainly keeps its current decisions in a document
by another name, say so and ask before creating a parallel `DECISIONS.md`, per
`decisions-format.md` § Where it lives -- and say that Daikenja reads only
`DECISIONS.md`.

**The checks run against the directory the file would be created in**, which
for `open.md` is the home repository, not necessarily the directory you are
standing in. Name that directory in every question and every refusal, so
nobody approves a write to a folder they did not have in mind.

**Refuse outright** when that directory is the user's home directory (the real
OS home, e.g. `~`) or `~/.claude`. Say so in one line and stop -- there is
nothing to propose. This is unconditional: matching takes the longest prefix
and `daikenja.yaml` is hand-editable, so a matched project is not evidence that
the directory is one.

```
Won't create a ledger in <path> -- that's your home directory, not a project.
Run this from the project you mean to log.
```

**Otherwise, if the directory is not a git repository** (no `.git`) **and is
not registered in `daikenja.yaml`**, ask before anything else, naming the exact
absolute path. This confirmation is separate from the Step 5 approval, because
it settles whether a ledger belongs here at all:

```
<path> isn't a git repository and isn't registered. Daikenja keeps a ledger's
history in git. Create the ledger there anyway?
```

A no ends the run; say nothing was written. A registered directory skips the
question: registration already settled it.

**Otherwise** say so plainly, and fold the scaffold into the Step 5 proposal --
one approval covers creating the file and writing the first entries:

```
No ledger at <path>. I will create <file> from the Daikenja template.
```

- `open.md`: copy `${CLAUDE_PLUGIN_ROOT}/templates/open.md` and replace
  `{{PROJECT}}` with the `projects:` key, or the directory's name when
  unregistered.
- `DECISIONS.md`: copy `${CLAUDE_PLUGIN_ROOT}/templates/DECISIONS.md` as it
  stands. When the repository has an ADR folder, add the `ADRs:` line under
  the title, per `decisions-format.md` § Where it lives.

Change nothing else in either template. After creating a `DECISIONS.md`, offer
once to add the pointer line to the repository's agent instructions file, per
`decisions-format.md` § The pointer line. That file is outside this skill's
write scope, so it changes only on the user's yes, as its own change.

## Mark a decision that was imposed

A decision made **outside the group and binding on it** -- a platform team's
published standard, a security policy, a contract term -- says so in its why
clause: `— imposed by the programme's architecture board.` There is no marker,
per `open-format.md` § Writing.

The test is **whether this group could reopen it**. A decision the user argued
for and won inside a programme is theirs, even though the programme published
it. A standard handed down that the user can only comply with, seek an
exemption from, or escalate is imposed. When the material does not settle
which, ask -- never conclude it from which team's document the material came
out of.

**Offer the open item, never write it.** An imposed decision creates work on
this side -- comply, seek an exemption, escalate -- and that work is what
`/daikenja:project-gaps` audits. When the material does not already name it,
offer in one line to raise it, saying that nobody on this side is on the hook
yet and asking who is. On the propose-then-wait path the offer goes in
"Questions before I write"; on the same-turn path it goes beside the written
lines, and the dictated decision still lands. Writing the item unasked would be
inventing an entry.

## Record a relationship only where the source says so

The one relationship recorded is a block between open items: the blocked item's
text opens with `Blocked by: <the other item, in words>.`, per `open-format.md`
§ `Blocked by:`. The item it names gains nothing.

**Write one only when the material states it.** "We can't start this until the
exemption criteria are published" is a block. Two items that merely look
related to you are not, however obvious it seems. When the material hints at a
block without stating it, that is a line in "Questions before I write".

- **The named item must be in `open.md`.** Name it in words the reader can
  match to one line. When none matches, or several could, ask which was meant;
  do not write the prefix until it is settled.
- **Adding a prefix to an item already written is an ordinary edit.**
- **Closing the named item never rewrites the blocked one on its own.** The
  proposal offers to drop the prefix in the same batch; the user decides.

Nothing else is recorded as a relationship. A conflict between two decisions is
settled before writing (`SKILL.md` § Check for duplicates first). An open item
that questions a decision in force says so in its own words, and the decision
stays as it is.

## Record a source

A source -- a document this project is tracked from -- goes in `open.md`'s
`## Sources` section as a head line plus optional field lines, per
`open-format.md` § Section: Sources. It needs a dictation or an approval like
any other entry.

- **Write only the fields the material supplies.** An absent field means
  unknown and stays absent. Never fetch the target to fill `modified:` in --
  that is `/daikenja:project-sources`'s job, and a refresh comes back through
  this skill with the values already established.
- **`modified:` and `read:` move together**, only when the source was actually
  read -- by the user, or shown to them in a `project-sources` run. Neither is
  ever today's date by default.
- **A dictated source takes the same-turn path** under the same four conditions
  as any entry.
- **The same target already recorded as a source is an edit**, not a second
  source. A context link with the same target is not a duplicate; nothing
  turns a link into a source unless the user asks.

## A batch handed over by another skill

`setup-project`'s seed and the migration in `docs/ledger-migration.md` produce
entries and hand them here; `meeting-review` does the same with what a
transcript settled. Each is a `project-log via <skill>` run:

- **Entries arrive classified**, with the repository each decision belongs to
  when the handing skill knows it. Where it does not, Step 5's repository
  question is asked like any other.
- **Every check still runs**: the version refusal, the duplicate check against
  what the files already hold, the keep rule, the owner check, and one approval
  for the whole batch. A large batch may be shown and approved in tranches;
  each tranche is its own approval.
- **An existing `DECISIONS.md` is extended, never overwritten**, exactly as in
  § Step 3.
- **The migration's own batch names its targets by absolute path**, so this
  skill does not resolve that project from the config, which is part of what
  the migration changes. The refusals for an unmigrated ledger and for an
  entry with no paths do not apply to this batch -- it is the run both point
  at -- and every other check does. Both refusals apply to every other run,
  `setup-project`'s seed included.

## Backfilling an existing project

A backfill is a run whose open items are mostly older than today -- recording a
project that has history, usually reached through `/daikenja:setup-project`.
Decisions carry no date, so for them a backfill changes nothing but the keep
rule's weight: an old decision still in force is kept, one the code already
makes plain is not.

**Date each open item when it was raised, not today.** That is what the field
means, per `open-format.md` § Section: Open items.

**A date the source never recorded is asked for, never invented.** If the user
can only place it approximately, normalize their approximation to the first day
of the coarsest unit they gave ("March 2026" becomes `2026-03-01`), and say in
the proposal which items this applies to and what each date was derived from,
so the user approves the derivation and not just the line. If the user cannot
approximate it either, the item is not written: name the ones dropped and why.

**Say what the dates do to the audit before the write.** Items dated to their
origin are older than `stale_after_days` the moment they land, so
`/daikenja:project-gaps` reports them on its next run. That surprises people
and it is the audit working.

## A meeting date handed over by `meeting-review`

A `project-log via meeting-review` run carries the meeting's own date, or
states that the transcript never gave one. A handed-over date is the date of
every open item the run writes, exactly as if the user had supplied it.
Decisions carry no date and are unaffected.

**No meeting date** is an item whose date cannot be established: ask for it. An
approximation is a real answer, handled as in § Backfilling an existing
project. Never invent one and never fall back to today.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, then continue on the defaults: the current directory is the one root, owner `@unassigned` unless the user names one. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never rewrite the file. |
| A named project key matches no entry | **Stop.** Name the key, list the registered keys, write nothing. Never fall back to directory matching. |
| A named project key matches an entry that has paths | **Use it**, from any directory. Its files resolve from the entry alone; the proposal names each by absolute path. Never fall back to directory matching. |
| The project's entry is `paths: []` or has no path | **Stop** with the "needs migration" line from `reading.md` § Notices, shared wording. |
| The entry still has a `ledger:` key | One line naming the key and `/daikenja:setup-user`, then continue with the fixed paths. |
| `.daikenja/ledger.md` at home with no `open.md` beside it | **Refuse** with the "needs migration" line. Scaffold nothing and write nothing, whether or not a `DECISIONS.md` exists. Not applied to the migration's own batch. |
| Either file carries a newer format version | **Refuse the whole batch.** Name the file and version, ask for a plugin update, cite `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md`. Nothing is written to either file. |
| A file has no version line | Read it as version 1; the proposal adds the line. |
| A version line does not parse | Report it, read the file as version 1, and the proposal replaces the line with the correct one. |
| A file to write is missing and its directory is the home directory or `~/.claude` | **Stop.** Refuse to scaffold. Unconditional. |
| A file to write is missing and its directory is neither a git repository nor registered | One question naming the absolute path. Wait for yes. |
| A repository has a current-decisions document under another name | Ask before creating a parallel `DECISIONS.md`. |
| A file is unreadable or not writable | **Stop.** Name the path and the error. Never write the entries somewhere else. |
| `open.md` is missing one of its three H2 sections | **Stop.** Name it. Offer to add the empty heading as its own approved write. Report any other defect seen while reading, and write nothing. |
| A `DECISIONS.md` area has no `Paths:` line | Report it. Still add to that area when the user places an entry there; never add the line unasked. |
| A line does not match its file's grammar | Report it -- which line, what is wrong -- then continue. An indented continuation line is not an error. |
| A decision's repository cannot be told from its paths | Ask which repository's `DECISIONS.md`, in "Questions before I write". Never write it to two. |
| A decision's why or revisit condition is not in the material | Ask. Never fill it in. |
| A decision conflicts with one in force | Ask which holds. Write the answer, never the conflict. |
| A `Blocked by:` the material implies but never states | One line in "Questions before I write". |
| A `Blocked by:` naming no item in `open.md`, or several | Do not write it. Ask which item was meant. |
| An existing item's `Blocked by:` names an item no longer there | Report it as a block on an item that is no longer open, then continue. Dropping it is a separate approved write. |
| The material does not settle whether a decision was imposed | Ask, in one line. |
| An open item's date cannot be established | Ask. An approximation is a real answer. Never invent one, never fall back to today; if the user cannot approximate it, drop the item and say so. |
| An owner handle appears neither in `open.md` nor in `personas.md` | One line in the proposal naming it and any near miss. Never a block, never a rewrite. |
| `personas` is not configured, or its local file is missing | Check `open.md` alone, with one notice that the comparison was narrower. |
| `personas` is a `drive:` pointer that does not resolve | **Stop** before writing, per `config-resolution.md` § Failure behavior. Show the lines that would have been written, say nothing was written, never fall back to a local file. Reached only when a handle is not in `open.md`. |
| Nothing in the material is worth logging | Say so and write nothing. |

## What this skill does not do

- It does not commit, stage or push. The files change in the working tree and
  the user commits them; `/daikenja:project-catchup` lists them as not
  committed yet.
- It does not summarize a thread for reading. That is `/daikenja:thread`.
- It does not report what changed since last time. That is
  `/daikenja:project-catchup`, from git history.
- It does not check whether a source moved, and it never fetches a source's
  target. That is `/daikenja:project-sources`.
- It does not write an ADR, or the pointer line in an agent instructions file.
  It may offer either; the user does it, or says yes to it as its own change.
- It does not write `daikenja.yaml`. `/daikenja:setup-user` owns the `profile:`
  block, `/daikenja:setup-project` owns a project's entry, and
  `last_checkpoint` belongs to `project-catchup`.
- It does not migrate an old ledger. `/daikenja:setup-user` starts that, and
  the migration hands its batch here.
- It does not write `personas.md` or validate an owner handle. It reads that
  file to check a handle and may offer `/daikenja:remember-persona`.
- It does not sweep either file for entries to link, merge, retire or reorder.
  It writes what the batch says and nothing else.
