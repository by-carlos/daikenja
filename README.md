# Daikenja

A Claude Code plugin that helps you answer long threads well and remember what
your projects decided.

**Not an assistant -- a sage you consult. It knows your work, the work around
you, and where to go next.**

Daikenja runs in **Claude Code** -- the **Code** tab of the Claude Desktop app,
or the `claude` command line. It reads the threads, documents and meetings you
are buried in, asks what you are actually trying to do, and hands back
something you can act on: a reply you can send, a verdict on a draft, or a
**ledger** -- two plain text files in the project's git repository, of what it
decided and what is still open, with git keeping the history.

It never sends a message or posts anything for you: you copy the result out and
send it yourself. (The optional [Slack bot](docs/guide/slack-bot.md), which you
run yourself, is the one thing that posts.) As in any Claude Code session, what
it reads is processed by Claude -- see [Your data](docs/guide/your-data.md).

**Status:** pre-1.0 and in active development -- see
[releases](https://github.com/by-carlos/daikenja/releases). A release that
changes something already on your disk says so; see
[Upgrading](docs/upgrading.md).

## How it works

[![The Daikenja loop in four steps. Read: you paste a thread and Daikenja asks what only you know. Draft: it writes the reply and can challenge it before you send. Record: it proposes ledger entries and waits for your yes, and writes them to DECISIONS.md and open.md in the project's git repository. Come back: weeks later you type a command and it tells you what changed.](docs/diagrams/how-it-works.svg)](docs/diagrams/how-it-works.svg)

A colleague drops a long thread on you and wants an answer today. Daikenja
**reads** it and asks where you stand, **drafts** the reply in your words,
**records** what the thread settled once you say yes, and weeks later tells you
what **changed** while you were away.

A decision in the ledger looks like this, in a `DECISIONS.md` file any text
editor opens:

```
- **Freeze schema changes on the events table until the rollout completes.** —
  two teams have pending migrations. Revisit: if the rollout date moves.
```

Every project lives in a git repository; projects without a folder are gone.
A notes folder works once `git init` has run in it, and nothing has to be
pushed. Coming from an earlier version? See
[Moving from the old ledger](docs/guide/ledger.md#moving-from-the-old-ledger).

## Is it for me?

| You want to... | Use | Read |
|---|---|---|
| Answer a thread without missing what is really being asked | `thread`, then `compose` | [Writing](docs/guide/writing.md) |
| Check a message you cannot afford to get wrong | `preflight` | [Writing](docs/guide/writing.md) |
| Keep a record of what a project decided | `project-log` | [Ledger](docs/guide/ledger.md) |
| Catch up on a project after time away | `project-catchup` | [Ledger](docs/guide/ledger.md) |
| Turn a meeting transcript into decisions and action items | `meeting-review` | [Reviewing](docs/guide/reviewing.md) |
| Check a document or thread against what was already decided | `judgement` | [Reviewing](docs/guide/reviewing.md) |
| Get a thread summarised or checked without leaving Slack | the optional Slack bot | [Slack bot](docs/guide/slack-bot.md) |
| Have something send, post or schedule on your behalf | **Not this.** It drafts and records; you send. | [Why](docs/guide/why.md) |

Every command, and which ones you can just ask for in plain words:
[Commands](docs/guide/commands.md).

## Install

It runs only in Claude Code: a **local** session in the Desktop app's **Code**
tab, or the command line. It does not appear in the Desktop app's Chat or
Cowork tabs, or on claude.ai.

**Claude Desktop app**, no terminal: click **+** next to the message box, then
**Plugins** > **Add**, type `by-carlos/daikenja` and click **Sync**. The plugin
directory opens: switch to the directory's own **Code** tab (not the app's) and
click **+** on the Daikenja card.

**Command line** -- for developers; skip it if you use the Desktop app. From
inside a Claude Code session:

```
/plugin marketplace add by-carlos/daikenja
/plugin install daikenja@daikenja
```

Screenshots, updating, and what to do when it does not show up:
[Install and update](docs/guide/install.md).

## Try it in five minutes

1. **Open a session.** First make a new empty folder, for example `Daikenja`
   in your Documents. Then in the Desktop app, go to the **Code** tab, start a
   new **local** session and pick that folder. On the command line, run
   `claude`.
2. **Set yourself up.** Type `/daikenja:setup-user` in the message box and
   press Enter. It asks a few questions and writes your settings. Once per
   person.
3. **Answer a real thread.** Type `/daikenja:thread` and paste a thread you
   owe an answer to. It tells you what is being asked and asks what only you
   know. Nothing is drafted yet.
4. **Get the draft.** Answer its questions, then run `/daikenja:compose`.

Typing `/` in the message box lists every command you have installed.

## Your data

What a skill reads -- a thread you paste, a document, your own notes -- is
sent to Claude for processing, as in any Claude Code session. What Daikenja
writes are plain files: your settings and notes in your home folder (or your
own Google Drive, if you opt in), and a project's ledger, which everyone who
can read the project's repository can read. Every file, and what leaves your machine:
[Your data](docs/guide/your-data.md).

## Documentation

| Page | Read it when... |
|---|---|
| [Install and update](docs/guide/install.md) | you are installing or updating, or it is not showing up |
| [Commands](docs/guide/commands.md) | you want the full list, and what you can ask for in plain words |
| [Writing a reply](docs/guide/writing.md) | you have a message to answer, draft or check |
| [The project ledger](docs/guide/ledger.md) | you want decisions kept, or need to know what was decided |
| [Reviewing things](docs/guide/reviewing.md) | you have a transcript, a document or a thread to check |
| [Tensei](docs/guide/tensei.md) | you want Claude to answer headline-first, say how sure it is, and rank its options -- see the side-by-side example |
| [Your data](docs/guide/your-data.md) | you want to know what is stored, where, and what leaves your machine |
| [The Slack bot](docs/guide/slack-bot.md) | you want summaries and checks inside Slack |
| [FAQ](docs/guide/faq.md) | something did not behave the way you expected |
| [Why Daikenja](docs/guide/why.md) | you are deciding whether it fits how you work |

## Help and contributing

Questions, bugs and ideas go to
[the issue tracker](https://github.com/by-carlos/daikenja/issues) (a free
GitHub account is needed), or ask whoever recommended Daikenja to you. A
problem with the marketplace listing itself belongs in
[`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins),
which owns the catalog.

[`CONTRIBUTING.md`](CONTRIBUTING.md) has the rest: how to load the working
tree, what an issue needs, the branch and commit conventions, and when a change
owes a changelog entry or an upgrade note. Read it before opening a pull
request.

**Do not report a security problem in a public issue.**
[`SECURITY.md`](SECURITY.md) says how to reach the maintainer privately.

## License

Free for any use, including at work, except building a competing commercial
product. Each release becomes Apache-2.0 two years after it is made available.
Formally [FSL-1.1-ALv2](LICENSE); versions before 0.6.0 were released under
MIT.
