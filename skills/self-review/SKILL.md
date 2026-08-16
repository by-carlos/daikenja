---
name: self-review
description: Reviews how the user themselves handled a thread they took part in, and gives private, direct, evidence-backed coaching on their own moves. Use when the user says "how did I handle that", "review my messages in this thread", "what could I have done better", "was I out of line", or pastes a thread they participated in and asks for feedback on their part in it. Findings are about the user alone, never about anyone else's failings, and nothing is written, logged or sent. Not a review of a document (that is /daikenja:doc-review), not a review of what a meeting settled (that is /daikenja:meeting-review), and not a pre-send check on a draft message (that is /daikenja:preflight).
metadata:
  owner: Carlos
  version: 1
---

# Self review

Private coaching on one person's moves in a thread they took part in. That
person is the user who invoked this skill, and nobody else.

This is the skill that can do real harm if it is wrong, and the skill whose
whole value disappears if it hedges. Both failure modes are guarded below.

## Hard rules

**The subject is the invoker.** Every finding is about something the invoker
did or did not do. Other people appear only as the situation the invoker was
responding to, described as observable behavior. Never a finding about someone
else's failings, never a judgement of how a colleague performed, and never
fault assigned to a third party. If the honest reading of a thread is that
someone else caused the problem, say what the invoker could still have done and
stop there.

**Evidence must be visible to the invoker.** If the best evidence for a finding
is private to someone else -- a direct message the invoker was not in, a
private assessment, a side channel -- rebuild the finding from sources the
invoker can see, or drop it. Never quote one person's private assessment to
another. A finding you cannot evidence from the invoker's own view does not
ship.

**This skill writes nothing.** It does not draft a reply, does not write the
ledger, does not send anything, and does not produce a message the user could
paste. It reports to the user and stops.

**A finding that cannot survive plain statement does not ship in any mode.** If
it only works when it is wrapped in softeners, it is not a finding yet. Either
state it plainly or drop it.

**Do not invent findings to fill the cap.** A thread the invoker handled well
produces a short report. Three findings is not a quota.

## Step 0: read the shared doc

Read `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` before doing anything. It
is where `tone` and `norms_doc` resolve, and it carries the failure-behavior
table this skill follows. Do not work from memory of it.

## Step 1: get the thread and identify the invoker

- **Text was pasted.** Use it as-is. Do not go looking for more.
- **A file path was given.** Read the whole file, in order.
- **A link was given.** Fetch it with whatever tool is connected for that
  source. Use the live content, not the link text.
- **Nothing was given.** Ask for a paste, a path or a link. Do not search for
  it and do not guess which conversation is meant.

If a fetch or a read fails, say what failed in one line and ask for a paste.
Never review a conversation you could not read.

**Then work out which participant is the invoker.** Take the first token of
`profile.name` from `~/.claude/daikenja/daikenja.yaml` and look for a matching
speaker label. One match means that is the invoker. No match, several matches,
or no config at all means **ask, in one line, which participant they are**. Do
not guess, and do not review the thread until you know. Reviewing the wrong
person is the worst thing this skill can do.

If the invoker turns out not to be a participant, say so and stop. There is
nothing to review. Offer `/daikenja:thread` for a summary instead.

## Step 2: walk the thread and anchor everything

Go through the thread in order, once, and collect the invoker's moves. A move
is anything they did or chose not to do that had an effect -- a message, a
silence, a commitment, an escalation, a decision to answer one question and not
another.

For each move, write down one line carrying:

- the turn (a timestamp, a message number or a permalink),
- a short quote of what the invoker actually wrote,
- what came immediately before it, and what happened after it.

That last part is the evidence for effect, and it is the part most easily lost.
Work from this anchored list from here on. **Never summarize the thread into
prose and then review from the summary** -- the summary drops the wording and
the sequence, which are the two things every finding rests on.

## Step 3: separate intent, content and effect

For each move, hold three things apart before you judge it:

- **Intent.** What the invoker was trying to achieve. Usually legitimate.
- **Content.** Whether what they said was correct on the substance.
- **Effect.** What actually happened next, in the thread, observably.

Being right on substance does not cancel a bad effect. A bad effect does not
make the substance wrong. Most useful findings live exactly in that gap, and
collapsing the three into a single verdict is how coaching turns into scolding.

Intent is inferred, so it is never stated as fact. Where intent is worth
crediting, credit it explicitly and label the finding's confidence accordingly.

## Step 4: build each finding

Every finding has these six parts, in this order. The order is fixed because
the evidence has to come after the claim it supports, not before.

```
<one-line title, stated as the claim>
What happened: <observable behavior only, no cause attribution>
Why it matters: <the impact, from what actually followed>
Intent: <where relevant -- the legitimate goal, credited plainly>
Try instead: <one concrete alternative, specific enough to act on>
Evidence: <quote or link> -- CONFIRMED | PLAUSIBLE
```

Rules per part:

- **Title.** The claim itself, in one line. Not a topic, not a category.
- **What happened.** Only what an observer could see. "You replied 40 minutes
  later with a one-line answer" is observable. "You were dismissive" is a
  conclusion and belongs nowhere in this field.
- **Why it matters.** Impact drawn from what followed in the thread. If nothing
  followed, say what the reader was left unable to do.
- **Intent.** Include it where the invoker plainly had a legitimate goal, and
  say what it was. Skip the field entirely when there is nothing real to
  credit. Never manufacture a compliment to cushion the finding.
- **Try instead.** One concrete alternative. Not "communicate more clearly".
  When the cause is invisible to you, make it conditional -- "if the delay was
  because you were waiting on the load test, then saying that in one line at
  11:20 would have..." A conditional alternative is honest; a confident guess
  at someone's reasons is not.
- **Evidence, last, with a confidence label.** Use a markdown link wherever a
  permalink exists, otherwise a short quote plus the turn.

**Confidence vocabulary is fixed and has exactly two levels.**

| Label | Means |
|---|---|
| `CONFIRMED` | Backed by a direct quote, a timestamp, or a diff. It is in the thread. |
| `PLAUSIBLE` | Inferred. It reads this way, and it could be wrong. |

There is no third level. Do not write "possibly", "somewhat", "it may be that",
"arguably" or any other hedge outside these two labels. A finding that is not
even `PLAUSIBLE` is not a finding.

## Step 5: communication notes (the conduct review)

Conduct is reviewed best-effort against generally accepted professional norms
for international, multicultural workplaces. The category label in the report
is **communication notes**. Two controls keep it honest.

**The clear-departure threshold.** Flag only what a reasonable colleague would
consider out of line -- contempt, public blame, sarcasm aimed at a person,
dismissing someone's stated constraint, talking past a direct question twice.
Anything borderline is demoted to a style observation in the ordinary findings,
not raised as conduct. When in doubt, demote. Conduct findings are rare by
design.

**Name the norm in one line.** Every conduct finding states the norm it
invokes, plainly, in the finding itself. "Disagreement is with the position,
not with the person" is a norm. "That was unprofessional" is not -- it names no
norm and cannot be argued with.

**Conduct findings are stated plainly in every tone mode.** Softening never
applies to a crossed line. `guided` mode may add scaffolding around a conduct
finding; it may not blunt the statement of it.

## Step 6: order and cap

Ordering is deterministic. Severity tier first, then impact within the tier.

| Tier | What it holds |
|---|---|
| 1 | Conduct findings (communication notes). |
| 2 | Findings where the invoker misled others -- a wrong fact stated confidently, a commitment nobody could keep, an implication left standing that was not true. |
| 3 | Effectiveness and habit findings -- slow, unclear, buried the ask, answered the wrong question, did not close the loop. |

Within a tier, hardest-hitting first, judged by real consequence, not by how
uncomfortable it is to read.

**Cap per run, by tone mode.** The rest are parked.

| Tone | Findings shown |
|---|---|
| `direct` | 5 |
| `standard` | 4 |
| `guided` | 3 |

**The remainder is parked by title.** One line each, title only, under a
`Parked for next time` heading, with the count. No detail, no evidence, no
softening -- a parked finding is a promise that it is still there, not a
half-delivered version of it. Parked titles are the same titles they would have
had if they had shipped.

**"What worked" is chronological**, not ranked, and contains only real items.
An empty "what worked" section is omitted rather than padded. Inventing one is
a lie about the thread, and the user will notice.

## Step 7: tone modes

`profile.tone` from `daikenja.yaml` selects the mode. Default is `standard`.
There is no project-level override for tone.

**What the mode changes, and nothing else.**

| | `direct` | `standard` | `guided` |
|---|---|---|---|
| Verdict placement | First line, before anything else. | After a one-line frame of the thread. | Last, after the reasoning has been walked through. |
| Scaffolding | None. Findings only. | A one-line frame, and a closing line. | Frame, why each finding is being raised, and a closing "what to carry into the next one". |
| Findings shown | 5 | 4 | 3 |
| "What worked" | After the findings, one line each. | Before the findings. | Before the findings, with a line on why each mattered. |

**Invariants across all three modes.** These do not vary, ever.

- **The same claim set.** Every finding appears in every mode, either in full
  or parked by title. The cap changes how many are developed, never how many
  were made. No mode makes a finding disappear.
- **The same tier order.** The cap always takes from the bottom of the ordered
  list, so no mode drops a harder finding and keeps a softer one.
- For any finding shown in full, **the same facts, the same evidence links and
  quotes, and the same confidence label**, unchanged.
- "What worked" contains only real items in every mode.
- Conduct findings stated plainly in every mode.

**The test that decides whether a mode is implemented correctly:** a reader of
any one mode can name every finding that was made, and no reader gets a weaker
version of a finding they were shown. Depth varies with the cap; the claim set
does not. If `guided` leaves someone unable to state what they actually did
wrong, `guided` is broken, not gentle.

## Step 8: ROLE CHECK (off by default)

This section is off unless `norms_doc` is configured.

1. Resolve `norms_doc` -- the matched project's key first, then `profile`'s.
2. **Absent at both levels.** Skip the section silently. No notice, no
   explanation, no mention that it exists. This is the documented default, not
   a degradation.
3. **Configured but it does not resolve or cannot be fetched.** One notice line
   naming the path, then skip the section and carry on with the rest of the
   review.
4. **Configured and readable.** Read it. Close the report with a per-duty
   verdict against what that document actually says -- one line per duty it
   names, each anchored to a quote or a heading from the document.

Anchor every ROLE CHECK line to the document. Never a verdict against a duty
you inferred, a role you assumed, or general expectations for someone's job
title. If the document does not name a duty, there is no verdict on it.

## Step 9: report

One canonical shape, arranged per the tone table in Step 7.

```
Reviewed: <what the thread was, how many turns, over what period>
You in this thread: <the speaker label matched to the invoker>

What worked
- <real item, chronological>

Findings (<n> of <total>, hardest first)

1. [communication notes] <title>
   What happened: ...
   Why it matters: ...
   Norm: ...
   Try instead: ...
   Evidence: "<quote>" (2026-08-14 11:40) -- CONFIRMED

2. <title>
   What happened: ...
   Why it matters: ...
   Intent: ...
   Try instead: ...
   Evidence: [thread link](https://example.com/t/1) -- PLAUSIBLE

Parked for next time (<n>)
- <title only>

ROLE CHECK
- <duty, quoted from the norms document> -- <verdict in one line>
```

Drop any section that is genuinely empty rather than printing an empty heading.
Say in one line when the findings list itself is empty -- "nothing on this
thread meets the bar for a finding" is a real and reportable outcome.

Number the findings. Users refer back to them by number when they argue, and
they should argue.

## Step 10: defend, do not retract

The user will challenge findings. That is the point of anchoring everything in
Step 2.

- **Challenged on the facts.** Answer from the anchor -- the quote and the
  turn. If the anchor does not support the finding, withdraw it and say which
  one and why. That is a correction, not a concession.
- **Challenged on the judgement.** Restate the finding once, plainly, with the
  norm or the impact it rests on. Then let it stand. Do not argue it twice.
- **Challenged emotionally.** Do not re-rank the findings, do not soften them,
  and do not add a compliment that was not in "what worked". Offer to switch
  tone mode, which changes delivery and not facts.

Never quietly drop a finding because it was unwelcome. Never upgrade a
`PLAUSIBLE` to `CONFIRMED` under pressure.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself.

| Situation | What to do |
|---|---|
| Nothing given | Ask for a paste, a path or a link. Do not guess which conversation is meant. |
| Fetch or read fails | Say what failed, ask for a paste. Never review a thread you could not read. |
| Which participant is the invoker is unclear | Ask, in one line. Never guess. This is a hard stop. |
| The invoker is not a participant | Say so and stop. Offer `/daikenja:thread` instead. |
| `daikenja.yaml` absent | One notice, tone defaults to `standard`, ROLE CHECK stays off. Ask who the invoker is, since there is no `profile.name` to match. |
| `profile.tone` missing or not one of the three | Use `standard` and say so in one line. |
| `norms_doc` absent | Not an error. Skip ROLE CHECK silently. |
| `norms_doc` configured but unreachable | One notice naming the path, skip ROLE CHECK, continue. |
| Thread has no speaker labels | Say so and stop. Without attribution there is no way to know which moves are the invoker's. |
| Best evidence is private to someone else | Rebuild it from what the invoker can see, or drop the finding. Never quote it. |
| Thread is very long | Read all of it, in order. Never sample or skip turns silently. |
| A colleague clearly behaved badly | Not a finding. Describe it only as the situation the invoker faced, and review what the invoker did about it. |
| User asks for a review of someone else | Decline in one line. This skill reviews the invoker only. |
| User asks you to draft the follow-up | That is `/daikenja:compose`. This skill writes nothing. |
| Fewer than three findings exist | Report what there is. Do not pad to the cap. |

## What this skill does not do

- It does not review anyone but the invoker.
- It does not summarize the thread. That is `/daikenja:thread`.
- It does not extract decisions or action items. That is `/daikenja:meeting-review`
  for a transcript, `/daikenja:project-log` for a ledger write.
- It does not review a document. That is `/daikenja:doc-review`.
- It does not check a draft before sending. That is `/daikenja:preflight`.
- It does not draft or rewrite a message. That is `/daikenja:compose`.
- It does not write, log or send anything.
