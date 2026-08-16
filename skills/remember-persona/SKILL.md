---
name: remember-persona
description: Records what the user says about a person they write to, in their own personas file at ~/.claude/daikenja/personas.md, so later messages are written for that reader. Use when the user says "remember that S challenges every technical claim", "log this persona", "note that D is the one who cares about cost", "remember how M likes to be written to", or describes a recipient while drafting and wants that kept. Also the skill other Daikenja skills route through when a description of a person comes up mid-draft. This is the only skill that writes persona content -- every other Daikenja skill reads it. It records only what the user actually said and never infers a character study. Not for a project decision or an open item (that is /daikenja:log) and not for creating the file in the first place (that is /daikenja:setup-user).
metadata:
  owner: Carlos
  version: 1
  writes: ~/.claude/daikenja/personas.md
---

# Remember persona

`personas.md` is the user's own prose about the people they write to. Other
skills read it so a note to a director does not read like a note to a vendor.
This skill is the only thing that writes content into it.

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

**Never create the file.** Creating `personas.md` belongs to `setup-user`. This
skill writes content into a file that already exists and does nothing else to
it.

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

## Step 2: resolve the file

Follow `config-contract.md` § Resolution order.

1. Read `~/.claude/daikenja/daikenja.yaml`. Malformed YAML is fatal -- report
   the first line that does not parse and stop. Never rewrite a file you cannot
   parse.
2. Resolve `profile.personas`, relative to `daikenja.yaml`'s own directory. An
   absolute path is also accepted. Default `~/.claude/daikenja/personas.md`.

**The file must already exist.** If it does not, stop and name the skill that
creates it:

```
No personas.md at <path>. /daikenja:setup-user creates it from the template.
Nothing was written.
```

When this skill was **routed to from another skill**, that notice goes back to
the caller as one line and the caller carries on with its own job. A missing
personas file never blocks a draft.

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

## Step 4: build the entry

Use the shape the template already establishes -- an H2 with the person's name,
then short prose under bold field labels:

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

**New person, no existing entry.** Append the section at the end of the file,
after the last existing content. Write it without asking. Touch nothing else --
no reordering, no reformatting, no tidying, and no normalizing a line a human
wrote by hand.

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
| `personas.md` does not exist | **Stop.** One line naming the path and `/daikenja:setup-user`. Nothing written. Routed callers get the line and carry on. |
| `daikenja.yaml` absent | One notice, then continue on the default path (`~/.claude/daikenja/personas.md`). Do not stop. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| `profile.personas` does not resolve | Treat as an absent key, per the contract. One notice naming the path, then fall back to the default path. |
| The file is not writable | **Stop.** Name the path and the error. Never write the entry somewhere else. |
| A person is named with nothing said about them | Write nothing. One line saying a name alone is not a persona. |
| The description is evaluative ("he is useless") | Record the behaviour underneath it if the user stated one, and say in one line what you wrote instead. If there is no behaviour under it, write nothing and ask what they do. |
| The person already has an entry | Propose, never write silently. See Step 5. |
| The file still holds the shipped template placeholder | Leave it alone. Append below it and note it once in the report. |
| The user asks for an entry to be deleted | Show the exact section and wait for approval, like any other change to existing content. |

## What this skill does not do

- It does not read `personas.md` on anyone's behalf. The skills that need a
  persona read it themselves.
- It does not create `personas.md`. That is `/daikenja:setup-user`, and its
  create-if-absent rule is untouched by this skill.
- It does not write `daikenja.yaml`. That is `/daikenja:setup-user`, except for
  `last_checkpoint`, which `catchup` owns.
- It does not record project decisions or open items. That is `/daikenja:log`,
  which writes the ledger and never touches this file.
- It does not build a persona by reading past messages, threads or transcripts.
  Only what the user states is recorded.
