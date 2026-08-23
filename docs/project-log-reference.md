# Project-log reference

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Step 3: scaffold the ledger when it is missing -- project-log "Step 3: scaffold the ledger when it is missing"
- § Mark a decision that was imposed -- project-log "Step 5: build the proposal"
- § Record a relationship only where the source says so -- project-log "Step 5: build the proposal"
- § Record a source -- project-log "Step 5: build the proposal"
- § Backfilling an existing project -- project-log "Step 5: build the proposal"
- § A meeting date handed over by `meeting-review` -- project-log "Step 5: build the proposal"
- § Failure cases -- project-log "Failure cases"
- § What this skill does not do -- project-log "What this skill does not do"

The `project-log` sections a run reaches only on some branches. Every rule here
is `project-log`'s own and binding on it exactly as if it sat in `SKILL.md`;
nothing else reads this file.

**This is not a contract two skills agree on**, which is what the rest of
`docs/` holds. It is one skill's instructions, kept here rather than inline so
a run that never reaches a branch never pays to read it. `SKILL.md` names the
section to read at the point each branch opens, and a run that opens none of
them reads none of this file.

**The hard rules in `SKILL.md` still govern everything here.** Nothing on this
page licenses a write the user has not stated or approved, an invented entry,
a repair made on this skill's own initiative, or a ledger write from another
skill.

## Step 3: scaffold the ledger when it is missing

If the ledger file does not exist, check first whether its location is
plausibly a project. Nothing about a missing ledger says it is -- the
directory could just as easily be the user's home directory or a scratch
folder they happened to be in.

**The checks below run against the directory the ledger would be created in.**
That is the project root when a `projects:` entry matched by directory, which
for a multi-path project is the first path in the entry and need not be the
directory you are standing in. **For an entry matched by key** (Step 2's one
exception, a pathless project) **there is no root at all** -- the directory
these checks run against is the parent of the resolved absolute `ledger:`
path instead. Name that directory in every question and every refusal, so
nobody approves a write to a folder they did not have in mind. A match does
not excuse a check: `daikenja.yaml` is hand-editable and matching takes the
longest prefix, so a matched project is not evidence that the directory is
one.

**Refuse outright** when that directory is the user's home directory (the
real OS home, e.g. `~`) or `~/.claude`. Say so in one line and stop. Do not
scaffold, and do not fold this into the Step 5 proposal -- there is nothing to
propose:

```
Won't create a ledger in <path> -- that's your home directory, not a project.
Run this from the project you mean to log.
```

**This refusal is unconditional**, and it applies the same way to a
key-resolved pathless entry: a `ledger:` pointer that resolves straight into
`~` or `~/.claude` refuses exactly like a directory match would, even though
no directory was ever compared. A `projects:` entry matching the home
directory does not license scaffolding there either way. Matching takes the
longest prefix, so an entry with a path that is the home directory's parent
makes the home directory itself resolve to a project, and `daikenja.yaml` is
hand-editable -- so a matched project is not evidence that this directory is
one. `setup-project` refuses to register either path for the same reason.

**Otherwise, if the directory is neither a VCS root** (no `.git`) **nor
already holds a `.daikenja/`**, it still is not obviously a project -- unless
it is **already registered in `daikenja.yaml`**, in which case skip this check
and go straight to the "otherwise" branch below. Registration is a deliberate
act that settles the question these two markers only guess at, and a project
with no repository of its own has neither marker: no `.git`, and no
`.daikenja/` until its first log. **A pathless entry reached by key is always
in this registered case** -- Step 2 only ever resolves one by matching it in
`daikenja.yaml`, so this check never has to guess for it. Without this
exemption such a project is asked to confirm itself on every first log.

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

## Mark a decision that was imposed

A decision made **outside the group keeping this ledger and binding on it** --
a platform team's published standard, a security policy, a contract term --
opens its body with the literal `Imposed.` followed by who imposed it, per
`ledger-format.md` § A decision imposed from outside. Anything the group
decided itself carries no marker; that is the ordinary case and there is
nothing to write for it.

The test is not who is named in the material, it is **whether this group could
reopen it**. A decision the user argued for and won inside a programme is
theirs, even though the programme published it. A standard handed down that the
user can only comply with, seek an exemption from, or escalate is imposed. When
the material does not settle which, ask in the proposal -- never guess, and
never mark a decision imposed because it arrived from another team's document.

`@unassigned` is the usual owner for an imposed decision, and it is not a gap.
Do not attribute an imposed decision to whoever forwarded it.

**Offer the open item, never write it.** An imposed decision creates work on
this side -- comply, seek an exemption, escalate -- and that work is what
`/daikenja:project-gaps` can actually audit, because it audits Open items and
never decisions. When the material does not already name that work, offer to
raise it in one line, saying that nobody on this side is on the hook yet and
asking who is. On the propose-then-wait path that line goes in "Questions
before I write". On the same-turn dictated path it goes alongside the written
lines as an offer, exactly like Step 8's follow-up offers: the dictated
decision still lands in that turn, and the open item is a separate write
needing its own yes. Writing the item unasked would be inventing an entry,
which the hard rules forbid -- and asking about it is not a reason to hold back
the entry the user dictated.

## Record a relationship only where the source says so

Two relationships beyond supersession are recorded, as body markers on the
**constrained** entry only: `Blocked by <id>.` and `Contradicts <id>.`, per
`ledger-format.md` § Relationships between entries. The entry they name gains
nothing -- do not edit it to mark the other side, and do not raise a second
Changelog verb for it.

**Write one only when the material states it.** "We can't start this until the
exemption criteria are published" is a block. Two entries that merely look
related to you are not, however obvious the graph seems -- inferring one
produces a relationship nobody agreed to, and the no-invention rule outranks a
richer record. When the material hints at a relationship without stating it,
that is a line in "Questions before I write".

Three more rules fall out of that:

- **The ID must resolve.** A marker naming an entry this ledger does not have
  is a broken reference the moment it is written. Name the ID in the proposal
  if you cannot resolve it, and do not write the marker until it is settled.
- **Adding a marker to an entry already written is an ordinary edit**, with its
  own `~D-nnn` or `~O-nnn` Changelog verb. There is no separate verb for a
  relationship, because there is no separate operation -- the body changed.
- **Settling one end never rewrites the other.** Resolving `O-007` does not
  strip `Blocked by O-007.` from `O-008`. Removing a marker is an edit the user
  asks for, like any other.

## Record a source

A source -- a document this project is tracked from -- goes in the
`## Sources` section as a head line plus indented field lines, per
`ledger-format.md` § Section: Sources. Everything general is unchanged: the
next `S-nnn` comes from the highest ever used in that section plus the
Changelog, the write needs a dictation or an approval, and the Changelog line
names it (`+S-nnn`, `~S-nnn`, `-S-nnn` -- never `resolved` or `superseded`).

- **Write only the fields the material supplies.** An absent field means
  unknown and stays absent. Never fetch the target to fill `modified:` in --
  reading what a source's system reports is `/daikenja:project-sources`'s job,
  and a refresh comes back through this skill with the values already
  established.
- **`modified:` and `read:` move together**, per the contract: they record
  what the system reported when the source was last read, and when that was.
  Neither is updated unless the source was actually read -- by the user, or
  shown to them in a `project-sources` run -- and neither is ever today's date
  by default.
- **When the ledger has no `## Sources` heading**, add it directly above
  `## Changelog` as part of the same write, and say so in the proposal (or,
  on the same-turn path, in the confirmation). The heading is never added on
  its own.
- **A dictated source takes the same-turn path** under the same four
  conditions as any entry: the fields are the user's own statement, nothing is
  fetched, and the operation is byte-determined.
- **The duplicate check covers sources too**, in `SKILL.md` § Check for
  duplicates first. The same target already recorded as a source is an edit to
  that `S-nnn`, not a second source. A context link with the same target is
  *not* a duplicate -- the two sections record different things, and nothing
  migrates a link into a source unless the user asks for the pair of writes.

## Backfilling an existing project

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

## A meeting date handed over by `meeting-review`

A run entered via `project-log via meeting-review` carries the meeting's own
date in the handoff, or states that the transcript never gave one. Treat a
handed-over meeting date exactly like a date the user supplied directly: it is
the entry's date field for everything this run writes, not today's date
pulled from the environment. This is not the backfill path above -- the
writer stays `project-log via meeting-review`, and nothing else about
backfilling applies -- but the reason is the same one: the date field means
when the thing happened, and a meeting reviewed after the fact is exactly the
case where that differs from today.

**No meeting date was handed over** is treated as an entry whose date cannot
be established, per the failure case below: ask for it, and an approximation
is a real answer, written with the `Approximate date.` marker. Never invent
one and never fall back to today.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, then continue on the defaults (`.daikenja/ledger.md`, owner `@unassigned` unless the user names one). Do not stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| A named project key matches no entry | **Stop.** Name the key, list the registered keys, and write nothing. Never fall back to directory matching. |
| A named project key matches an entry that has paths | **Refuse.** Name the key and say logging against it means running from one of its own directories. Never fall back to directory matching -- the named key is decisive. |
| A named project key matches a pathless entry whose `ledger:` is relative or absent | **Stop.** Name the key and say it has no path and no absolute ledger, so it has no location. Never invent one. |
| Ledger missing and the directory it would be created in is the home directory or `~/.claude` | **Stop.** Refuse to scaffold. Name the path and say why. Unconditional -- a matching `projects:` entry does not license it, and neither does a key-resolved pathless entry whose `ledger:` lands there. |
| Ledger missing and the directory it would be created in is neither a VCS root nor already has `.daikenja/` | One question, naming the absolute path, before scaffolding. Wait for yes before continuing. Skipped when the project is already registered -- which a key-resolved pathless entry always is. |
| Project unregistered | One line naming `/daikenja:setup-project`, per Step 2, then carry on with the ledger. |
| Ledger path unreadable or not writable | **Stop.** Name the path and the error. Do not fall back to another location and do not write the entries somewhere else. |
| Ledger missing one of the four original H2 sections | **Stop.** Name the missing section. Offer to add the empty heading as its own approved write. Do not write entries into a file whose shape you had to guess. Report any other defect already seen while reading the whole ledger alongside the stop -- the run still writes nothing. |
| Ledger has no `## Sources` heading and the run records a source | Not a missing section -- the heading is optional until the first source. Add it directly above `## Changelog` as part of the same write, and say so. |
| A line inside a section does not match the grammar | Report it -- name the line and what is wrong -- then continue with the rest. A line indented two or more spaces with no list marker is a continuation, not an error. |
| A Changelog ID resolves to no entry | One line saying so, then continue. Somebody deleted an entry by hand. Do not rewrite the Changelog. |
| Supersession marked on only one of the two entries | Report the mismatch, naming both IDs. The tail is authoritative. Do not repair it as a side effect of another write. |
| A relationship the material implies but never states | One line in "Questions before I write" naming both entries. Never write the marker on your own reading of the material. |
| A `Blocked by` or `Contradicts` the user asks for, naming an ID this ledger does not have | Do not write it. Name the ID in the proposal and ask which entry was meant. A marker written against a missing ID is a broken reference from the moment it lands. |
| An existing entry already carries a marker naming a missing ID | Report it -- which entry, which ID -- then continue with the write, per `ledger-format.md` § Reading rules, rule 6. Repairing it is a separate write with its own approval. |
| The material does not settle whether a decision was imposed or made here | Ask, in one line in the proposal. Never infer it from which team's document the material came out of. |
| An entry's date cannot be established | Ask for it. An approximation is a real answer and is written with the `Approximate date.` marker. Never invent one, and never fall back to today. If the user cannot approximate it, drop that entry and say so. |
| An owner handle appears neither in this ledger nor in `personas.md` | One line in the proposal naming the handle, and the near miss if there is one. Never a block, never a rewrite of the handle. |
| `personas` is not configured, or its local file is missing | Check the ledger alone, with one notice saying the comparison was narrower for it. Not an error -- the file is optional prose, not a roster. |
| `personas` is a `drive:` pointer that does not resolve, or reads back empty | **Stop** before writing, per `config-resolution.md` § Failure behavior. Show the lines that would have been written so the user keeps them, say nothing was written, and never fall back to a local file. Reached only when a run has a handle this ledger does not already know. |
| Nothing in the material is worth logging | Say so and write nothing. An empty ledger is better than a padded one. |

## What this skill does not do

- It does not summarize a thread for reading. That is `/daikenja:thread`.
- It does not report what changed since last time. That is
  `/daikenja:project-catchup`.
- It does not check whether a source moved, and it never fetches a source's
  target. That is `/daikenja:project-sources`, which reads and reports --
  and, when the user records a refresh, writes it through this skill.
- It does not write `daikenja.yaml`. `/daikenja:setup-user` owns the `profile:`
  block, `/daikenja:setup-project` owns a project's `projects:` entry, and
  `last_checkpoint` belongs to `project-catchup`.
- It does not archive, prune or trim anything on a schedule. Old resolved items
  stay until a human asks for them to go.
- It does not write `personas.md`. It reads that file to check a handle and may
  offer `/daikenja:remember-persona`, which owns every content write to it.
- It does not validate an owner handle. There is no list of legal owners, no
  rejection and no correction -- only the notice in Step 5.
- It does not build a relationship graph. It writes the markers the material
  states, on one entry each, and never sweeps the ledger looking for entries
  that ought to be linked or for markers that ought to be retired now that
  what they name is settled.
