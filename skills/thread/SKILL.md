---
name: thread
description: Reads a Slack or email thread, summarizes what is being asked and by whom, then collects context from the user before any reply is drafted. Use whenever the user pastes a Slack permalink or thread link, forwards an email thread, pastes a block of chat history, or says things like "what is this about", "help me answer this", "I need to reply to this thread". This skill gathers only -- it never writes the reply itself. The reply is produced later by the /daikenja:compose skill.
metadata:
  owner: Carlos
  version: 1
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
reply; the summary is the answer and nothing precedes it.

```
Thread: [channel or subject, and how many messages]
Asking: [who is asking, and what they actually want]
Open: [what is still undecided]
Waiting on you: [what, if anything, is yours]
Tone: [neutral / tense / urgent -- only if it is not neutral]
```

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
