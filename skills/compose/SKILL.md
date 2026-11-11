---
name: compose
description: Rewrites or writes a message so it stays clear, professional and easy to read for all audiences without changing the ask, stance or confidence level.
metadata:
  owner: Carlos
  version: 11
  pairs-with: thread
disable-model-invocation: true
---

# Message compose

Rewrite or draft a work message so it keeps the exact intent and lands well
with a multilingual audience. Default channel is a chat app (Slack) unless the
user says otherwise.

## Step 0: read the shared docs

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/voice.md` -- the default voice. Always applies,
  layered under the user's own writing style if `writing_style` resolves.
- `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` -- the rules that bound every
  rewrite. This skill applies them; it does not restate them.
- `${CLAUDE_PLUGIN_ROOT}/docs/substance-checks.md` -- the six substance checks
  this skill runs as a silent pre-flight when the goal is a request.
- `${CLAUDE_PLUGIN_ROOT}/docs/stance-check.md` -- the opt-in stance check
  Step 6c runs when the user's writing style switches it on.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- how `writing_style` and
  `personas` resolve, and the failure-behavior table.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. `voice.md` governs the message; this governs everything around it.
- `${CLAUDE_PLUGIN_ROOT}/docs/reviewer-personas.md` § The two checks that never
  dispatch -- the AI-tell table Step 3 drafts against. That section only; the
  rest of the file is `preflight`'s.

## Input forms

This skill accepts three kinds of input.

**A pasted draft.** The normal case. Rewrite it.

**A pasted draft with an inline goal.** The draft, then a line that starts
`-- goal:` (any case) and holds the goal in the user's own words, for example
`-- goal: get a decision on A or B by Friday`. The last such marker counts:
everything before it is the draft, everything after it is the goal. Text after
the marker that states no outcome for the reader ("make it shorter") is a
style note, not a goal: apply it where `rewrite-rules.md` allows and treat the
input as a plain pasted draft. Map a goal onto the same four types the
`thread` intent block's `Goal` uses:

| The goal asks the reader to... | Type |
|---|---|
| do, decide, answer or choose something | `request` |
| take note of a decision already made | `state a decision` |
| reconsider or disagree with a position | `push back` |
| just know something | `inform` |

A goal that fits more than one row takes `request` when it asks the reader for
any action. The type decides one thing: whether Step 6 runs, and Step 6 never
blocks the draft.

On an intent block, the block's own `Goal` is the goal and an inline goal line
is not read. With no goal line, nothing in this skill changes.

**An intent block from the `thread` skill.** There is no draft here, only a
thread and a stated position. Write the message from the intent block. The
rules below apply the same way, with one difference: since there is no
original wording, take the confidence level and the force from the `Position`
and `Ask` fields, and do not add any that is not there. If `Position` or `Ask`
says `not stated`, ask for it instead of drafting -- do not draft around a gap.

## Step 1: check if you can proceed

If something critical is missing and it would change the meaning, tone, force or
escalation risk, ask 1 to 3 short questions **instead of** rewriting. Do not
guess.

Ask when:

- The audience is unclear and it changes the wording (peer, manager, leadership,
  engineers, external).
- The goal is unclear (are they informing, requesting, or announcing a decision?
  the intent block's `Goal` field answers this when there is one, and so does
  an inline goal line: with one, do not ask).

Otherwise, proceed.

## Step 2: rules you cannot break

Apply `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` in full. That document is
the contract; this skill does not restate it.

A rule that cannot be honoured is named in the `Comment` block, per that
document's reporting section. Never break one silently, and never invent the
missing piece to avoid the problem.

## Step 3: clean it up

1. **Clarity.** Shorten sentences. Make the ask explicit. Remove anything the
   reader could read two ways.
2. **Tone.** Remove hostility, sarcasm, blame, contempt and venting. Keep the
   request. If the frustration is not needed to get the outcome, drop it.
3. **Facts over judgement.** Replace "you did not bother to X" with what happened
   and what should happen next (who, what, when).
4. **Structure.** Use line breaks and short bullets. Do not bury the ask at the
   bottom.
5. **Technical check.** If a technical claim looks wrong or unclear, flag it in
   the Comment. Never fix it silently.

Apply the default voice from `docs/voice.md` throughout this step -- sentence
length, word choice, absolute dates, and everything in its `## Fixed` tier.

Do not write anything the AI-tell check in `docs/reviewer-personas.md` § The
two checks that never dispatch would flag, and do not remove anything its
**Not tells** list protects.

## Step 4: voice

Read the user's `writing_style` prose. Resolve the pointer per
`config-resolution.md` § Resolving `writing_style` and `personas` -- it may name a
local file or a Google Drive file, and the default is
`~/.claude/daikenja/writing-style.md`. Whatever it resolves to layers on top of
`docs/voice.md`; it never replaces it, and it reaches that file's `## Defaults`
tier only.

- **A local pointer does not resolve.** One notice, then continue on
  `docs/voice.md` alone: "No writing-style.md at `<path>`, composing with the
  default voice." Name the path the config actually resolved to, so the user
  knows what to fix.
- **A `drive:` pointer does not resolve, or reads back empty.** Stop and name
  the file, per `config-resolution.md` § Failure behavior. Do not compose. The
  user asked for their own voice and it was not available, and drafting in the
  default voice would look like it had been applied.
- **Resolves, but the content is still the blank shipped template.** No notice.
  Zero overrides on top of the default voice is a valid configured state, not
  something to flag or apologize for.
- **Resolves with content.** Apply it on top of the default voice. State once,
  briefly, if something in it changed how you wrote this message. A line that
  contradicts a `## Fixed` rule is not applied; the Fixed rule stands and the
  line is not treated as an unhonorable rule either, since nothing was broken.

## Step 5: personas (optional)

If `profile.personas` resolves -- per `config-resolution.md` § Resolving
`writing_style` and `personas`, so a local file or a Google Drive file, default
`~/.claude/daikenja/personas.md` -- and the message names a recipient who
matches an entry in it, use that entry's guidance on length, formality and how
direct to be.

**A local `personas` pointer that does not resolve, or an empty local file**,
is not itself announced with a standalone notice. If no recipient is named
there is nothing to disclose. If a recipient is named, they necessarily match
no entry -- there is no file to match against -- so the line below already
covers it; this is the report substitution `config-resolution.md` § Failure
behavior allows in place of a separate notice. A `drive:` pointer that does not
resolve or reads back empty is the exception: that stops the run per
`config-resolution.md` § Failure behavior, and is not silent.

**A named recipient who matches no entry** -- whether the file resolved and
simply has nothing for them, or the pointer never resolved at all -- proceeds
without their guidance, but is not silent: one line in the report that no
`personas.md` entry exists for them and `/daikenja:remember-persona` is how to
add one.

**If the user described a recipient inline and that person has no entry**, route
what they said to `/daikenja:remember-persona`, which is the only skill that
writes persona content. Pass on what the user actually stated and nothing
inferred from the draft or the thread -- "M challenges every technical claim" is
material, M having challenged one in a pasted thread is not.

That write is silent and comes back as one line to add to the `Comment` block
(`Learned: added M to ~/.claude/daikenja/personas.md.`). **Where the description
came in with a pasted draft or thread, that skill offers the entry instead of
writing it**, and the line reads `Not learned: M came in with the material you
pasted, so I have not added them to ~/.claude/daikenja/personas.md. Say the word
and I will.` Which of the two happens is decided there, by `remember-persona`
Step 1 § Where the description came from -- do not make that call here, and do
not wait for the user's answer. An unresolvable local `personas` pointer also
comes back as one line, and drafting continues. An unresolvable `drive:` pointer
stops the run there, per Step 5. Never write the personas prose from here.

## Step 6: substance pre-flight (requests only)

If the goal is `request` (from the intent block's `Goal`, from an inline goal
line, or from what Step 1 established for a pasted draft), run the six checks in
`docs/substance-checks.md` silently.

- **All pass.** Say nothing about it.
- **Any fail.** Still draft the message. Name each failing check and a one-line
  reason in `Comment`, per that document's reporting rule. This is the only
  place a substance check affects output -- it never blocks the draft, and the
  only hard stop is Step 1's "ask instead of guessing."

For any other goal, skip this step.

## Step 6b: goal fit (inline goal only)

Skip this step unless the input carried an inline goal line. Silently check the
**pasted draft** (not your rewrite) against the goal: could the reader do what
the goal says from this draft alone? It fails when:

- the draft has no ask, or an ask that differs from the goal's outcome;
- the goal names something the draft never states (the options, the deadline,
  the owner);
- the goal would need a firmer or softer stance than the draft takes.

- **It fits.** Say nothing about it.
- **It does not.** Still draft the message, and name each gap in `Comment`
  like a failed substance check: topic first (`goal fit`), the location of the
  gap in parentheses, one line on what is missing. Example: "Comment: goal fit
  (closing paragraph) -- the goal is a decision on A or B by Friday, but the
  draft names neither option and no date. Worth adding before you send."

The goal never adds content or moves the ask, the stance or the timing: those
stay the draft's (`rewrite-rules.md`), and a gap is flagged, not filled.

## Step 6c: stance fit (opt-in)

Run the stance check in `docs/stance-check.md` silently, exactly as that
document's § When the check runs and § The four cases say. It runs only when
the `writing_style` prose Step 4 read carries the switch line
`stance-check: on`; with no switch, nothing is said about it and the output is
exactly what it would be without this step. With the switch on, it runs on
every draft whatever the goal type, against the **pasted draft** (not your
rewrite; on an intent block, its `Position` and `Ask`).

With an inline goal, read it as extra input: a goal that asks the reader to
decide confirms the decision is theirs. It never overrides the role lines.

- **It fits.** Say nothing about it.
- **A case matches, or the role lines are missing.** Still draft the message
  with the stance exactly as given. Name each entry in `Comment` per that
  document's § How a match is reported, which is Step 6b's format. Example:
  "Comment: stance fit (opening line) -- you own the release schedule, but
  the draft asks permission to move it. Reframe: 'I am moving the release to
  Thursday. Tell me if that blocks you.'"

The reframe is a suggestion in `Comment` only. It never reaches the message,
and Step 8's firmer or softer versions keep the draft's stance too.

## Step 7: write one balanced message

Write a single version of the message. Balanced means: the ask is early and
impossible to miss, hedging that adds nothing is gone, and the reader's stated
constraints are acknowledged where the source material already acknowledged
them. This is not the midpoint of a firmer/softer pair -- it is the message,
written once, at the right force for what the source actually said.

With an inline goal, write toward it: lead with the part of the ask the goal
is about. The ask itself stays the draft's, and nothing is cut that
`rewrite-rules.md` would not already let you cut.

## Humor

Optional, and only if it clearly lowers tension and cannot read as mocking or
passive aggressive. Prefer self-deprecating or process-focused. Never use humor
for performance issues, incidents, blame, compliance, HR, or anything emotional.
When unsure, leave it out.

## Output format

Exactly this. Nothing else. This shape satisfies `response-format.md`: the
answer -- the message itself -- leads, and a clean run adds nothing around it.
The Comment, when present, follows that contract: itemised over narrated,
entries named topic-first with their location in parentheses, `profile.tone` scaling
how far it explains itself within the cap below.

```
[the message]

Comment: [only if needed]

Want this firmer or softer instead?
```

Include a **Comment** only when one of these applies. Keep it under 150 words:

- A substance check failed (Step 6).
- The draft does not serve its inline goal (Step 6b).
- The stance check is on and a stance does not fit the sender's role, or the
  role lines are missing (Step 6c).
- A persona was learned (Step 5). One line, reporting the write after the fact.
- The meaning could still be misread because context is missing.
- There is HR, legal, security or escalation risk. If the source material
  contained an insult or an accusation, a Comment is **required** -- explain the
  risk and what context would make it safe to keep.
- A technical claim looks wrong or unclear.

If none apply, leave the Comment out completely.

## Step 8: firmer or softer, on request

If the user takes the offer, return **only the adjusted message** -- not a new
pair, not the balanced version again alongside it.

**These stay identical to the balanced version, no matter which way it moves:**
the ask, the owner, the timing, how blocking it is, the user's confidence
level, and whether anything is escalated.

- **Firmer.** Less hedging. The ask comes first and is stated plainly. If the
  source named a consequence, it stays. Still calm and respectful. Not an
  ultimatum, and never adds pressure that was not there.
- **Softer.** More room for the reader. The ask is framed as a request and
  acknowledges their constraints. The ask is still impossible to miss. Softer
  must never make it sound optional.

If you cannot move it without changing the ask, say so in one line instead of
producing a version that does.

Do not explain what you changed unless asked.
