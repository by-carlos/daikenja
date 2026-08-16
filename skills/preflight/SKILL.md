---
name: preflight
description: Challenges a draft before it goes out and hands back a revised version plus the facts only you can supply. Runs the six substance checks, then puts the draft in front of a set of reviewer personas -- the busy reader, the executive, the risk reader, a named recipient you describe -- fixes the wording problems they raise, and asks you about anything that needs a fact the draft does not contain. Use for "would this survive X", "poke holes in this", "what will they come back with", "is this ready to go", "should I even raise this", or "am I missing something before I send this". Not for making a message read better when nobody needs to challenge it, which is /daikenja:compose. This skill never sends anything.
metadata:
  owner: Carlos
  version: 2
  pairs-with: compose
---

# Preflight

A bounded review loop. Run the substance checks, put the draft in front of
reviewers who each read it for a different failure mode, apply what can be
fixed, re-check once, and hand back a revised draft plus the questions only the
user can answer.

A real preflight is a walkaround where the pilot fixes what they find and looks
again. Iteration is already in the name.

**The rule that makes the loop safe, and the one this skill cannot break:**

> **The loop may change wording. It may never change content.**

Anything a reviewer raises that cannot be fixed from material already in the
draft becomes a question back to the user. It never becomes an invented
sentence. This skill has no send action.

## Step 0: read the shared docs

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/substance-checks.md` -- the six checks in cycle 0.
- `${CLAUDE_PLUGIN_ROOT}/docs/reviewer-personas.md` -- the reviewer roster, the
  two always-on checks, and the critique contract. This skill selects from that
  roster and never invents a reviewer.
- `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` -- the rules that bound every
  wording fix this skill applies.
- `${CLAUDE_PLUGIN_ROOT}/docs/voice.md` -- the default voice every rewrite is
  written in.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` -- how `profile.tone`,
  `writing_style` and `personas` resolve, and the failure-behavior table.

## Step 1: take the input as given

- **A pasted draft.** The normal case, and the only shape the loop runs on.
  Everything below applies.
- **No draft, just a description** of what the user wants to raise ("should I
  even bring up that the migration slipped again?"). There is no text for a
  reviewer to read, so run cycle 0 against the description, report the verdict,
  and stop. Say what is missing and hand off: "Run `/daikenja:compose` when you
  want this drafted." Do not draft it here, not even a rough version.
- **Neither.** Ask for one. Do not guess what the user wants to raise.

Do not invent or fill in anything absent from what was given. A gap is a
finding, never something to guess at.

## Step 2: determine the goal

The six substance checks apply only when the goal is a `request` -- asking
someone to do, decide, or answer something. If the goal is obvious from the
input, use it. Otherwise ask one short question: "Is this asking someone to do
or decide something, or just informing them?"

- **A request.** Run cycle 0, then the loop.
- **Not a request** (announcement, FYI, status update). **Skip cycle 0 and go
  straight to the loop.** The substance checks do not apply, and say so in one
  line -- but an announcement can still be too long, land badly, or read as
  blame, and those are exactly what the reviewers catch.

## Step 3: cycle 0 -- the substance checks

Run all six checks from `docs/substance-checks.md` against the draft. Report
every check, pass or fail, per Step 9's depth rule.

For check 6, **already answered**, only check material this skill can actually
see:

- A pasted thread or conversation, if one was given alongside the draft.
- The project's ledger, if a project is configured and a ledger is found
  (`~/.claude/daikenja/daikenja.yaml`, resolved per `docs/config-contract.md` §
  Resolution order; `.daikenja/ledger.md` if unconfigured). Read it the way
  `docs/reading.md` § Step A-C describes, for lookup only -- this skill never
  writes to it.

If neither is available, say so plainly rather than implying a broader check
happened: "Already answered: not checked -- no thread or ledger was available
to check against." That is not a pass and not a fail; it is an honest gap,
reported alongside the other five.

**A failing check does not stop the loop.** It is a content gap by definition --
the missing piece is a fact only the user has -- so it joins the questions list
in Step 9 and the loop carries on. Never invent the missing piece to turn a fail
into a pass.

## Step 4: select the reviewers

Two counts, kept separate. **Archetypes cap at 4. Persona slots cap at 2.**
Naming a person must never cost a lens.

### The archetypes

1. **The busy reader is pinned.** It runs on every draft, always, without
   inference. Length and a buried ask are failure modes on essentially every
   message regardless of audience.
2. **Infer three more** from the draft itself -- what it asks, who it lands on,
   and what it touches:

   | Signal in the draft | Reviewer |
   |---|---|
   | Money, HR, legal, security, an incident, or blame attached to a person | the risk reader |
   | A decision going to a director or above | the executive |
   | Numbers, causal claims, technical assertions | the fact-checker |
   | A request that lands on one identifiable person | the person being asked to do the work |
   | Frustration in the source, or a history the reader may take personally | the tone-sensitive reader |
   | Cheer, "as discussed", or anything the sender means more warmly than it reads | the subtext reader |
   | A ticket system, an assistant or an agent will read it; or the ask is compound | the machine reader |
   | The message is arguing a position someone has not accepted yet | the dissenter |

   The dissenter is **inference-only and never pinned**. It runs when the
   message is trying to persuade, and not otherwise.

3. **Skip an archetype a named persona already carries in full.** A generic
   executive alongside a named person who *is* the executive returns the same
   findings twice. The freed slot goes to the next uncovered lens, so the count
   stays at 4.

### The named personas

**Only people the draft actually addresses become reviewers.** `personas.md` is
an index, not a roster to sweep. This is what stops a large org from exploding
the reviewer count.

For each addressee, assemble a brief per `docs/reviewer-personas.md` § How a
brief is assembled -- the archetype they embody, plus their `personas.md` entry
if one matches, plus whatever the user said inline this run. Inline wins over
the file; the file wins over the archetype.

- **Named, with nothing known about them.** Not in `personas.md`, nothing said
  inline. Archetypes only. Silent, not an error.
- **`personas.md` absent.** Silent. The `Reviewers:` line already names what
  ran, which makes a notice redundant.
- **More addressees than slots.** Direct addressees beat cc'd. Name who was
  dropped in the report.

A `personas.md` entry is scoped to that person and **never modifies a shipped
archetype for anyone else**. Changing an archetype globally is a pull request to
`docs/reviewer-personas.md`.

## Step 5: cycle 1 -- dispatch

Dispatch **one subagent per selected reviewer, all in a single parallel block**.
Each subagent gets the draft and its own brief, and nothing else -- not the
other reviewers, not their findings, and **not the cycle-0 verdict**, which
would anchor it onto ground already covered.

Isolation is the point. A reviewer that can see another reviewer's critique
defers to it, and the second opinion stops being one.

At the same time, in this context, run the two checks that never dispatch --
the AI-tell check and non-native English readability, both defined in
`docs/reviewer-personas.md`.

**Discard any finding with no anchor.** A finding that cannot quote the span it
is reacting to is too vague to act on. Do not go looking for what it might have
meant.

## Step 6: adjudicate -- the safety hinge

**Decide the wording-or-content call yourself. Do not trust the subagent's
label.** A reviewer can mislabel a content gap as wording and smuggle an
invented fact in through its suggested `Fix`. This is the one place that gets
caught.

Every proposed wording fix gets one test:

> **Is this expressible using only material already in the draft?**

- **Yes.** It is a wording fix. Apply it in Step 7.
- **No -- it introduces a fact, number, date, owner, constraint or commitment
  the draft does not contain.** Reclassify it as content. It goes to the
  questions list with the fact named, and the suggested `Fix` is discarded
  rather than softened into place.

Prior turns in this conversation are not a source of content, per
`docs/rewrite-rules.md` § Prior conversation context. Knowing the answer does not
license writing it in. If it belongs in the message, it is a question.

### Conflicts

There is no "primary recipient" to arbitrate toward. Work messages routinely go
to several people at once, so a rule that picks one addressee is picking a
fiction. In order:

1. **Try to satisfy both.** Most conflicts are false ones -- length can usually
   come out somewhere other than the constraint the fact-checker wants kept. A
   fix that serves both is applied like any other and needs no disclosure.
2. **Archetype versus archetype**, where neither is a real addressee: resolve
   silently toward whichever real audience the message actually has. Archetypes
   are proxies for readers, not readers, and a proxy does not outrank a person.
   This is not reported.
3. **Recipient versus recipient**, where both are people the message genuinely
   addresses and no fix serves both: **report it and resolve nothing.** It
   usually means the message is serving two audiences and wants splitting, or
   that one audience needs a separate note. Say that, rather than quietly
   picking a winner.

Case 3 is reported alongside the content questions in Step 9, because like them
it is something only the user can settle.

## Step 7: rewrite -- never dispatched

Apply the accepted wording fixes here, in this context. **The rewrite step is
never delegated.** Rewriting is where invention happens, so it stays in the one
place that has read `docs/rewrite-rules.md`, `docs/voice.md` and the user's own
`writing-style.md`.

- Apply `docs/rewrite-rules.md` in full. The ask, the stance, the confidence
  level, the owners, the timing and how blocking it is all survive untouched.
- Apply `docs/voice.md`, layered under the user's `writing_style` file if one
  resolves (`profile.personas` and `profile.writing_style` per
  `config-contract.md`). A missing `writing-style.md` gets one notice, then the
  default voice alone.
- A rule that cannot be honoured is named in the report, never broken silently.

## Step 8: cycle 2 -- re-check once

**Re-dispatch only the reviewers that raised something in cycle 1**, against the
revised draft. They confirm resolved or restate.

- New wording findings are adjudicated and applied the same way.
- New content findings join the questions list.
- **Zero wording findings in cycle 1 skips cycle 2 entirely.** There is nothing
  to re-read.

**The loop stops here. Two cycles, no exceptions.** After the first rewrite what
remains is almost always content, which no further cycle can fix. Collect it and
report it once rather than bouncing back at the user three separate times.

## Step 9: report

Verdict first, deliverable second, evidence third:

```
Verdict: needs 2 facts from you before it goes

<the revised message>

Needs you
1. [the fact-checker] The message says the migration "will take a while" --
   they need the actual window to plan around it. You have not stated one.
2. [substance check: attempts stated] The message asks priya to look at the
   failure but does not say what you already tried.

Reviewers: busy reader (always on), the executive (the ask lands with a
director), S (named in the draft)

Applied: 4 wording fixes across 2 cycles.
Conflict: R needs the rollback detail kept and M needs this under ten lines.
No fix serves both -- this may want to be two messages.
Learned: added S to ~/.claude/daikenja/personas.md.
```

The verdict line is `ready to send` or `needs <n> facts from you before it
goes`. Nothing else.

**Depth keys off `profile.tone`**, per `config-contract.md`:

| `tone` | What the report shows |
|---|---|
| `direct` | The six checks collapse to one line when they all pass. Only failures are itemised. |
| `standard` | Every check on its own line. Findings summarised without their anchors. |
| `guided` | All six checks, every finding with its anchor, and the reasoning behind each fix. |

**A clean draft produces a short report, not a padded one.** If every reviewer
returns nothing, say so plainly and hand back the draft unchanged.

## Step 10: learned personas

If the user described someone inline who has no entry in `personas.md`, route
that description to `/daikenja:remember-persona`, which is the only skill that
writes persona content. Pass on what the user actually said and nothing
inferred from the draft.

The write is silent and reported afterwards as the one-line `Learned:` line
above. A missing `personas.md` comes back as one line from that skill and this
one carries on -- it never blocks a review.

## When dispatch is unavailable

One notice line, then run the reviewers **in this context, sequentially**, one
brief at a time, and continue. Everything else is identical.

```
Subagents unavailable, running the reviewers in sequence.
```

This follows `config-contract.md`'s standing failure rule -- one notice, then
continue with reduced behaviour. Dispatch is a preference, not a dependency.

The cost is real and worth stating once here rather than apologising for it
later: a sequential reviewer has seen the ones before it and will defer to them.
Hold each brief separately and do not let a later reviewer soften a finding an
earlier one made.

## Failure cases

| Situation | What to do |
|---|---|
| No draft and no description given | Ask for one. Do not guess what the user wants to raise. |
| A description with no draft | Cycle 0 only. Report the verdict and hand off to `compose`. Never draft one here. |
| Subagent dispatch unavailable | One notice, then run the reviewers in sequence. |
| A finding arrives with no anchor | Discard it. An unanchored finding is noise. |
| A wording `Fix` introduces a fact not in the draft | Reclassify as content. Never apply it, and never write the fact in. |
| Every reviewer returns nothing | Report it plainly and hand back the draft unchanged. |
| `personas.md` absent | Silent. Archetypes only. |
| `daikenja.yaml` absent | Not fatal. Continue on the defaults; "already answered" falls back to whatever thread was pasted. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse, per `config-contract.md`. |
| No ledger at the resolved path | Not fatal. Report "already answered" as not checked and continue. |
| More addressees than persona slots | Direct beats cc'd. Name who was dropped. |
| Goal cannot be determined from the input | Ask the one question in Step 2. Do not guess. |
| The user asks for the message to be sent | Decline. This skill has no send action. |

## What this skill does not do

- It does not send, post or schedule anything.
- It does not draft a message from nothing. A description with no draft gets a
  verdict and a handoff to `/daikenja:compose`.
- It does not write `personas.md`. It routes through
  `/daikenja:remember-persona`, which owns every content write to that file.
- It does not write the ledger. It reads one for check 6 and nothing more.
- It does not invent a reviewer. The roster in `docs/reviewer-personas.md` is
  fixed and changes only by pull request.
- It does not run more than two cycles.
