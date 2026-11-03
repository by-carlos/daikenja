# Commands

[Home](../../README.md) · [Install](install.md) · **Commands** · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** every Daikenja skill, what it is for, and whether you can just
> ask for it in plain words. Typing the command always works: type `/` in the
> message box and pick from the list.

Six skills also start when you describe what you want; the rest run only when
you type them. "Plain words" below shows a phrase that works; a dash means
type the command. When plain words stop working, see
[Install § When plain words do not start a skill](install.md#when-plain-words-do-not-start-a-skill).

## Writing

| To... | Command | Plain words |
|---|---|---|
| Understand a thread before replying | `/daikenja:thread` | "help me answer this" |
| Draft or rewrite a message | `/daikenja:compose` | -- |
| Challenge a draft before sending | `/daikenja:preflight` | -- |
| Remember how a colleague reads | `/daikenja:remember-persona` | "remember that S challenges every claim" |
| Learn your writing style from samples | `/daikenja:learn-voice` | -- |

More: [Writing a reply](writing.md).

## The ledger

| To... | Command | Plain words |
|---|---|---|
| Record a decision or open item | `/daikenja:project-log` | "log this", "record this decision" |
| See what changed since you last looked | `/daikenja:project-catchup` | -- |
| Get a full project overview | `/daikenja:project-summary` | -- |
| Look up a past decision | `/daikenja:project-decisions` | -- |
| Find open items nobody owns, or that sat too long | `/daikenja:project-gaps` | -- |
| See which tracked documents moved | `/daikenja:project-sources` | -- |
| List every project, and which one you are in | `/daikenja:project-list` | -- |

More: [The project ledger](ledger.md).

## Reviewing

| To... | Command | Plain words |
|---|---|---|
| Turn a transcript into ledger entries | `/daikenja:meeting-review` | "what came out of this call?" |
| Review a document before sharing | `/daikenja:doc-review` | "review this doc" |
| Check claims against the ledger | `/daikenja:judgement` | "is this right?" |
| Get coaching on how you handled a thread | `/daikenja:self-review` | -- |

More: [Reviewing things](reviewing.md).

## Setup

| To... | Command | Plain words |
|---|---|---|
| Set yourself up, once | `/daikenja:setup-user` | -- |
| Register a project, once per project | `/daikenja:setup-project` | -- |
| Adopt, update or remove Tensei, the Daikenja way of working | `/daikenja:tensei` | -- |

More: [Install and update](install.md#after-installing), [Tensei](tensei.md).

## Typing a word after the command

Some commands take a word after them:

- **A project name**, for the five reading commands (`project-catchup`,
  `project-summary`, `project-decisions`, `project-gaps`, `project-sources`):
  `/daikenja:project-summary atlas-migration` reads that project from any
  folder. The name is the one the project was registered under with
  `setup-project`; `/daikenja:project-list` shows them all. `project-log`
  does not take a name: run it from one of the project's folders.
  `setup-project` takes one to migrate a project still on the old ledger --
  `/daikenja:setup-user` tells you when.
- **`message`**: `/daikenja:thread message` writes the thread summary for a
  channel, and stops there -- no questions, no draft. `/daikenja:judgement
  message` writes the verdict for a channel or a pull request. Both name people
  instead of saying "you".
