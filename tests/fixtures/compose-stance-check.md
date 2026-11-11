Synthetic inputs for `compose`'s opt-in stance check and for `learn-voice`
carrying its lines across. Invented people and project (`tempest`). Not real
work content.

Depends on: compose "Step 6c: stance fit (opt-in)", compose "Output format", learn-voice "Step 7: write"

## The writing-style file

Point `profile.writing_style` at a scratch copy of this file for every walk
except Walk 6, which uses the same file with the first line deleted.

```markdown
stance-check: on

# Writing style

## Tone

Short sentences. No greeting in chat.

## Role and stance

- What I own or decide: the tempest release schedule and the team's on-call rota.
- What is usually the reader's to decide: the platform budget, hiring, and the data team's roadmap.
```

The sender is rimuru, tempest's team lead. The readers are shuna (owns the
platform budget) and geld (leads the data team).

## Walk 1 -- asking permission for something the sender owns

To: #tempest-eng
"Hi all, would it be OK if I moved the tempest release to Thursday? The
migration needs one more day of testing."

Expected: the message is rewritten with the question kept as a question.
`Comment` has one `stance fit` line naming the opening sentence, saying the
sender owns the release schedule, and suggesting a reframe that states the
move and invites objections. The reframe adds no date, owner or deadline the
draft does not state.

## Walk 2 -- deciding what is the reader's

To: shuna
"We are cutting the observability line from next quarter's platform budget.
Let me know if you have questions."

Expected: the decision stays stated as a decision in the message. `Comment`
flags it: the platform budget is the reader's, and the reframe asks shuna to
decide.

## Walk 3 -- apologising for a fault the sender does not hold

To: geld
"So sorry the data team's export job failed overnight and broke your
dashboards. I will keep an eye on it."

Expected: the apology stays in the message. `Comment` flags that the export
job is the data team's, and the reframe acknowledges the impact without
taking the fault.

## Walk 4 -- complaining where an expectation fits

To: #tempest-eng
"Nobody ever updates the on-call handover doc. I keep finding out about
incidents from the dashboard."

Expected: Step 3 already removes the venting; the stance stays a complaint.
`Comment` flags it: the sender owns the on-call rota, and the reframe states
the expectation ("Please update the handover doc at the end of each shift").

## Walk 5 -- a draft that fits

To: shuna
"Could you decide by Friday 2026-11-20 whether the observability line stays
in next quarter's platform budget? I can bring the usage numbers to Monday's
review."

Expected: no `stance fit` line. The request goes to the budget's owner, so
nothing matches.

## Walk 6 -- the switch absent

Delete the `stance-check: on` line from the file, then run Walk 1 again.

Expected: no `stance fit` line and no mention of the check. The output is the
same as before this change: the `## Role and stance` section alone turns
nothing on.

## Walk 7 -- with an inline goal

To: shuna
"We are cutting the observability line from next quarter's platform budget.
-- goal: get shuna's decision on the observability line by Friday"

Expected: Step 6b flags `goal fit` (the draft states a decision where the
goal asks for one, and names no date) and Step 6c flags `stance fit` (the
budget is shuna's; the goal confirms the decision is the reader's). Both are
flagged, neither is filled in, and the stance is not changed.

## Walk 8 -- `learn-voice` keeps the lines

Run `/daikenja:learn-voice` with `profile.writing_style` pointed at a scratch
copy of the file above and `learn-voice-samples.md` as the samples, against
the scratch copy rather than a real file.

Expected: the written file has the `stance-check: on` line and the
`## Role and stance` section byte for byte as above, the report says they were
carried across unchanged, and neither is reworded or listed as a section the
new file lacks.
