# Where your data lives

[Home](../../README.md) · [Install](install.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · **Your data** · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** your personal files live in `~/.claude/daikenja/` on your
> machine, or in a `daikenja` folder in your own Google Drive if you opt in.
> A project's ledger lives in the project and is shared with whoever can read
> it. Daikenja has no server, sends nothing, and writes nothing without your
> approval.

[![Three places Daikenja keeps files. Your machine: settings, persona notes, writing style, glossary and Tensei, private to you. Your Google Drive, only if you opt in: persona notes or writing style. The project: the ledger and project card, shared with everyone who can read the project.](../diagrams/where-data-lives.svg)](../diagrams/where-data-lives.svg)

## Who can see what

| File | Who can read it |
|---|---|
| Your settings, persona notes, writing style, glossary | **Only you**, on your machine -- or your own Google Drive, if you moved persona notes or writing style there |
| A project's ledger and project card | **Everyone who can read the project.** In a git repository, that is everyone with access to the repository |

**Persona notes are about real colleagues, and they stay yours.** They are
never written into a ledger or a project. Keep them local, or in your own
Drive, and write them as you would want them read if they were ever seen.

**The ledger is shared by design.** Its entries name owners by handle and
record what was decided. Write a ledger line the way you would write a commit
message: for the whole team.

**What reaches the model.** Daikenja runs inside Claude Code. When a skill
reads a thread, a document or one of your files, that content becomes part of
your Claude Code conversation, handled like anything else you show Claude.
Daikenja itself has no server and adds no destination of its own.

## Every file, and who writes it

Nothing personal is stored in this repository, and nothing personal should ever
be written into the installed plugin directory -- plugin directories are managed
and get overwritten on update.

| What | Where | Written by |
|---|---|---|
| Profile, per-project settings, checkpoints | `~/.claude/daikenja/daikenja.yaml` | `setup-user` for your profile, `setup-project` for a project's entry, and `project-catchup` for the `last_checkpoint` key only |
| Your notes on the people you write to | `~/.claude/daikenja/personas.md`, or `daikenja/personas.md` in your Google Drive | you, plus `remember-persona` for people you describe to it |
| How you write | `~/.claude/daikenja/writing-style.md`, or `daikenja/writing-style.md` in your Google Drive | you, plus `learn-voice`, which backs up the file before replacing it |
| Your domain glossary -- one line per term you have had to explain | `~/.claude/daikenja/glossary.md` | you, plus any skill that glosses a term you defined for it, one dated line at a time |
| The Tensei persona, if you installed it | `~/.claude/daikenja/tensei.md`, plus one import line in `~/.claude/CLAUDE.md` | `tensei` |
| A project's decision ledger | `<project root>/.daikenja/ledger.md`, or wherever that project's `ledger:` key points -- including outside the project. For a project spanning several directories the root is the first one registered | `project-log` only |
| A project's card | beside the ledger, as `project.md` | `setup-project`, when you accept it |

The plugin ships blank starting points in `templates/`. Those get copied out to
your directories; the copies are the live files.

## Two rules every skill follows

- **One writer for the ledger.** Only `project-log` writes ledger content.
  `project-catchup` writes one setting, `last_checkpoint`, and never touches the
  ledger. `setup-project` and `meeting-review` propose entries, and every line
  still goes through `project-log` for your approval. Every other skill only
  reads.
- **You approve first.** A skill proposes, you confirm, then it writes.

## Google Drive, if you want it

**Local files are the default, and Google Drive is opt-in.** If you want your
persona notes or your writing style reachable from another machine, either one
can live in Google Drive instead. `setup-user` offers this once, works fine
without it, and never asks you to sign up for anything. Drive is reached through
Google's own connector, under your own account, so nothing goes through the
plugin author. The two settings are independent: keeping persona notes local
while sharing a writing style is a normal setup. The ledger does not move -- it
stays in the project.

Everything Daikenja puts in Drive goes in **one `daikenja` folder** it creates
for you, mirroring `~/.claude/daikenja/` on your machine. Nothing is left loose
at the top level of your Drive.

Two things to know before you choose Drive:

- **`setup-user` has to create the file.** The connector only shows Claude the
  files it created itself, so a document already in your Drive cannot be
  pointed at, however you share it.
- **A Drive file Daikenja cannot read stops the skill** rather than quietly
  carrying on. An unreadable file and an empty one look identical from here,
  and the alternative is drafting in the default voice while you think your
  own style was applied.
