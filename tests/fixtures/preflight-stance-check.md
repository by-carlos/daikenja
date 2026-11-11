Synthetic inputs for `preflight` running the opt-in stance check. Invented
people and project (`tempest`). Not real work content.

Depends on: preflight "Step 3b: stance fit (opt-in)", preflight "Step 10: report", stance-check.md "How a match is reported"

Run every walk under `claude --plugin-dir .`, with `profile.writing_style`
pointed at a scratch copy of the file below, never a real one.

## The writing-style file

The same file as `compose-stance-check.md`. Walk 2 uses it with the first line
deleted.

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

## Walk 1 -- a mismatching draft, switch on

To: #tempest-eng
"Hi all, would it be OK if I moved the tempest release to Thursday? The
migration needs one more day of testing, and I would rather not ship it
half-checked. Let me know what you think."

Expected: the report carries one `Stance fit` line naming the opening
question, saying the sender owns the release schedule, and suggesting a
reframe that states the move and invites objections, with no date, owner or
deadline the draft does not state. The revised draft still asks the question:
no wording fix turns it into a statement. The line is not in `Needs you` and
the verdict's fact count does not include it. No reviewer finding cites the
stance check.

## Walk 2 -- the same draft, switch absent

Delete the `stance-check: on` line from the scratch file, then run Walk 1
again.

Expected: no `Stance fit` line and no mention of the stance check anywhere in
the report. Every other line is what `preflight` gave for this draft before
the check existed: the `## Role and stance` section alone turns nothing on.

## Walk 3 -- a draft that fits, switch on

To: shuna
"Could you decide by Friday 2026-11-20 whether the observability line stays
in next quarter's platform budget? Usage is down a third since August; I can
bring the numbers to Monday's review."

Expected: no `Stance fit` line. The request goes to the budget's owner, so
nothing matches, and the report says nothing about the check.
