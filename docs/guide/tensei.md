# Tensei

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · **Tensei** · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** optional. Makes Claude's everyday answers headline-first and
> labelled, in every Claude Code session on your computer -- not only
> Daikenja's. `/daikenja:tensei` installs, updates and removes it, and asks
> before changing anything.

## What it changes

Tensei shapes **how Claude talks to you**. What it writes for others --
messages, documents, ledger lines, commit text -- keeps following its own
rules, with one exception: anything a person will read must make sense without
the earlier conversation.

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

Run `/daikenja:tensei`. It needs no other Daikenja setup.

**What it changes on your computer.** It saves the persona as `tensei.md` in
your Daikenja folder (`~/.claude/daikenja/`), and adds one line to the end of
your personal Claude instructions file, `~/.claude/CLAUDE.md`, so every session
loads it. It shows you what it is about to do and asks first.

**Your edits are safe.** Unlike your other Daikenja files, Tensei is content
the plugin keeps improving. Running the skill again offers the newer version,
but:

- a copy you have not edited can be updated to the new one;
- a copy you **have** edited is never overwritten without asking;
- anything replaced is backed up first, under `~/.claude/backups/`.

**Removing it.** Run `/daikenja:tensei` and ask to remove it. It backs up the
persona and your `CLAUDE.md`, offers to delete the persona, and takes out the
line it added -- a line you wrote by hand is left alone.

It runs only when you type the command: a skill that edits the instructions
file every session reads should never start on its own.
