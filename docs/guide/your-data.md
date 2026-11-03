# Your data

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · **Your data** · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** Daikenja has no server of its own. It keeps plain files: your
> personal ones in your home folder (or your own Google Drive, if you opt in),
> and a project's ledger in the project, shared with whoever can read the
> project. What a skill reads is processed by Claude, as in any Claude Code
> session. It never sends a message or posts anything for you.

[![Three places Daikenja keeps files. Your machine: settings, persona notes, writing style, glossary, Tensei and backups, private to you. Your Google Drive, only if you opt in: persona notes or writing style. The project: the ledger and project card, shared with everyone who can read the project. Anything a skill reads is also processed by Claude.](../diagrams/where-data-lives.svg)](../diagrams/where-data-lives.svg)

## What leaves your machine

- **To Claude (Anthropic).** Daikenja runs inside Claude Code. Whatever a skill
  reads -- a thread you paste, a document, your persona notes, the ledger --
  becomes part of your Claude Code conversation and is processed by Claude,
  under your own Claude account's terms and your organization's settings.
  Daikenja cannot change those. `preflight` also hands the draft and persona
  notes to its reviewers, which are further Claude calls in the same session.
- **To Google**, only if you keep persona notes or your writing style in
  Google Drive. They are then stored by Google under your account and your
  organization's Drive policy.
- **To Slack or other tools you connected**, only as reads: a skill fetches a
  thread or page through a connector you set up in Claude Code, with your own
  access.
- **Nothing to the plugin author.** There is no Daikenja server, account or
  telemetry.

It never sends a message or posts anything for you. The one exception is the
optional [Slack bot](slack-bot.md), a separate program you run yourself, which
posts as its own Slack app.

## Who can see what

| File | Who can read it |
|---|---|
| Your settings, persona notes, writing style, glossary | **You**, on your machine -- or in your own Google Drive, if you moved persona notes or writing style there, with whoever you share that folder with |
| A project's ledger and project card, in the project's folder | **Everyone who can read the project.** In a git repository, everyone with access to it -- the whole world, if the repository is public |
| The ledger of a project with no folder, in your own Daikenja folder | **You**, unless you chose a shared location |

**Persona notes are about real colleagues.** Keep them factual, write them as
you would want them read, and check whether your organization treats notes
about colleagues as personal data.

**Before you log something, remember a project's ledger is shared.** Write a
line the way you would write a commit message, for the whole team. Replaced
lines are marked, not deleted, and in a git repository every line stays in the
history -- moving the ledger later does not remove what was already committed.

## When it asks first

- **The ledger, the project card and your settings change only on your yes.**
  Every ledger line goes through `project-log`, which shows the exact lines
  first; `meeting-review`, `setup-project` and `project-sources` only propose.
  `project-catchup` asks before moving your checkpoint.
- **Two personal files are the exception:**
  - `remember-persona` adds a note for someone new as soon as you describe
    them, and tells you after (it asks first if you described them alongside
    something you pasted). Changes to anything you wrote yourself wait for
    your yes.
  - `learn-voice` rewrites your writing style in one go, after saving a dated
    backup of the old one.
- **`tensei`** asks before writing its file or changing your `CLAUDE.md`.

## Every file, and who writes it

`~` is your home folder: `C:\Users\<you>` on Windows, `/Users/<you>` on a Mac.
The `.claude` folder in it is hidden by default; you can also ask Claude to
open any of these files for you.

| What | Where | Written by |
|---|---|---|
| Your settings: who you are, registered projects, checkpoints | `~/.claude/daikenja/daikenja.yaml` (a plain-text settings file) | `setup-user`, `setup-project`; `project-catchup` for the checkpoint only |
| Your notes on the people you write to | `~/.claude/daikenja/personas.md`, or `daikenja/personas.md` in your Google Drive | you, plus `remember-persona` |
| How you write | `~/.claude/daikenja/writing-style.md`, or `daikenja/writing-style.md` in your Google Drive | you, plus `learn-voice` |
| Backups of your writing style, and what `learn-voice` noticed but kept out | `~/.claude/daikenja/writing-style.*.md`, dated | `learn-voice` |
| Your domain glossary | `~/.claude/daikenja/glossary.md` | you; `setup-user` creates the blank file |
| The Tensei persona, if you installed it | `~/.claude/daikenja/tensei.md` and `.tensei-manifest.json`, plus one line in `~/.claude/CLAUDE.md` | `tensei` |
| Tensei backups | `~/.claude/backups/tensei-<timestamp>/` | `tensei` |
| A project's ledger | `.daikenja/ledger.md` in the project's folder by default -- see note | `project-log` only |
| A project's card | `project.md` beside the ledger (`<name>.project.md` beside a ledger with another file name) | `setup-project`, when you accept it |
| The Slack bot's settings and log, if you run it | `~/.claude/daikenja/bot.yaml`, plus a log file wherever you point `--log-file` | you write `bot.yaml`; the bot writes the log |

**Ledger location note.** A project registered with `setup-project` can keep
its ledger elsewhere, including outside the project; a project with no folder
keeps it in `~/.claude/daikenja/ledgers/` by default. For a project spanning
several folders, the ledger is in the first folder registered.

Backups are kept until you delete them. Nothing personal is stored in the
plugin's own folder, which is replaced on every update.

## Google Drive, if you want it

**Local files are the default; Google Drive is opt-in.**

- **What can go there:** persona notes, your writing style, or both -- each is
  your own choice. The ledger never moves; it stays with the project.
- **How:** `setup-user` offers it once. It reaches Drive through Google's
  connector in Claude Code, under your own Google account, and works fine
  without it.
- **One folder.** Everything goes in one `daikenja` folder it creates,
  mirroring `~/.claude/daikenja/`. Nothing is left loose in your Drive.
- **`setup-user` has to create the file.** The connector only shows Claude
  files it created itself, so a document already in your Drive cannot be used,
  however you share it.
- **An unreadable Drive file stops the skill** rather than quietly carrying on:
  an unreadable file and an empty one look identical, and the alternative is
  drafting in the default voice while you think your own style was applied.
