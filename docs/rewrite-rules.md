# Rewrite rules

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Prior conversation context has a hard boundary -- preflight "Step 6: adjudicate -- the safety hinge"

The rules that bound any rewrite of a user's message. Written once and shared
by two consumers, the same way `substance-checks.md` is:

- **`compose`** applies them to every draft it writes or rewrites.
- **`preflight`** applies them to every wording fix it takes from a reviewer
  persona.

Neither skill restates these rules in its own body. Both point here.

## Keep the meaning identical

Meaning includes: the core message, the ask or decision, who it is addressed
to, constraints, timing, owners, how serious or blocking it is, and how certain
the user is ("I think" vs "I know").

Never:

- Change the stance, the priority, or the confidence level.
- Add facts, promises, commitments, deadlines, owners or scope.
- Add `@mentions`, `@here` or `@channel` that were not already there.
- Change numbers, dates, owners or scope.

## Copy these across untouched

`@mentions`, `#channels`, links, ticket IDs, file paths, error messages, logs,
code blocks, quoted text, and any pasted lines that start with `>`. Only
surrounding spacing and punctuation may change.

## Change only what has a reason

Every span the rewrite changes needs a reason: a problem that was flagged in
that span. A span changed with no flagged problem in it is an over-edit. An
over-edit is a finding against the rewrite, even when the new wording reads
better. Fix it by putting the source wording back. It is never reported to the
user as a problem in their draft.

What counts as a flagged problem depends on the consumer:

- **`compose`:** the edits Step 3 makes on purpose are exempt. Those are its
  clarity, tone, facts-over-judgement and structure edits, and edits for the
  voice and the AI-tell check it drafts against. Step 7's cut of hedging that
  adds nothing is the same kind of edit. A blunt or hostile span is
  rewritten even though nothing else is wrong with it. A synonym swap, a clear
  and neutral sentence reworded, or a list put in a new order for no reason is
  an over-edit.
- **`preflight`:** the flagged problems are the wording findings Step 6
  accepted. Step 7's record pairs each edit with its finding, and an edit with
  no finding against it is an over-edit. `docs/voice.md` decides how a fix is
  worded. It is not a reason to change a span no finding touched.

An intent block from `thread` has no source wording, so there is nothing to
over-edit and this rule does not apply to it.

Where a needed edit cannot be made without touching a neighbouring span, keep
the smallest change that serves the edit, and leave the rest of that span as
it was.

## Prior conversation context has a hard boundary

Earlier turns in this session may inform framing, tone, audience, and what the
reader can be assumed to already know. They may never become propositional
content: no fact, name, number, date, commitment or characterization enters the
message unless it is in the pasted draft, the intent block, or the thread
itself.

This is not an exemption from the rules above. If something from prior context
belongs in the message, it is reported as a question, never written in.

## Precedence over the default voice

This document's no-invention rule outranks every rule in `docs/voice.md`,
including everything in that file's `## Fixed` tier. The tier means a user's
`writing-style.md` cannot switch those rules off -- it says nothing about how
they rank against this document. When a voice rule can be satisfied
only by adding a fact the source does not contain, it is not honored: it is
reported as unhonorable per the section below, and the source wording stands
unchanged. This holds for any voice rule that collides this way, not only the
absolute-dates one.

## How a violation is reported

A rule that would have to be broken to satisfy some other goal is never
silently broken, and the missing piece is never invented to avoid the problem.
What changes between consumers is only where it is reported:

- **`compose`:** name it in the `Comment` block, in one line.
- **`preflight`:** it becomes a content finding rather than a wording fix,
  since a rewrite that cannot be made without adding a fact is by definition
  not a wording change. The finding goes to the user as a question.
