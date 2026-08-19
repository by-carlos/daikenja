---
name: meeting-review
description: Turns a meeting transcript into proposed ledger entries -- decisions actually made, action items with owners and dates, and questions left unresolved. Use when the user says "review this meeting", "what came out of this call", "turn this transcript into actions", or pastes a transcript, meeting notes or a recording link and asks what was decided or who owes what. This skill writes nothing itself. It classifies, then hands the entries to the /daikenja:project-log skill, which shows the exact lines and waits for approval. Not for a chat thread (that is /daikenja:thread) and not for coaching on how the user handled the meeting (that is /daikenja:self-review).
metadata:
  owner: Carlos
  version: 1
  writes-through: project-log
---

# Meeting review

A transcript goes in. What was actually settled, who owes what, and what is
still open comes out. The ledger write goes through `project-log`.

## Hard rules

**Never write the ledger.** `project-log` is the only skill that writes ledger
content. This one classifies and hands over. The Changelog then records the
writer as `project-log via meeting-review`.

**Never promote a suggestion to a decision.** A meeting is full of half-formed
ideas. Something is settled when it was closed out loud and nobody objected.
Everything else is discussion, and discussion does not go in the ledger.

**Never invent an owner.** An action item is owned by the person who accepted
it, or who was assigned it and did not push back. Nobody else. "We should
probably do X" has no owner and usually is not an action item at all.

**Never characterize how people behaved.** Report positions and quotes, not
fault. Who was unprepared, who talked over whom, and who is blocking progress
are not this skill's output.

**Carry an anchor for every candidate.** Each thing you propose keeps the
speaker and a short quote. When the user challenges a call -- and they will --
you defend it from the anchor, not from a second read of the transcript.

## Step 1: get the transcript

- **A file path was given.** Read the whole file, in order.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **A link was given.** Fetch it with whatever tool is connected for that source
  (a meeting tool, a doc, a web page). Use the live content, not the link text.
- **Nothing was given.** Ask for a paste, a path or a link. Do not search for it
  and do not guess which meeting is meant.

If a fetch or a read fails, say what failed in one line and ask for a paste.
Never guess at the content of a meeting you could not read.

If a credential, token, connection string or password appears in the transcript,
say so in one line and never copy it forward. That is a security matter, not a
privacy one. Ordinary workplace content -- names, roles, disagreements,
performance talk -- is the normal subject matter of a meeting the user attended,
and gets handled like anything else.

## Step 2: reduce it in two passes

Transcripts are long and messy. Speaker labels vary, the same point gets made
three times, and side conversations interleave. Two passes handle that without
losing attribution.

**Pass 1 -- walk the transcript in order and collect candidates.** Work through
it in chunks. From each chunk, write down only the moments that might matter,
each as one line carrying the speaker, a short quote and where it sits (a
timestamp or a line number). Nothing else survives the pass.

**Pass 2 -- work on the candidate list, not on the transcript.** Merge repeats,
drop the side conversation, and classify what is left.

**Never summarize the transcript into prose and then classify from the
summary.** The summary drops the speaker and the wording, which are the two
things you need to tell a decision from a suggestion.

Handling the mess:

- **The same point made three times** is one candidate. Anchor it to the turn
  where it was settled, not to the first time it came up. If it was never
  settled, anchor it to the clearest statement of it.
- **Speaker labels vary.** "Priya Nair", "priya" and "P" in one transcript are
  one person. Normalize to one lowercase token. If two labels might be two
  different people, keep them separate and ask. Never merge two people.
- **Side conversations, small talk and tool noise** ("you're on mute", "can you
  see my screen") are dropped in pass 2 and never reported.
- **Garbled or inaudible passages** are ambiguous, not blank. Do not reconstruct
  what was probably said. If a candidate depends on a garbled line, say so.

## Step 3: classify

Getting this wrong pollutes the ledger, and the ledger is what every other
Daikenja skill reads.

**A decision** was settled in the meeting. The tell is an explicit close --
"ok, that's the call", "agreed", "we're doing it that way" -- from someone with
standing, with no objection after it. Silence following a proposal is not
agreement. A decision the meeting only *revisited* is not a new decision.

**An action item** is a concrete task with an owner. The owner accepted it, or
was assigned it in the room and did not push back. Keep the date if one was
said, absolute, never relative.

**An unowned action item** is a concrete task that nobody picked up. It is still
a real open item. The owner is `@unassigned`, written out. That is exactly what
`project-gaps` looks for.

**An open question** was raised and not answered by the end of the meeting.

**Discussion** is everything else -- a proposal nobody agreed to, a parked idea,
thinking out loud, "we should probably" with no owner and no shape. It is not an
entry. Report it separately so the user can see you saw it, and log it only if
they say it is a real open question.

When you cannot tell, ask. One line, one question. Do not resolve the ambiguity
yourself and do not log both readings.

Where these land in the ledger: decisions go to the Decisions section, action
items and open questions both go to Open items. `project-log` owns the line
shape, the IDs and the dates. See `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md`
if you need the detail, and never format entries yourself.

## Step 4: attribute

The owner is `@` plus one lowercase token, no spaces, taken from the speaker
label in the transcript (`Priya Nair` becomes `@priya`).

- A person who accepted a task owns it.
- What the user says is theirs is theirs. Use the first token of `profile.name`
  from `~/.claude/daikenja/daikenja.yaml`.
- Nobody identifiable means `@unassigned`.

**A name that is not in `personas.md` is normal, not an error.** That file is
optional prose that tells you who someone is. It is not a roster, and a person
missing from it did not stop attending meetings. Use the transcript's own label,
and never invent a role, a team or a handle for someone you do not know. If the
transcript names people the config does not cover, note it once at the end of
the report, in one line, and carry on.

`personas.md` here means whatever `profile.personas` resolves to -- a local file
or a Google Drive file, per `config-contract.md` § Resolving `writing_style` and
`personas`. Nothing in this skill changes with the form of the pointer except
what happens when it fails.

If a local `personas` pointer does not resolve, or `daikenja.yaml` is missing
entirely, that is one notice line and the review still runs. Neither is needed
to read a transcript. A `drive:` pointer that does not resolve or reads back
empty stops the run instead, per `config-contract.md` § Failure behavior.

## Step 5: report

Report first, log second. The user often wants only the report. The shape
below follows `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- read it
before writing the reply; `profile.tone` scales any narration around the
sections, never what is in them.

```
Meeting: <what it was, when, and roughly how long or how many turns>
Speakers: <labels as they appear, normalized>

Decisions
1. <what was settled> -- <who closed it> ("<short quote>")

Action items
1. <the task> -- @owner, due <YYYY-MM-DD or "no date given"> ("<short quote>")

Open questions
1. <the question> -- raised by <who>, not answered

Discussed, not settled
- <the idea> -- <who> proposed it, nobody agreed

Notes
- <anything you deliberately did not log, and why, one line each>
```

Drop a section that is empty rather than printing it with nothing under it, and
say in one line what came up empty ("nothing was settled in this meeting").

`Notes` is where the judgment calls go, one line each, so the user can overrule
any of them. A decision the meeting only restated, a point lost to a garbled
passage, a name the config does not cover, a missing `daikenja.yaml` -- all of
it lands here rather than being dropped silently or padded into a section it
does not belong in.

Quote sparingly and only where the wording carries the weight. Keep each line to
one idea.

**Decisions, action items and open questions are not capped.** Dropping a real
decision is the failure this skill exists to prevent. **Discussion is capped at
5**, listed by one-line title, matching the parked treatment `doc-review` and
`self-review` use. If there are more, name the count.

## Step 6: hand off to `project-log`

Close the report with the offer, and stop:

```
Log these to the ledger? I will run /daikenja:project-log with the entries
above. It shows the exact lines and waits for your approval before anything
is written.
```

On a go-ahead, run `/daikenja:project-log` and give it the classified entries,
their owners and their anchors. From there `project-log` does its own job --
resolving the project and the ledger, allocating IDs, checking for
duplicates, showing the exact lines, waiting for approval, and writing. The
Changelog writer is `project-log via meeting-review`.

Do not duplicate any of that here. Do not resolve the ledger path, do not
allocate IDs, do not format entry lines, and do not ask for approval on
`project-log`'s behalf. If the project is unregistered or the ledger does not
exist yet, `project-log` handles it.

If the user declines, write nothing and say nothing was written. The report
stands on its own.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| Nothing given | Ask for a paste, a path or a link. Do not guess which meeting is meant. |
| Fetch or read fails | Say what failed, ask for a paste. Never review a calendar title in place of a transcript. |
| Transcript is very long | Two passes per Step 2. Read all of it. Never sample or skip sections silently. |
| Transcript has no speaker labels | Say so. Extract only what is unambiguous, attribute the rest `@unassigned`, and never guess who spoke. |
| Garbled or inaudible passages | Treat as ambiguous. Do not reconstruct. Say which candidate is affected. |
| Two labels might be the same person | Keep them separate and ask. Never merge two people. |
| A name is not in `personas.md` | Not an error. Use the transcript's label and note it once at the end. |
| The `personas` pointer does not resolve, or `daikenja.yaml` is missing | One notice, then continue. Neither is needed to read a transcript. |
| Nothing was settled | Say so and propose nothing. A meeting with no decisions is a normal meeting. |
| User asks you to write the ledger directly | Decline per the hard rule. Run `/daikenja:project-log`. |
| User asks who was at fault or how someone performed | Decline. Report positions and quotes only. `/daikenja:self-review` coaches the user on their own moves, nobody else's. |

## What this skill does not do

- It does not summarize a Slack or email thread. That is `/daikenja:thread`.
- It does not write the ledger. That is `/daikenja:project-log`, which this
  skill runs.
- It does not draft the follow-up message. That is `/daikenja:compose`.
- It does not review how the user handled the meeting. That is
  `/daikenja:self-review`.
- It does not report what changed since last time. That is
  `/daikenja:project-catchup`.
