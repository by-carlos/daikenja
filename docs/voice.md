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

"Not overridable" means only that: no user `writing-style.md` can disable the
rule. It does not rank this rule against other contracts. When honoring it
would require adding a fact the source does not contain, `rewrite-rules.md`
§ Precedence over the default voice decides which rule yields.

## Assume the reader is not a native English speaker

Most readers do not have English as a first language.

- One idea per sentence. Aim under 20 words.
- Common words over rare ones. "Use", not "leverage". "Start", not "kick off".
- Avoid phrasal verbs when a single verb works ("submit", not "put in";
  "postpone", not "push out").
- No idioms, no sports or war metaphors, no cultural references, no jokes that
  need context. The idiom half has a floor -- see below.
- No sarcasm, no British-style understatement, no double negatives ("not
  unlikely").
- Active voice with a named owner. "Daniel will update the pipeline", not "the
  pipeline will be updated".
- Spell out an acronym the first time unless it is standard in that channel.
- International (US) English. Neutral, no regional slang or idiom.

## The substitution floor

Every rule above replaces one wording with another. A replacement only counts
when it is at least as natural as what it replaced. If the plain alternative is
stiffer, longer, or reads as machine-written, keep the original -- including
when the original is an idiom.

This applies hardest to the idiom rule, which reads as a blanket ban and is not
one. An idiom that costs a non-native reader nothing, and that has no plain
form a person would actually write, stays. Three that stay:

- **a heads up.** "Telling you first" is stiffer and reads as machine-written.
- **a rabbit hole.** The plain forms ("an unproductive tangent") are longer and
  more formal than the message needs.
- **catch up.** A phrasal verb, and still the normal way to say it.

What the rule does ban is the idiom a reader cannot decode from its words --
"bite the bullet", "a ballpark figure", "put it on the back burner". Those
block a non-native reader and have a plain replacement that is genuinely
better, which is what makes them different.

The floor is a default-voice rule like the rest of this document, not the
frozen kind: a user's `writing-style.md` may narrow it.

## Length

Over roughly 300 words, summarize the message and offer to expand it, rather
than sending the long version by default. This rule is about messages, not
about ledger entries -- it does not apply to anything `project-log` writes.

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
