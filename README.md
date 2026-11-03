# Daikenja

**Not an assistant -- a sage you consult. It knows your work, the work around
you, and where to go next.**

Daikenja is a plugin for Claude Code. It reads the threads, documents and
meetings you are buried in, asks what you are actually trying to do, and hands
back something you can act on: a reply you can send, a verdict on a draft, or
a plain markdown **ledger** -- a project's running record of what was decided
and what is still open.

It never sends, never publishes, and never writes a word you did not ask for.
You copy the result out and send it yourself.

**Status:** in active development.

## How it works

[![The Daikenja loop in four steps. Read: you paste a thread and Daikenja asks what only you know. Draft: it writes the reply and can challenge it before you send. Record: it proposes ledger lines and waits for your yes. Come back: weeks later it tells you what changed.](docs/diagrams/how-it-works.svg)](docs/diagrams/how-it-works.svg)

A colleague drops a long thread on you and wants an answer today:

1. **Read.** `/daikenja:thread` tells you what is actually being asked and by
   whom, then asks you the few things only you know.
2. **Draft.** `/daikenja:compose` writes the reply in your words, with your ask
   and your stance intact. For a message you cannot afford to get wrong,
   `/daikenja:preflight` puts it in front of reviewers who each look for a
   different failure, and hands back a revised draft.
3. **Record.** The thread settled two things. `/daikenja:project-log` shows you
   the exact ledger lines it wants to add and waits for your yes.
4. **Come back.** Three weeks later, `/daikenja:project-catchup` tells you what
   was decided while you were away, what is still open, and who owes it.

## Is it for me?

| You want to... | Use | Read |
|---|---|---|
| Answer a thread without missing what is really being asked | `thread`, then `compose` | [Writing](docs/guide/writing.md) |
| Check a message you cannot afford to get wrong | `preflight` | [Writing](docs/guide/writing.md) |
| Keep a record of what a project decided, beside its code | `project-log` | [Ledger](docs/guide/ledger.md) |
| Catch up on a project after time away | `project-catchup` | [Ledger](docs/guide/ledger.md) |
| Turn a meeting transcript into decisions and action items | `meeting-review` | [Reviewing](docs/guide/reviewing.md) |
| Check a document or thread against what was already decided | `judgement` | [Reviewing](docs/guide/reviewing.md) |
| Have a team thread answered without leaving Slack | the optional Slack bot | [Slack bot](docs/guide/slack-bot.md) |
| Have something send, post or edit on your behalf | **Not this.** It drafts and records; you send. | [Why](docs/guide/why.md) |

## Install

Needs the **Claude Code CLI** or the **Code** tab of the **Claude Desktop
app**. It does not run in Chat, Cowork or claude.ai.

**Claude Desktop app**, no terminal: click **+** next to the prompt box, then
**Plugins** > **Add**, type `by-carlos/daikenja` and click **Sync**. Then click
**+** on the Daikenja card under the **Code** tab.

**Claude Code CLI**, from inside a session:

```
/plugin marketplace add by-carlos/daikenja
/plugin install daikenja@daikenja
```

Screenshots, updating, and what to do when it does not show up:
[Install and update](docs/guide/install.md).

## What it keeps, and where

The plugin adds no hooks and runs nothing in the background. It never sends a
message or posts anything; the one exception is the optional Slack bot, which
you run yourself and which posts only as its own Slack app. Everything
Daikenja writes is a plain file you can open:

- **Your settings and notes** -- your profile, how you write, what you told it
  about the people you write to -- live in `~/.claude/daikenja/` on your
  machine, or in a `daikenja` folder in your own Google Drive if you choose
  that.
- **A project's ledger** lives in the project, at `.daikenja/ledger.md` by
  default, where git versions it beside the code.

Every file, and which skill writes it: [Where your data lives](docs/guide/your-data.md).

## Try it in five minutes

1. Run `/daikenja:setup-user`. It checks your environment and writes your
   settings. Once per person.
2. Run `/daikenja:thread` and paste a real thread you owe an answer to. It
   tells you what is being asked and asks what only you know. Nothing is
   drafted yet.
3. Answer its questions, then run `/daikenja:compose` for the draft.
4. When you want a project's decisions kept, run `/daikenja:setup-project` in
   its directory. Once per project.

## Commands

| To... | Run | Or just say |
|---|---|---|
| Understand a thread before replying | `/daikenja:thread` | "help me answer this" |
| Draft or rewrite a message | `/daikenja:compose` | -- |
| Challenge a draft before sending | `/daikenja:preflight` | -- |
| Remember how a colleague reads | `/daikenja:remember-persona` | "remember that S challenges every claim" |
| Learn your writing style from samples | `/daikenja:learn-voice` | -- |
| Record a decision or open item | `/daikenja:project-log` | "log this", "record this decision" |
| See what changed in a project | `/daikenja:project-catchup` | -- |
| Get a full project overview | `/daikenja:project-summary` | -- |
| Look up a past decision | `/daikenja:project-decisions` | -- |
| Find open items nobody owns | `/daikenja:project-gaps` | -- |
| See which tracked documents moved | `/daikenja:project-sources` | -- |
| List every project | `/daikenja:project-list` | -- |
| Turn a transcript into ledger entries | `/daikenja:meeting-review` | "what came out of this call?" |
| Review a document before sharing | `/daikenja:doc-review` | "review this doc" |
| Check claims against the ledger | `/daikenja:judgement` | "is this right?" |
| Get coaching on how you handled a thread | `/daikenja:self-review` | -- |
| Set yourself up, or a project | `/daikenja:setup-user`, `/daikenja:setup-project` | -- |
| Install the Tensei conversation persona | `/daikenja:tensei` | -- |

A dash means the skill runs only when you type it. That is deliberate: those
skills write files, or are ones you would not want firing on their own.
Typing the command always works.

## Documentation

| Page | Read it when... |
|---|---|
| [Install and update](docs/guide/install.md) | you are installing or updating, or it is not showing up |
| [Writing a reply](docs/guide/writing.md) | you have a message to answer, draft or check |
| [The project ledger](docs/guide/ledger.md) | you want decisions kept, or need to know what was decided |
| [Reviewing things](docs/guide/reviewing.md) | you have a transcript, a document or a thread to check |
| [Tensei](docs/guide/tensei.md) | you want Claude's everyday answers shorter and headline-first |
| [Where your data lives](docs/guide/your-data.md) | you want to know what is stored, where, and who can see it |
| [The Slack bot](docs/guide/slack-bot.md) | your team wants answers inside Slack |
| [FAQ](docs/guide/faq.md) | something did not behave the way you expected |
| [Why Daikenja](docs/guide/why.md) | you are deciding whether it fits how you work |
| [Upgrading](docs/upgrading.md) | a skill told you to re-run setup after an update |

## Contributing

Bugs and ideas go to [the issue tracker](https://github.com/by-carlos/daikenja/issues).
A problem with the marketplace listing itself belongs in
[`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins),
which owns the catalog.

[`CONTRIBUTING.md`](CONTRIBUTING.md) has the rest: how to load the working
tree, what an issue needs, the branch and commit conventions, and when a change
owes a changelog entry or an upgrade note. Read it before opening a pull
request.

**Do not report a security problem in a public issue.**
[`SECURITY.md`](SECURITY.md) says how to reach the maintainer privately.

## License

[FSL-1.1-ALv2](LICENSE) -- free for any use except building a competing
commercial product, and each release becomes Apache-2.0 two years after it is
made available. Versions released before this change remain MIT.
