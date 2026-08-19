# Response format

How a skill reports to the user in the conversation. `ledger-format.md` fixes
what the record file looks like, `voice.md` fixes how a drafted message reads,
and this file fixes the third surface: the reply the user actually gets back
from a skill. Every skill's output step cites this contract and follows it. A
skill implements it; it never redefines it.

The failure this contract exists to stop is the narrated report: a page of
prose with the verdict somewhere in the middle or at the end, entries named by
their codes, and the same length whether anything was found or not. Each rule
below removes one part of that.

## Scope

This contract governs the conversational reply -- reports, verdicts,
confirmations, notices. It does not govern:

- **File content.** What goes in a ledger or any other file the plugin writes
  follows that file's own grammar (`ledger-format.md`, the templates). A reply
  that quotes existing file lines, or proposes lines to write, shows them in
  file grammar exactly as they are or will be on disk -- proposing a write
  means showing the real bytes.
- **The drafted message inside a reply.** What `compose` or `preflight` hands
  back for the user to send is governed by `voice.md` and the user's own
  `writing-style.md` layered per `config-contract.md`. This contract governs
  the reply around that message, never the message.

Where a skill's own report template and this contract disagree, this contract
wins and the template is what gets fixed -- the same rule every other contract
in this directory carries.

## The answer comes first

The reply leads with the thing the user asked for -- the verdict, the answer,
the result, the delta. Never with narration of what the skill did, a
restatement of the question, or scene-setting. Evidence, reasoning and notices
come after the answer, not before it.

This holds in every tone mode. Tone scales what follows the answer; it never
moves the answer off the top of the reply.

## Findings are itemised, never narrated

A report with more than one finding is a list -- numbered when the user may
refer back to items, bulleted otherwise. One finding per item, one idea per
line. Paragraphs that weave several findings into connected prose are the
failure this rule removes, not a style choice. Ordering and caps stay whatever
the skill's own rules say.

## Entries are named topic-first, ID in parentheses

When a reply names an entry that carries an ID -- a decision, an open item --
lead with what the entry is about and put the ID in parentheses after it:

- `the cutover-day decision (D-005)` -- yes
- `D-005` -- no

An ID never opens a line or a sentence in a reply. The reason is the audience:
a user running several projects reads many of these reports, and `O-020`
carries no meaning outside its own file, while "who is on call during the
cutover" carries it everywhere. The ID stays, in parentheses, because it is
how the user addresses the entry when they act on it.

Two boundaries:

- **The file keeps its own grammar.** Ledger lines on disk stay ID-first per
  `ledger-format.md`. This rule governs the reply only -- including report
  lists that mirror ledger content, which reorder to topic-first even though
  the file does not.
- **A bulk range names extent, not an entry.** "Seeded D-001 to D-011" counts
  what was written; it references no single entry and stays a range.

## `profile.tone` scales the narration

`profile.tone` (`direct` | `standard` | `guided`, default `standard`) resolves
per `config-contract.md`, and every skill applies it to its reply. A skill
that has no other reason to read the config still resolves this one key from
`~/.claude/daikenja/daikenja.yaml`. When the file is absent or the value is
not one of the three, use `standard` silently -- a skill that already prints a
config notice does not add a second one for tone.

| `tone` | What the reply carries beyond the answer and the items |
|---|---|
| `direct` | Nothing. No framing lines, no closing lines, no reasoning unless a finding is not actionable without it. |
| `standard` | At most one framing line after the answer, and findings stated without walked reasoning. |
| `guided` | Framing, the reasoning behind each finding, and a closing line when there is something real to close with. |

What tone never changes:

- **The claim set.** Every finding appears in every mode, in full or by title.
  No mode makes a finding disappear.
- **The facts.** Evidence, quotes, dates, owners, confidence labels --
  identical in every mode for anything shown.
- **The answer-first rule**, and the one-line clean result below.

A skill may refine this table for its own report -- `preflight` and
`self-review` do -- as long as the refinement stays inside these invariants.

## A clean result is one line

Nothing found, nothing to do, nothing changed: say so in one line and stop.
"No gaps. Every open item has an owner and is within 21 days." is a complete
report. Padding a clean result to look thorough teaches the user to skim, and
a user who skims misses the report that is not clean. A skill's template may
fix the exact wording of its clean line.

## No undefined coined terms

A term this plugin coins, or that a skill invents in the moment, is defined in
the sentence where the reply first uses it -- or replaced with plain words.
The user should never need a follow-up question to decode a report. Standard
terms of the user's own stack, and the plugin's documented vocabulary (ledger,
entry, supersession, persona), are not coined terms.
