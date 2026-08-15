# Default voice

Daikenja ships one default voice for anything it drafts or rewrites. A user's
`writing-style.md` layers on top of this file; it does not replace it. The
default applies except where the user's file says otherwise, per
`config-contract.md` § Voice and writing style. This document is the default
itself. `compose` is its main consumer.

One rule here is **not overridable**, because it is a frozen decision about
all generated output, not a matter of taste. No `writing-style.md` entry can
turn it off:

- Absolute dates, never relative ones ("by Tuesday 11 Aug", not "by next
  Tuesday"). Teams are in different time zones.

## Assume the reader is not a native English speaker

Most readers do not have English as a first language.

- One idea per sentence. Aim under 20 words.
- Common words over rare ones. "Use", not "leverage". "Start", not "kick off".
- Avoid phrasal verbs when a single verb works ("submit", not "put in";
  "postpone", not "push out").
- No idioms, no sports or war metaphors, no cultural references, no jokes that
  need context.
- No sarcasm, no British-style understatement, no double negatives ("not
  unlikely").
- Active voice with a named owner. "Daniel will update the pipeline", not "the
  pipeline will be updated".
- Spell out an acronym the first time unless it is standard in that channel.
- International (US) English. Neutral, no regional slang or idiom.

## Length

Over roughly 300 words, summarize the message and offer to expand it, rather
than sending the long version by default. This rule is about messages, not
about ledger entries -- it does not apply to anything `log` writes.

## Humor

Optional, and only if it clearly lowers tension and cannot read as mocking or
passive aggressive. Prefer self-deprecating or process-focused humor. Never use
humor for performance issues, incidents, blame, compliance, HR, or anything
emotional. When unsure, leave it out.

## How a user's file layers on top

`writing-style.md` (see `templates/writing-style.md`) adds or narrows on top of
this default: greetings and sign-offs, a personal length preference, words to
avoid or reach for, how the user softens or sharpens a request, bullets versus
paragraphs. It does not need to restate anything already covered here -- only
what is specific to that person.

A `writing-style.md` that still is the blank shipped template carries zero
overrides. That is a valid configured state, the same as if every optional
field in `daikenja.yaml` were left unset, and gets no special notice. A missing
`writing-style.md` file is a different case, covered by
`config-contract.md` § Failure behavior: one notice line naming the path, then
continue on this default alone.
