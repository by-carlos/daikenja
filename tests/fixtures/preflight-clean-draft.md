Synthetic drafts for `preflight` acceptance. Invented people and project.
Not real work content.

Neither draft is missing a fact. Every fix either draft needs can be written
using words already on the page, so neither should produce a question.

Draft 1 should return **no findings at all**, which skips cycle 2. It routes the
question by ownership without the phrasing reading as blame -- an earlier version
opened the ask with "You own the migration --" and the tone-sensitive reader
caught it, so the draft was never the clean control it claimed to be.

## Draft 1 -- nothing to find

To: T

"The Beacon staging deploy failed on the 2026-08-15 run. The build log points
at the `region_id` foreign key, and I confirmed it against the 2026-08-14 run,
which passed with the same script.

The constraint is part of your migration, so you are the person to ask -- can
you tell me by Thursday 2026-08-20 whether it is meant to be live yet? I will
hold the deploy until then."

## Draft 2 -- only the wording is wrong

To: T

"Hope the week is going well. As discussed, I wanted to circle back on the
Beacon staging situation, which as you know has been a bit of a moving target
for a while now.

So the deploy failed on the 2026-08-15 run, and having looked at the build log
it points at the `region_id` foreign key, and I did also check it against the
2026-08-14 run which passed on the same script, so it does look like something
changed between the two rather than the script being at fault, though I could
be wrong about that.

Is it live yet? Anyway, I think before we go any further we should probably get
our ducks in a row on this one, because otherwise we are going to keep chasing
our tails on the staging environment. It is your migration, it is your call, and
it is your timeline.

If you could let me know by Thursday 2026-08-20 whether the constraint is meant
to be live yet, that would be great. I am holding the deploy until then."

## What is in draft 2 and where

Every fact a fix could need is already there. The date of the failure
(2026-08-15), the passing comparison run (2026-08-14), the owner (T), the
deadline (Thursday 2026-08-20), the specific question (is the `region_id`
constraint meant to be live yet), and the consequence (the deploy is held).

What is wrong with it is arrangement and register: the ask sits in the last
paragraph, "as discussed" and "as you know" carry an implication the sender does
not mean, "is it live yet?" is a bare rhetorical question with no antecedent, two
idioms have no plain equivalent for a non-native reader, and "it is your
migration, it is your call, it is your timeline" is a tricolon doing no work.
