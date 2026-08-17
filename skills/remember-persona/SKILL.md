---
name: remember-persona
description: Records what the user says about a person they write to, in their own personas file (by default ~/.claude/daikenja/personas.md, or a Google Drive file if that is where they keep it), so later messages are written for that reader. Use when the user says "remember that S challenges every technical claim", "log this persona", "note that D is the one who cares about cost", "remember how M likes to be written to", or describes a recipient while drafting and wants that kept. Also the skill other Daikenja skills route through when a description of a person comes up mid-draft. This is the only skill that writes persona content -- every other Daikenja skill reads it, and it scaffolds personas.md from the template on first use if it is not already there. It records only what the user actually said and never infers a character study. Not for a project decision or an open item (that is /daikenja:project-log) and not for the rest of first-time setup, which this skill does not perform (that is /daikenja:setup-user).
metadata:
  owner: Carlos
  version: 5
  writes: whatever profile.personas resolves to (default ~/.claude/daikenja/personas.md)
---

# Remember persona

`personas.md` is the user's own prose about the people they write to. Other
skills read it so a note to a director does not read like a note to a vendor.
This skill is the only thing that writes content into it.

Throughout this skill, `personas.md` means whatever `profile.personas` resolves
to -- a local file by default, or a Google Drive file. Step 2 and Step 5 are
where the two differ; everything else is the same work on the same prose.

## Hard rules

**Only what the user said.** Every word written comes from what the user
actually stated. Never infer a trait from a draft, from a thread, from a name,
or from a role. If a description is thin, the entry is thin. A one-line entry
that is true beats a paragraph that is half guessed.

**Behavioural, never evaluative.** Record what the person *does*, not what they
are. "Challenges technical claims" is a lens someone can write toward. "Is
obstructive" is a verdict, it is worse reviewer input, and this file is a
liability if it is ever read over the user's shoulder.

**Silent means append-only, and only for new people.** Adding a section for
someone with no entry is additive and reversible, so it is written without
asking and reported after. Changing prose the user wrote by hand is a different
act -- it is **proposed**, shown in full, and written only on approval.

**Scaffold, never hand-build.** If the personas file does not exist when this
skill has an entry to write, copy `${CLAUDE_PLUGIN_ROOT}/templates/personas.md`
verbatim and write the entry into the copy, the same way `project-log`
scaffolds a missing ledger. `setup-user`'s create-if-absent rule is untouched:
it still copies the same template on its own run, and copying the template
twice is idempotent. What changes is that this skill no longer stops and waits
for `setup-user` to have run first.

**Scaffolding covers local files only, and a write is never redirected.** When
`profile.personas` points at a Google Drive file, this skill writes to that file
and never creates one -- `setup-user` is the only skill that creates a Drive
file, per `config-contract.md` § Who writes what. If a Drive pointer does not
resolve, write nothing, say so, and keep the entry in the conversation so the
user can retry once the file is reachable. Never fall back to the local default:
that would split the user's notes across two stores without telling them.

**Never write the personas file from any other skill.** A skill that needs an
entry recorded runs this one.

## Step 0: read the contract

Read `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` before writing anything --
how `profile.personas` resolves, and the failure-behavior table. Do not work
from memory of it. If it and this skill ever disagree, the contract wins and you
say so.

## Step 1: get the material

- **The user described someone.** That description is the material. Use it.
- **Another skill routed a description here.** Same thing. The description came
  from what the user said while drafting, not from the draft's own contents.
- **A person is named with nothing said about them.** There is nothing to
  record. Say so in one line and write nothing. A name is not a persona.
- **Nothing was given.** Ask who, and what about them. Do not go reading threads
  or drafts to assemble a picture of somebody.

Never mine a draft, a thread or a transcript for traits. The user stating "M
challenges every technical claim" is material. M having challenged a claim in a
pasted thread is not.

**Material that says it is synthetic is not material.** Acceptance fixtures,
worked examples and anything else that announces itself as invented describe
people who do not exist, and this file is a record of real colleagues. Write
nothing, say so in one line, and do not ask the user to confirm -- the file said
it plainly enough:

```
That description comes from a test fixture, so I have not recorded it.
```

## Step 2: resolve the file

Follow `config-contract.md` § Resolution order.

1. Read `~/.claude/daikenja/daikenja.yaml`. Malformed YAML is fatal -- report
   the first line that does not parse and stop. Never rewrite a file you cannot
   parse.
2. Resolve `profile.personas` per `config-contract.md` § Resolving
   `writing_style` and `personas`. It may name a local file or a Drive file.
   Default `~/.claude/daikenja/personas.md`.

**A Drive pointer that resolves** is read with the connector's file-download
tool -- never the natural-language extraction tool -- and everything from Step 3
on is the same work on the same prose. Step 5 is where the write itself differs.

**A Drive pointer that does not resolve** ends the run: one notice naming the
file and the reason, the entry shown in full so the user still has it, and
nothing written anywhere. **A download that comes back empty is this same
case**, not an empty personas file. An empty read cannot be told apart from a
file with no entries, and writing on that assumption would replace the user's
prose with a file containing one persona:

```
Your personas are in Drive as <name>, and I cannot read it right now
(<reason>). I have not written anything. Here is the entry, so you can keep it
or ask me again later:
```

**If a local file does not exist, scaffold it.** Say so plainly before doing
anything else, mirroring `project-log` Step 3:

```
No personas.md at <path>. I will create one from the Daikenja template.
```

Create the parent directory if needed, copy
`${CLAUDE_PLUGIN_ROOT}/templates/personas.md` to `<path>` verbatim, and change
nothing else in the template -- the placeholder block stays, per Step 3's rule
for it. Scaffolding is silent and reported the same way an append is (Step 6):
it needs no approval of its own, and the report in Step 6 names both the
scaffold and the entry in the same message.

This never blocks a draft: whether the file already existed or was just
scaffolded, the entry gets written either way. When this skill was **routed to
from another skill**, the scaffold-and-write happens the same way, and the
report goes back to the caller as one line.

## Step 3: read what is already there

Read the whole file before writing.

**Look for an existing entry for this person.** Match on the section heading,
generously -- "Sarah", "Sarah Kaur" and "S" are the same person if the user is
plainly talking about the same person. When you cannot tell, ask rather than
appending a second section for someone who already has one.

**Note whether the shipped template placeholder is still present** -- the
`Delete everything below this line` marker and the `## <Name or group>` example
sections underneath it. If it is, leave it exactly as it is. It is the format
hint for whoever opens the file next, and removing it is not this skill's call.
Mention it once in the report.

Read nothing else out of the file and change nothing you were not asked to.

**What you read here stays here.** Reading the whole file is necessary to place
an entry and to spot an existing one. Repeating what it says about anyone else
is not: no summarising other people's entries, no listing who is already in
there, no reasoning out loud about how they compare. These are the user's
private notes on real colleagues, and they have a way of being read over a
shoulder. Say a match exists or does not, and nothing about the neighbours.

## Step 4: build the entry

**Match the format the file already uses.** Read how the existing entries are
written -- the heading level, whether the name carries a role after it, whether
the fields are bold labels or bullets -- and write the new entry the same way.
**The file is the authority on its own format**, and a user who has settled on a
shape has settled it for a reason.

The shape below is the fallback, for a file that has no entries yet to copy:

```markdown
## Sarah

**Who they are.** Director of platform engineering. Signs off on the migration
budget.

**What they want from you.** The decision and what it costs. No project
history.

**How to write to them.** Short. Lead with the ask.

*Recorded by Daikenja on 2026-08-16 from what you said while drafting. Edit or
delete this freely.*
```

**Write only the fields the material supports.** Four labels with two of them
guessed is worse than one label that is true. The template's labels are `Who
they are`, `What they already know`, `What they want from you` and `How to write
to them`; use the ones that fit and drop the rest.

**Relational context goes under `Who they are`** -- "reports to V", "works
closely with K's team". It is not a lens, but it is a fact the user stated and
it matters for how a message lands. It gets no field of its own.

**The provenance line is required on every entry this skill writes.** Writes are
silent, so the file has to say which entries came from Daikenja and when. Get
the date from the environment with `date +%Y-%m-%d` -- the local date, never one
recalled from memory, and never a relative date.

## Step 5: write

**New person, no existing entry.** Append the section **at the end of the
entries, immediately after the last persona section -- not at the end of the
file.** A file may carry trailing sections that have to stay last: standing
drafting rules, notes to self, a template block. Dropping a person underneath
those breaks the file's own structure.

**In Drive, the placement is the same and the write is a replacement.** The
connector cannot update a file's content, so the write follows
`config-contract.md` § Writing replaces the file: download, splice the entry
into the downloaded bytes at the same position, create a new file with the same
name, read it back to confirm, and only then trash the old one. **Never trash
first** -- a create that fails after the old file is gone destroys prose that
cannot be recovered.

**Splice, never regenerate.** What gets written is exactly what was downloaded
plus this one entry. Everything else -- hand-written sections, the template
placeholder, spacing, trailing notes -- is carried across untouched. This skill
already never reformats a local file, and a whole-file replace makes that rule
load-bearing rather than merely polite.

Write it without asking. Touch nothing else -- no reordering, no reformatting,
no tidying, and no normalizing a line a human wrote by hand.

**Existing entry, and the user said something new about them.** Do not write.
Show the exact addition and the exact line it would sit after, and wait:

```
S already has an entry. I would add this under it:

  **How to write to them.** Short. Lead with the ask.

Add it?
```

Approval is the user saying yes in this conversation. Silence is not approval,
and neither is the user replying about something else. Approval of one addition
does not carry to the next.

**Existing entry, and the user is correcting it.** Same as above, and show what
the current text says as well as what it would become. Rewriting the user's own
prose always gets shown in full first.

## Step 6: report

Silent means unannounced beforehand, not invisible. Every write is reported
after it happens, naming the file and showing what landed, so it can be edited
or deleted:

```
Learned: added S to ~/.claude/daikenja/personas.md.

  ## S

  **Who they are.** Director of platform engineering.
  **How to write to them.** Short. Lead with the ask.
```

When the file did not exist and this skill scaffolded it, the report says both
in one message:

```
Created ~/.claude/daikenja/personas.md from the template, then learned: added
S to it.

  ## S

  **Who they are.** Director of platform engineering.
  **How to write to them.** Short. Lead with the ask.
```

When this skill ran inside another skill's work, that report is one line in the
caller's own output rather than a block of its own -- `Learned: added S to
~/.claude/daikenja/personas.md.` The user can open the file to see the entry.

Report the number of entries, not an assessment of them. Do not congratulate the
user on the persona, and do not summarize what you think it means about the
person.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| The personas file does not exist | Scaffold it from the template, then write the entry. One notice naming the path, then continue -- not a stop. Routed callers get the same one-line report. |
| `profile.personas` names a Drive file that resolves | Write to it by replacement, per Step 5. Same prose work as a local file, same report. |
| `profile.personas` names a Drive file that cannot be reached, or whose download is empty | Write nothing, anywhere. One notice naming the file and the reason, then show the entry so the user keeps it. Never create a Drive file and never fall back to the local default. |
| More than one Drive file carries the pointer's name | **Stop.** Name both and say an earlier write was probably interrupted. Never guess which is current -- picking wrong loses whichever entries are in the other one. |
| The Drive replacement fails after the new file was created | The old file is still there and untouched. Say both files now carry the name, name the one just written, and stop. Never trash the old file to tidy up an unverified write. |
| `daikenja.yaml` absent | One notice, then continue on the default path (`~/.claude/daikenja/personas.md`). Do not stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| `profile.personas` names a path that does not resolve | Treat as an absent key, per the contract. One notice naming the path, then fall back to the default path. |
| The file is not writable | **Stop.** Name the path and the error. Never write the entry somewhere else. |
| A person is named with nothing said about them | Write nothing. One line saying a name alone is not a persona. |
| The description came from a fixture or worked example | Write nothing. One line saying it came from a test fixture. Do not ask the user to confirm. |
| The file's entries use a different format from the template | Match the file, not the template. It is the authority on its own format. |
| The file has trailing sections after the entries | Append after the last entry, above those sections. Never at the very end. Placement is the same in Drive, where the whole file is rewritten from the bytes just downloaded, per Step 5. |
| The description is evaluative ("he is useless") | Record the behaviour underneath it if the user stated one, and say in one line what you wrote instead. If there is no behaviour under it, write nothing and ask what they do. |
| The person already has an entry | Propose, never write silently. See Step 5. |
| The file still holds the shipped template placeholder | Leave it alone. Append below it and note it once in the report. |
| The user asks for an entry to be deleted | Show the exact section and wait for approval, like any other change to existing content. |

## What this skill does not do

- It does not read `personas.md` on anyone's behalf. The skills that need a
  persona read it themselves.
- It does not inspect or overwrite `personas.md` when the file already exists.
  Scaffolding only happens on absence, the same test `setup-user` uses, and
  `setup-user`'s own create-if-absent rule is untouched by this skill.
- It does not write `daikenja.yaml`. That is `/daikenja:setup-user`, except for
  `last_checkpoint`, which `project-catchup` owns.
- It does not record project decisions or open items. That is
  `/daikenja:project-log`, which writes the ledger and never touches this file.
- It does not build a persona by reading past messages, threads or transcripts.
  Only what the user states is recorded.
