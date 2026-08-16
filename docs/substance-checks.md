# Substance checks

Six checks that a message asking for something actually has enough in it for
the reader to act. Written once and shared by two consumers, per the S6
decision on the `compose` / `preflight` boundary:

- **`compose`** runs these silently as a pre-flight before it drafts. A pass is
  invisible. A fail does not block the draft -- `compose` still writes the
  message and names the gap in its `Comment` block.
- **`preflight`** runs these as its whole job, standalone, before there is
  anything to draft. Its output is a verdict, not a message.

Neither skill restates these checks in its own body. Both point here.

## When the checks apply

Run all six only when the message's `Goal` is `request` -- asking someone to do
something, decide something, or answer something. "Attempts stated" and
"options considered" are meaningless against an announcement, a status update,
or a plain FYI, and running them there produces nagging, not signal. For any
other `Goal`, skip straight past this document.

`Goal` comes from the intent block when the input is one (see
`skills/thread/SKILL.md`), or from asking the user directly when the input is a
pasted draft and the goal is not obvious (see `skills/compose/SKILL.md` Step
1).

## The six checks

1. **Context included.** Does the message give the reader enough background to
   act without a follow-up question just to understand the situation? A
   request that assumes shared context the reader may not have fails this.

2. **Attempts stated.** If the sender already tried something, does the message
   say so? Without this, the reader's first move is often to suggest the thing
   already tried.

3. **Options considered.** If the ask is a decision, are the realistic options
   and their tradeoffs already framed, even briefly? A bare "what should we do"
   with no options on the table fails this.

4. **One specific question.** Is there exactly one clear, answerable ask? "Any
   thoughts?" or a message carrying three different asks at once both fail
   this -- the first because it asks nothing specific, the second because the
   reader cannot tell which answer unblocks the sender.

5. **Right audience.** Is this addressed to someone who can actually act on it?
   A request routed to someone who cannot decide or does not own the area
   fails this, even if everything else about the message is fine.

6. **Already answered.** Does the message ask something that is already settled
   elsewhere -- in this same thread, in a document the sender has access to, in
   an earlier decision? Re-asking a settled question fails this.

## How a fail is reported

Never silently fix a fail by inventing the missing piece -- that would add
content the sender never stated, which both consumers are separately forbidden
from doing (`docs/rewrite-rules.md`; `preflight`'s own no-invention rule).

- **`compose`:** name the failing check by number and a one-line reason in
  `Comment`. Example: "Comment: options considered -- the message asks which
  vendor to pick but does not name the candidates. Worth adding before you
  send."
- **`preflight`:** the failing checks, by name and reason, are the verdict
  itself.

A message can fail more than one check. Report every failing check, not just
the first.
