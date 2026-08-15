---
name: preflight
description: Decides whether a message is worth sending as it stands, before any rewriting happens. Takes either a pasted draft or a plain description of what you want to raise with nobody drafted yet, and returns a verdict, not a message. Use for "should I even raise this", "is this worth sending", "am I missing something before I send this", "does this have enough to go on", or "is this ready to go" -- questions about substance, not wording. Not for making a message read better or land calmer (that is /daikenja:compose, which also runs these same checks silently before it drafts). If you already have wording you want improved, use /daikenja:compose instead.
metadata:
  owner: Carlos
  version: 1
  pairs-with: compose
---

# Preflight

A pre-send substance check. Given a draft, or just a plain description of what
someone wants to ask or raise, decide whether it has enough in it to be worth
sending -- not whether the wording is good. This skill never rewrites and
never sends anything. It returns a verdict.

## Step 0: read the shared doc

Read `${CLAUDE_PLUGIN_ROOT}/docs/substance-checks.md` before doing anything. Do
not work from memory of it. This skill implements that document; it does not
restate the checks here.

## Step 1: take the input as given

Two input shapes, both valid:

- **A pasted draft.** Evaluate the draft as written.
- **No draft.** A plain description of what the user wants to ask or raise
  ("should I even bring up that the migration slipped again?"). Evaluate the
  substance of that description. There is nothing to rewrite here, and this
  skill does not draft one -- see Step 5.

Do not invent or fill in anything not present in the input. If something a
check needs is genuinely absent from what was given, that is a fail on that
check, not something to guess at.

## Step 2: determine the goal

The checks in `substance-checks.md` apply only when the goal is a `request` --
asking someone to do, decide, or answer something. If the goal is obvious from
the input (a clear ask, or clearly just an announcement or FYI), use it.
Otherwise ask one short question: "Is this asking someone to do or decide
something, or just informing them?"

- **Not a request** (announcement, FYI, status update). Say so and stop -- the
  substance checks do not apply. Verdict: nothing to check, send when ready.
- **A request.** Continue to Step 3.

## Step 3: run the six checks

Run all six checks from `docs/substance-checks.md` against the input from
Step 1.

For check 6, **already answered**, only check material this skill can
actually see:

- A pasted thread or conversation, if one was given alongside the draft or
  description.
- The project's ledger, if a project is configured and a ledger is found
  (`~/.claude/daikenja/daikenja.yaml`, resolved per `docs/config-contract.md` §
  Resolution order; `.daikenja/ledger.md` if unconfigured). Read it the way
  `docs/reading.md` § Step A-C describes, for lookup only -- this skill never
  writes to it.

If neither is available, say so plainly rather than implying a broader check
happened: "Already answered: not checked -- no thread or ledger was
available to check against." That is not a pass and not a fail; it is an
honest gap, and it is reported alongside the other five, not silently skipped.

## Step 4: the verdict

Report every check, pass or fail, one line each. Then one overall line.

```
Context included: pass
Attempts stated: fail -- the message asks for help but does not say what was
already tried.
Options considered: not applicable -- this is not a decision request.
One specific question: pass
Right audience: fail -- addressed to the whole channel; only priya owns this.
Already answered: not checked -- no thread or ledger was available to check
against.

Verdict: needs work before you send it -- two checks failed above.
```

If every applicable check passes:

```
Context included: pass
Attempts stated: pass
Options considered: not applicable -- this is not a decision request.
One specific question: pass
Right audience: pass
Already answered: pass -- no matching decision or open item found in the
project ledger.

Verdict: ready to send.
```

Report every failing check, not just the first, per `substance-checks.md`'s
reporting rule. Never invent the missing piece to turn a fail into a pass.

## Step 5: this skill never blocks or drafts

There is nothing for this skill to block -- it has no send action and no draft
to withhold. It always finishes with a verdict, even when every check fails.

If the verdict has any fails and the user wants the message written or
rewritten, hand off: "Run `/daikenja:compose` when you want this drafted." Do
not draft it here, even a rough version -- that is `compose`'s job, and it
runs these same checks again on its own as a silent pre-flight.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Not fatal. Continue; "already answered" falls back to whatever thread was pasted, or is reported as not checked. |
| `daikenja.yaml` malformed | Stop. Name the first line that does not parse, per `config-contract.md`. |
| No ledger at the resolved path | Not fatal for this skill (it is not the ledger's writer or its dedicated reader). Report "already answered" as not checked and continue with the other five. |
| Goal cannot be determined from the input alone | Ask the one question in Step 2. Do not guess. |
