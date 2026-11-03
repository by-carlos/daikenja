# Why Daikenja

[Home](../../README.md) · [Install](install.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · **Why**

> **In short:** most of a working week is reading what others wrote,
> answering it, and remembering what was settled. Daikenja helps with those
> three and stops there: it never acts for you, and everything it keeps is a
> plain file. If you want something that sends, schedules or edits on your
> behalf, it is the wrong tool.

## The problem

Three things go wrong again and again, and none of them is about writing
faster:

- **Answering the wrong question.** A long thread hides what is actually being
  asked, and the reply addresses something else.
- **A message that misfires.** The ask is buried, the tone lands wrong, or it
  re-asks something already settled -- and it cannot be unsent.
- **Forgetting what was decided.** Decisions live in threads, calls and
  people's heads. Three weeks later nobody can say what was agreed, by whom,
  or what replaced it.

## The idea

- **Understand before drafting.** `thread` refuses to write a reply until you
  have said where you stand, so the draft carries your position, not a
  plausible-sounding one.
- **Challenge before sending.** `preflight` reads a draft the way different
  readers will, and fixes wording without touching what you meant.
- **Record as you go, in plain text.** The ledger is a markdown file in the
  project. No database, no service, no account -- git versions it, and anyone
  can read it without Daikenja.
- **You stay the author.** Nothing is sent, posted or written without your
  explicit yes. Daikenja proposes; you decide.

## When not to use it

- **You want an agent that acts for you.** Daikenja never sends, posts,
  schedules or edits anything outside its own files. That is a design rule,
  not a missing feature.
- **You are not in Claude Code.** It does not run in Claude's Chat or Cowork
  tabs, or on claude.ai.
- **Your team needs one shared, access-controlled record.** The ledger is a
  file in a project; sharing it is sharing the project. The Slack bot answers
  from one person's ledgers, and a shared team bot has not been designed.
- **A one-line reply.** For a quick "thanks, done", the skills are more
  ceremony than help.

The full list of current edges is in
[Known limitations](../future-work.md).

## How it compares

| Instead of... | Daikenja differs because... |
|---|---|
| Asking Claude directly to "write a reply" | it first works out what is being asked and what you have committed to, and checks the draft against readers and the project's decisions |
| An AI writing tool that rewrites freely | it may change wording, never the ask, the stance or your confidence level |
| Architecture decision records (ADRs) or a wiki | the ledger is one line per decision, kept current as part of the conversation, with supersession tracked; it can point at your ADRs or wiki pages as sources |
| Meeting-notes AI | `meeting-review` proposes only what was actually closed out loud, with an owner who accepted it, and a quote for each |
