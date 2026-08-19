# Rewrite rules

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
