# Tensei

[Home](../../README.md) · [Install](install.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · **Tensei** · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** Tensei is an optional persona for your everyday conversations
> with Claude -- every session, not only Daikenja's skills. Answers lead with
> the finding, stay short unless you ask for depth, and label their parts
> (Answer, Warning, Report...) so you can skim. `/daikenja:tensei` installs,
> updates or removes it.

## What it changes

Tensei shapes **how Claude talks to you**, never what it writes for others.
Messages, documents, ledger entries and commit text keep following their own
rules.

- **Headline first, then stop.** The first line carries the finding, complete
  enough to act on. The default answer is that line plus a few sentences; ask
  for more and you get full depth.
- **The cold-read test.** Every message makes sense to someone who read none
  of the earlier ones -- things are named in words, not "item 3" or "the point
  above".
- **Labelled parts.** A response with several parts marks each one, so a
  risk is never buried under an answer:

  ```
  💬 Answer:  the direct response
  ℹ️ Notice:  the premise is off, or something outranks the ask
  📋 Report:  what was done
  💡 Suggestion:  unprompted advice, offered once
  ⚠️ Warning:  a risk, always shown, never cut for brevity
  ❓ Query:  a question whose answer changes what happens next
  ```

- **Certain, likely or guessing.** It says which, and checks rather than
  stating a guess as fact.

The full text is [`templates/tensei.md`](../../templates/tensei.md).

## Install, update, remove

Run `/daikenja:tensei`. It needs no `daikenja.yaml` and no prior
`setup-user` run.

It writes the persona to `~/.claude/daikenja/tensei.md` and adds one import
line at the end of `~/.claude/CLAUDE.md`, which is what makes it apply to every
session on the machine. It shows you what it is about to do and asks first.

**Your edits are safe.** Unlike your other Daikenja files, Tensei is content
the plugin keeps revising. Re-running the skill offers the newer shipped
version, but:

- a copy you have not edited can be updated to the shipped one;
- a copy you **have** edited is never overwritten without asking;
- anything replaced is backed up first, under `~/.claude/backups/`.

**Removing it** backs up the file and your `CLAUDE.md`, deletes the persona,
and takes out the import line -- but only if the skill added that line itself.
A line you wrote by hand is left alone.

It runs only when you type the command: a skill that edits the `CLAUDE.md`
every session reads should never fire on its own.
