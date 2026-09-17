---
name: thread
description: Reads a Slack or email thread, summarizes what is being asked and by whom, then collects context from the user before any reply is drafted. Use when the user pastes a thread link or a block of chat history, or says "help me answer this". It gathers only and never writes the reply.
metadata:
  owner: Carlos
  version: 2
  pairs-with: compose
---

# Thread reply

Phase one of a two-phase workflow. This skill builds the picture. The
`compose` skill writes the message.

## Hard rule: do not draft

**Do not write a reply, a draft, or a suggested wording while this skill is
running.** Not even a short one. Not even if the answer looks obvious.

The real gate is the intent block in Step 5: never draft before it exists with
a real `Position` and a real `Ask`, both something other than `not stated`.
Until then, you gather and you wait, no matter how the user phrases it.

If you think you have enough to draft, say so in one line and stop:
"I think I have enough. Run /daikenja:compose when you are ready."

## Step 1: get the thread

- **A link was given.** Use the available Slack or email tools to fetch the full
  thread, including the parent message and every reply. Do not work from the
  permalink text alone.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **Nothing was given.** Ask for a link or a paste. Do not search for it.

If a fetch fails, say what failed and ask for a paste. Do not guess at the
content.

## Step 2: summarize it

Keep this to about 5 lines. The block below follows
`${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- read it before writing the
reply; the summary is the answer and nothing precedes it. § The second person
belongs to conversation decides whether `Waiting on` carries a name or `you`.

```
🧵 **Thread** -- [what it is about, who is in it, and how many messages]
❓ **Asking** -- [who is asking, and what they actually want]
🔓 **Open** -- [what is still undecided]
⏳ **Waiting on** -- [name: what is theirs]
📒 **Ledger** -- [what the project already has on this -- see Step 2b]
🌡️ **Tone** -- [neutral / tense / urgent -- only if it is not neutral]
```

**The `Thread` line is about the thread, never about how it arrived.** Lead
with what the thread is about, then who is in it, then the count. Never name
the input mechanism -- not `pasted block`, not `link`, not `forwarded` -- and
never state an absence. A channel that is not known is simply not mentioned;
`channel not stated` is a defect, not a disclosure.

**`Waiting on` names the person**, per `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md`
§ The second person belongs to conversation. In this reply, where there is one
reader, `you` is that person's name and is correct. In any form that leaves the
session, the name is written out.

**`Tone` is written in this reply only.** Any form that leaves the session omits
it, empty or not: it exists to feed the draft `compose` writes, and a consumer
that never reaches `compose` gains nothing from a bot publicly labelling
someone's message `tense`.

**The summary block is never wrapped in a code fence and never contains one**,
even when the thread itself quotes a fenced snippet -- a config block, a stack
trace, a code sample. A quoted line is named or restated inline, not fenced.

**A line that wraps onto a second line indents the continuation.** A second
line that starts at the margin, with no indent, ends the block for a
consumer that finds it by shape.

Attribution rules, because getting this wrong is expensive:

- Name who said what. Do not merge two people's positions into one.
- Separate a **question** from a **proposal** from a **decision**. If someone
  suggested something and nobody agreed, it is a suggestion, not a decision.
- If a position is ambiguous, say it is ambiguous. Do not resolve it for them.
- Quote sparingly and only when the exact wording matters.

**Do not flag ordinary workplace content.** Names, roles, opinions,
disagreements and performance concerns are the normal subject matter of a
thread the user is already part of. Handle them like any other content.

The one exception: if a credential, token, connection string or password appears
in the thread, say so in one line and never copy it forward. That is a security
matter, not a privacy one.

## Step 2b: place the thread

A thread is rarely the first thing a project has heard about its subject. If
the project keeps a ledger, what it already decided, what is still open, and
whether this thread contradicts any of it belongs in the summary -- otherwise
the user is asked to supply from memory what is already written down. This
step reads; it never writes. **`project-log` is the only skill that writes a
ledger, and nothing here changes that** -- a decision the thread seems to
make is reported here and logged, if at all, by the user through
`/daikenja:project-log` afterwards.

**Find the project**, in the order `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md`
§ Finding the project fixes, and stop at the first that resolves:

1. **A key the user named** -- "help me answer this, it's harbor" -- per
   `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0. Decisive; never falls
   back. An unknown key is reported with the registered keys and this step
   ends without a project.
2. **The current directory**, per `reading.md` § Step A. The user is standing
   in a project; that is the project.
3. **The thread's content**, per `${CLAUDE_PLUGIN_ROOT}/docs/project-card.md`
   § Resolving a project by content: the channel it came from, a tracker key
   or repository it names, then its subject against every registered card's
   Scope. A handle match is stated as a match; a Scope match is a candidate
   the user confirms before its ledger is read as theirs. Either way the
   `Ledger:` line says how the project was found -- `matched by
   #harbor-rollout`, or `confirmed by you` -- since the user did not name it
   and is not standing in it.

When a key or a directory resolved, still run the content check as a
**cross-check**: a decisive handle on a *different* project's card is
reported as a mismatch (`This thread is from #atlas-dev, which belongs to
atlas-migration, not to harbor`), and the summary goes on with the project
the user is in. The user may be answering a neighbouring project's thread on
purpose; the line makes sure it is on purpose.

**Read what the project has**, per `reading.md` § Step B and § Step C: resolve
the ledger path, read the Decisions and Open items sections, and read the
card beside the ledger if there is one. Then write the `Ledger:` line:

- **Decisions the thread touches** -- topic first, ID in parentheses, per
  `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md`.
- **Decisions the thread contradicts**, named as such: "contradicts the
  Saturday cutover decision (D-005)". A proposal in the thread that runs
  against a decision in force is the most useful thing this line can say.
- **Open items the thread bears on**, and whether the thread appears to
  resolve one -- reported as "appears to resolve", never as resolved, since
  only `project-log` can do that and only on the user's say-so.

```
📒 **Ledger** -- harbor (C:/GitHub/harbor/.daikenja/ledger.md): touches the ramp
cutover decision (D-001); the proposed Friday start contradicts its Monday
2026-08-17 date; appears to resolve the rollback-trigger question (O-001).
```

Keep it to one or two lines. Naming the project and the ledger path is what
makes the rest checkable, so both stay even when nothing matched:
`📒 **Ledger** -- harbor (C:/GitHub/harbor/.daikenja/ledger.md): nothing on this
subject.` is a complete, useful line.

**When no project resolved**, or the project has no ledger, leave the
`Ledger` line out and say nothing about it. A thread that is not project
work is the ordinary case, and `daikenja.yaml` being absent is not a reason
to narrate configuration in the middle of a thread summary. The only notice
this step ever adds on its own is the mismatch above.

## Step 3: get the user's position

You cannot write a reply for someone whose position you do not know. If the user
has not said what they want to happen, ask. Keep it to 1 or 2 questions:

- What outcome do they want from this reply?
- Is there a position they are holding, or are they asking a question?

Do not ask more than two questions at a time. Do not ask about tone yet.

## Step 4: keep gathering

The user will keep adding context over several messages -- background, history
with the people involved, constraints, things that happened offline, links to
other threads.

Each time:

- Fold it into what you already have.
- Say in one line what changed, if anything material changed.
- If the new information contradicts the thread, point that out.
- If the new information contradicts a ledger decision Step 2b read, point
  that out too, naming the decision. Do not log anything -- offer
  `/daikenja:project-log` once if the user seems to be making a new decision,
  and leave it there.
- If something is still missing that would change the reply, name it once. Do
  not keep asking.

Do not restate the whole summary every turn.

## Step 5: hand off

When the user invokes `/daikenja:compose`, or says in plain words that they are
ready ("draft it", "go ahead", "that's everything"), produce the intent block
below, then follow that skill. Do not produce this block earlier.

```
INTENT BLOCK
Audience: [who reads it -- peer / manager / leadership / engineers / external]
Channel: [#channel name, DM, or email]
Goal: [inform / request / state a decision / push back]
Position: [what the user is actually saying, in their words where possible]
Ask: [the single thing the reader should do, and by when if stated]
Constraints: [anything that limits the wording]
Risks: [escalation, HR, security, or a technical claim worth checking]
```

Anything not established goes in as `not stated`. Do not fill a gap with a guess.
If `Position` or `Ask` is `not stated`, ask for it before drafting.

A decision Step 2b found the thread contradicts, and the user did not
address, goes under `Risks` -- "the reply runs against the Saturday cutover
decision (D-005)" -- so `compose` carries it into the draft's caveats rather
than losing it at the handoff.

## What this skill does not do

- It does not write the ledger, the project card or `daikenja.yaml`. Step 2b
  reads; `/daikenja:project-log` writes, on its own approval.
- It does not register a project it could not resolve, and it does not
  create a card for one that has none. `/daikenja:setup-project` does both.
- It does not draft. That rule is at the top of this file and Step 2b does
  not soften it.
