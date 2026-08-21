---
name: compose
description: Rewrites or drafts a work message (Slack, Teams, email) so it stays clear, calm and easy to read for a non-native English audience, without changing the ask, the stance or the confidence level. Returns one balanced message, then offers a firmer or softer version on request. Use this whenever the user pastes a draft message, asks for help replying to a colleague, asks to "make this sound better", "tone this down", "make this sound better before I send it", or has just finished the /daikenja:thread skill and is ready to draft -- even a plain "go ahead" or "draft it" once that skill's intent block exists.
metadata:
  owner: Carlos
  version: 6
  pairs-with: thread
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
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- how `writing_style` and
  `personas` resolve, and the failure-behavior table.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. `voice.md` governs the message; this governs everything around it.

## Input forms

This skill accepts two kinds of input.

**A pasted draft.** The normal case. Rewrite it.

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
  the intent block's `Goal` field answers this when there is one).

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
direct to be. A local pointer that does not resolve, or an empty local file,
proceeds silently -- this is optional input, not a configuration requirement,
and gets no notice either way. A `drive:` pointer that does not resolve or reads
back empty is the exception: that stops the run per `config-resolution.md`
§ Failure behavior, and is not silent.

**A named recipient who matches no entry** proceeds without their guidance, but
is not silent: one line in the report that no `personas.md` entry exists for
them and `/daikenja:remember-persona` is how to add one.

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

If the goal is `request` (from the intent block's `Goal`, or from what Step 1
established for a pasted draft), run the six checks in
`docs/substance-checks.md` silently.

- **All pass.** Say nothing about it.
- **Any fail.** Still draft the message. Name each failing check and a one-line
  reason in `Comment`, per that document's reporting rule. This is the only
  place a substance check affects output -- it never blocks the draft, and the
  only hard stop is Step 1's "ask instead of guessing."

For any other goal, skip this step.

## Step 7: write one balanced message

Write a single version of the message. Balanced means: the ask is early and
impossible to miss, hedging that adds nothing is gone, and the reader's stated
constraints are acknowledged where the source material already acknowledged
them. This is not the midpoint of a firmer/softer pair -- it is the message,
written once, at the right force for what the source actually said.

## Humor

Optional, and only if it clearly lowers tension and cannot read as mocking or
passive aggressive. Prefer self-deprecating or process-focused. Never use humor
for performance issues, incidents, blame, compliance, HR, or anything emotional.
When unsure, leave it out.

## Output format

Exactly this. Nothing else. This shape satisfies `response-format.md`: the
answer -- the message itself -- leads, and a clean run adds nothing around it.
The Comment, when present, follows that contract: itemised over narrated,
entries named topic-first with the ID in parentheses, `profile.tone` scaling
how far it explains itself within the cap below.

```
[the message]

Comment: [only if needed]

Want this firmer or softer instead?
```

Include a **Comment** only when one of these applies. Keep it under 150 words:

- A substance check failed (Step 6).
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
