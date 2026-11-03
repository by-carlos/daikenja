# Writing a reply

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · **Writing** · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** `thread` works out what a thread is asking and what you need to
> decide, `compose` writes the message, and `preflight` challenges a draft you
> cannot afford to get wrong. None of them sends anything. Two more skills
> teach Daikenja how you write and how the people you write to read.

| You have... | Run |
|---|---|
| A thread you owe an answer to | `/daikenja:thread`, then `/daikenja:compose` |
| Your own rough draft to tidy | `/daikenja:compose` |
| A draft that cannot go wrong | `/daikenja:preflight` |

## Understand the thread first: `thread`

`/daikenja:thread` reads a Slack or email thread and tells you what is being
asked, by whom, and who is waiting on what. Then it asks you what only you
know: what you have already promised, what you will not commit to.

**Paste the thread text** -- that always works. A link works only if your
Claude Code session is connected to Slack or your email; if fetching it fails,
it says so and asks for a paste.

**It does not draft.** That is the point: a reply drafted before you have said
where you stand is a reply in someone else's words. Add the word `message` --
`/daikenja:thread message` -- to get the summary written for a channel instead,
with people named rather than "you"; that form stops at the summary.

## Draft or rewrite: `compose`

`/daikenja:compose` drafts a work message, or rewrites one you wrote, for
Slack, Teams or email. It keeps it clear, calm and easy to read **without
changing the ask, the stance or your confidence level**. Afterwards you can ask
for a firmer or a softer version; the ask, the owner and the timing stay the
same either way.

For a request, it also runs the six
[substance checks](#challenge-a-draft-before-it-goes-out-preflight) and names
any that fail beside the draft. It never holds the draft back.

## Challenge a draft before it goes out: `preflight`

`/daikenja:preflight` is for the message you cannot afford to get wrong:

1. **Substance checks.** Six questions every request has to pass: enough
   context to act on, what you already tried, the options framed, one
   specific question, the right person, and not already answered elsewhere.
2. **Reviewers.** It puts the draft in front of several readers, each looking
   for a different failure: the busy reader, the fact-checker, the risk reader,
   the executive, the tone-sensitive reader, and others. Up to two of the
   people the draft is addressed to join them, using what you have told
   Daikenja about them.
3. **Rewrite.** It fixes the wording problems they raise.
4. **Re-check.** The reviewers look once more at what changed, then you get
   the revised draft plus the facts only you can supply.

**It changes wording, never content.** If a fix would need a fact the draft
does not have, it asks you instead of inventing one. The reviewers and their
rules are in [`reviewer-personas.md`](../reviewer-personas.md); the six checks
in [`substance-checks.md`](../substance-checks.md).

## Teach it how you write: `learn-voice`

Out of the box, Daikenja drafts in a plain, calm default voice
([`voice.md`](../voice.md)). `/daikenja:learn-voice` replaces the parts of it
you would write differently, by working out your style from samples you
supply.

- It reads only samples you say you wrote yourself.
- It records style, never facts about people or projects.
- It backs up your current `writing-style.md` to a dated copy, then writes the
  whole file **without a preview** -- the backup is your undo.
- What it noticed but kept out of the file comes back as a separate "what to
  watch" report, saved so the next run can show what moved.

Run it whenever you have more samples, not only at setup.

## Remember how someone reads: `remember-persona`

A **persona**, in Daikenja, is your notes on one real person you write to: "S
challenges every technical claim", "the director reads only the first line".
Say it while drafting, or run `/daikenja:remember-persona`, and later drafts
and `preflight` reviews are written for that reader.

It is the only skill that writes persona notes, and a note for someone new can
be added without asking -- see
[When it asks first](your-data.md#when-it-asks-first). The notes stay in your
own files and are never written into a project.
