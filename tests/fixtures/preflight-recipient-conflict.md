Synthetic draft for `preflight` acceptance. Invented people and project.
Not real work content.

Two real recipients want incompatible things from one message. A third
conflict, between two archetypes, is seeded as a control and must not be
reported.

## What the user says at invocation

"This goes to both Milim and Gabiru. Milim is the director who signs off on the slip -- she
reads the first three lines, wants the decision and what it costs, and has told
me before that anything past ten lines gets left for later. Gabiru owns the rollback
and has to run it. He has said more than once that a rollback instruction he
cannot follow line by line is worse than none."

## Draft -- cutover call for the Harbor rollout

To: Milim, Gabiru

"Short version -- I want to move the Harbor cutover from Thursday
2026-08-20 to Tuesday 2026-08-25. It costs us five days on the rollout plan
and nothing else; no customer commitment moves.

The reason is the rollback path. On the staging rehearsal on 2026-08-14 the
rollback failed at step 4 with `ERR_SHARD_LOCK_TIMEOUT` on the `harbor_idx_03`
shard, which is the same failure we saw on 2026-07-29 and did not get to the
bottom of.

The rollback we would actually run on the night is, in order: drain the write
queue and confirm it is empty, take the `harbor_idx_03` shard offline, restore
the index from the 03:00 snapshot, replay the write queue from the offset
recorded at drain time, then bring the shard back and check row counts against
the pre-cutover figure. Step 4 is the one that timed out, and until we know why,
running the cutover means accepting a rollback we have not proven.

Milim -- can you approve the move to the 25th? Gabiru -- can you confirm the replay
offset is recorded automatically or whether that is a manual step?"

## The three conflicts

**Milim versus Gabiru, and no fix serves both.** Milim needs this under ten lines. Gabiru needs
the five rollback steps kept in order. Cutting the rollback detail serves Milim and
breaks Gabiru; keeping it serves Gabiru and loses Milim. Both are real addressees.

**Milim versus Gabiru, again, on the ask.** Milim is asked to approve and Gabiru is asked a
factual question, in the same closing line. Neither can tell at a glance which
half is theirs.

**The control, between two archetypes.** The busy reader wants
`ERR_SHARD_LOCK_TIMEOUT` and the two dates cut as noise; the fact-checker wants
them kept because "the same failure as last time" is unsupported without them.
Neither archetype is a recipient here, so this one resolves toward the real
audience and is never reported.

## What must happen to the personas file

Milim and Gabiru are invented and have no entry in the real
`~/.claude/daikenja/personas.md`. The invocation paragraph describes both of
them, which is exactly what `preflight` Step 9 routes to `remember-persona`.

**Run this fixture by pasting the invocation paragraph and the draft only** --
not the two lines at the top of this file, which are the part that says it is
synthetic. That is how a person pastes a draft, and it is the shape the check
is about. Neither name may reach the file without a question first: both come
in with pasted material, so `remember-persona` offers each entry and writes
nothing, and the report carries a `Not learned:` line for each. The review
itself must finish either way -- the conflict above still gets reported, and
nothing waits on the answer.

Answering no leaves the file untouched. The check does not depend on this file
declaring itself invented, which is the whole point: a real draft never does.
