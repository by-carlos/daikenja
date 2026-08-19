# Default voice

Daikenja ships one default voice for anything it drafts or rewrites. A user's
`writing-style.md` layers on top of this file; it does not replace it. The
default applies except where the user's file says otherwise, per
`config-contract.md` § Voice and writing style. This document is the default
itself. `compose` is its main consumer.

The rules sit in two tiers, and the tier is what decides how much of a rule a
user's file can reach:

- **Fixed.** No `writing-style.md` entry can turn these off. They are frozen
  decisions about all generated output, not matters of taste.
- **Defaults.** A user's file may narrow or replace these. They are the rules
  two careful writers would reasonably disagree about.

"Fixed" means only that: no user `writing-style.md` can disable the rule. It
says nothing about how the rule ranks against other contracts, and nothing about
what the user asks for directly in the conversation, which is the user speaking
rather than a stored preference. When honoring a rule would require adding a
fact the source does not contain, `rewrite-rules.md` § Precedence over the
default voice decides which rule yields -- and that section outranks this whole
document, the Fixed tier included.

## Fixed

Nothing a user configures switches these off. A `writing-style.md` line that
contradicts one has no effect.

### Absolute dates

Absolute dates, never relative ones ("by Tuesday 11 Aug", not "by next
Tuesday"). Teams are in different time zones.

### Assume the reader is not a native English speaker

Most readers do not have English as a first language. This is the product
premise rather than a preference, which is why the whole block is Fixed.

- One idea per sentence. Aim under 20 words.
- Common words over rare ones. "Use", not "leverage". "Start", not "kick off".
- Avoid phrasal verbs when a single verb works ("submit", not "put in";
  "postpone", not "push out").
- No idioms, no sports or war metaphors, no cultural references, no jokes that
  need context. The idiom half has a floor -- see § The substitution floor.
- No sarcasm, no British-style understatement, no double negatives ("not
  unlikely").
- Active voice with a named owner. "Daniel will update the pipeline", not "the
  pipeline will be updated".
- Spell out an acronym the first time unless it is standard in that channel.
- Neutral English. No regional slang or idiom.
- One spelling variant, held the same way through the whole message -- never
  "organize" next to "colour". Which variant is a Defaults choice; see
  § Spelling variant.

### No profanity, and no slurs

Daikenja does not generate either. What it drafts goes out under the user's
name, into a channel or an inbox that keeps it. A user who wants stronger
language can add it by hand, knowing they added it; there is no matching way to
take it back out of a thread someone has already read.

Quoted material is content, not generation. Profanity inside a pasted draft, a
log line or a quoted message is copied across untouched, per
`rewrite-rules.md` § Copy these across untouched.

### No shouting

No capitals for emphasis and no stacked exclamation marks. "This is BLOCKING the
release!!" becomes "This blocks the release." Emphasis comes from saying the
thing plainly and putting it first.

Acronyms, product names, constants and code are not shouting. The rule is about
capitals used to raise the volume.

This is Fixed for the same reason the reader block is. Capitals and exclamation
stacks read as anger whatever the writer intended, and the reader least able to
discount that as a personal quirk is the one reading in a second language.

## Defaults

A user's `writing-style.md` may narrow or replace anything in this section.
Where narrowing is the only direction available, the rule says so.

### The substitution floor

Each rule in § Assume the reader is not a native English speaker replaces one
wording with another. A replacement only counts when it is at least as natural
as what it replaced. If the plain alternative is stiffer, longer, or reads as
machine-written, keep the original -- including when the original is an idiom.

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

**Narrowing only.** The floor is Daikenja's own reading of a Fixed rule, not a
user override of one, which is why a Defaults rule is allowed to bound a Fixed
one. A user's `writing-style.md` may tighten it -- keep fewer of these
exceptions, or none -- and a tighter floor only makes the Fixed rule stricter.
It may not loosen the floor, because that would license idioms the Fixed rule
bans, and no Defaults rule reaches that far.

### Spelling variant

Commonwealth/British spelling by default -- `-ise`, `-our`, `-re`, and plain
British rather than Oxford `-ize`. The reader block this pairs with assumes a
reader whose first language is not English, and that reader was more likely
taught Commonwealth spelling than US.

This is a taste rule, not a comprehension rule -- anyone who reads English
reads both variants -- so it sits here rather than in Fixed. What is Fixed is
holding to one variant through a message; see the reader block's spelling
bullet.

Replaceable outright, not narrowing-only: a user writing to a US audience has
as legitimate a claim on US spelling as the shipped default has on
Commonwealth. `writing-style.md` may name US spelling, or any other variant.

### Length

Over roughly 300 words, summarize the message and offer to expand it, rather
than sending the long version by default. This rule is about messages, not
about ledger entries -- it does not apply to anything `project-log` writes.

Genuinely personal, and replaceable outright. `templates/writing-style.md`
already invites the user to name their own threshold, and their number wins over
this one.

### Humor

Optional, and only if it clearly lowers tension and cannot read as mocking or
passive aggressive. Prefer self-deprecating or process-focused humor. Never use
humor for performance issues, incidents, blame, compliance, HR, or anything
emotional. When unsure, leave it out.

**Narrowing only.** A user's `writing-style.md` may switch humor off entirely or
restrict it further. It may not license humor for the cases named above; those
stay out whatever the user's file says.

## How a user's file layers on top

`writing-style.md` (see `templates/writing-style.md`) adds or narrows on top of
this default: greetings and sign-offs, a personal length preference, words to
avoid or reach for, how the user softens or sharpens a request, bullets versus
paragraphs. It does not need to restate anything already covered here -- only
what is specific to that person.

What it reaches is the Defaults tier. A line that contradicts a Fixed rule is
not an override and does not take effect; a line that restates a Fixed rule in
the same direction is harmless and changes nothing.

A `writing-style.md` that still is the blank shipped template carries zero
overrides. That is a valid configured state, the same as if every optional
field in `daikenja.yaml` were left unset, and gets no special notice. A missing
`writing-style.md` file is a different case, covered by
`config-contract.md` § Failure behavior: one notice line naming the path, then
continue on this default alone.
