# Reviewing things

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · **Reviewing** · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** four skills that read something and report on it, without
> rewriting it. A meeting transcript becomes proposed ledger entries; a
> document gets a checklist review; a thread or page is checked against what
> the project already decided; and a thread you took part in gets private
> coaching on your own moves.

| You have... | Run | You get back |
|---|---|---|
| A meeting transcript | `/daikenja:meeting-review` | Decisions, action items and open questions, proposed for the ledger |
| A document you are about to share | `/daikenja:doc-review` | A list of findings against a fixed checklist |
| A thread or page making claims | `/daikenja:judgement` | Which claims the ledger settles, which are plain fact, which are presented as settled but not established |
| A thread you were part of | `/daikenja:self-review` | Private coaching on how you handled it |

## Meeting transcripts: `meeting-review`

Paste a transcript, or ask what came out of a call. `meeting-review` sorts what
was said into decisions, action items with owners and dates, and questions left
open. Decisions become ledger decisions; action items and open questions both
become open items. It then asks whether to log them, and on your yes
`project-log` shows the exact lines and waits for a second yes.

It is strict about what counts:

- **A suggestion is not a decision.** Something is settled when it was closed
  out loud and nobody objected.
- **It never invents an owner.** An action item belongs to whoever accepted it.
- **It reports positions, not behaviour.** Who talked over whom is not its
  business.
- Every item keeps the speaker and a short quote, so you can challenge any call
  it made.

## Documents: `doc-review`

`/daikenja:doc-review`, or "review this doc", checks a document before you
publish or share it: unclear sentences, hard reading for non-native speakers,
undefined terms, rules nobody enforces, undated decisions, missing owners,
contradictions, and content that is stale on its face.

**It reports and never rewrites.** A clean document gets a short report, not a
padded one.

## Claims against the ledger: `judgement`

`/daikenja:judgement`, or "is this right?", takes a thread or a document and
tells you three things: which parts a recorded decision already settles, which
are plain fact, and which are presented as settled without being established.

By default it answers you in the conversation. Add the word `message` --
`/daikenja:judgement message` -- to get a shareable "AI review summary" to paste
into a pull request or a channel instead. Either way it is read-only: no reply drafted, nothing
logged.

## Your own part in a thread: `self-review`

`/daikenja:self-review` looks at a thread you took part in and coaches you on
your own moves, with evidence from the thread.

- **Every finding is about you.** Other people appear only as the situation you
  were responding to, never as the subject of a finding.
- **It builds findings only from what you could see.** Nothing from a private
  channel you were not in is quoted to you.
- **It writes nothing** and produces nothing you could paste anywhere.

It runs only when you type it.
