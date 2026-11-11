# Your data

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · **Your data** · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** Daikenja has no server of its own. It keeps plain files: your
> personal ones in your home folder (or your own Google Drive, if you opt in),
> and a project's ledger in the project's git repository, shared with whoever
> can read it. What a skill reads is processed by Claude, as in any Claude Code
> session. It never sends a message or posts anything for you.

[![Three places Daikenja keeps files. Your machine: settings, persona notes, writing style, glossary, Tensei and backups, private to you. Your Google Drive, only if you opt in: persona notes or writing style. The project's git repository: the ledger, DECISIONS.md at the root and .daikenja/open.md, plus the optional project card, shared with everyone who can read the repository, with git keeping the history. Anything a skill reads is also processed by Claude.](../diagrams/where-data-lives.svg)](../diagrams/where-data-lives.svg)

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
| A project's ledger (`DECISIONS.md` and `.daikenja/open.md`) and project card, in the project's repository | **Everyone who can read the repository** -- the whole world, if it is public. A local repository you never push stays on your machine |

**Persona notes are about real colleagues.** Keep them factual, write them as
you would want them read, and check whether your organization treats notes
about colleagues as personal data.

**Before you log something, remember a project's ledger is shared.** Write an
entry the way you would write a commit message, for the whole team. A replaced
decision or a closed item disappears from the file but stays in the git history
once committed -- rewriting or moving the ledger later does not remove what was
already committed. `project-log` never commits: you decide when an edit
enters the history.

## When it asks first

- **The ledger, the project card and your settings change only on your yes.**
  Every ledger change goes through `project-log`, which shows the exact lines
  first and never commits them; `meeting-review`, `setup-project` and `project-sources` only propose.
  `project-catchup` asks before moving your checkpoint.
- **Two personal files are the exception:**
  - `remember-persona` adds a note for someone new as soon as you describe
    them, and tells you after (it asks first if you described them alongside
    something you pasted). Changes to anything you wrote yourself wait for
    your yes.
  - `learn-voice` rewrites your writing style in one go, after saving a dated
    backup of the old one.
- **`tensei`** asks once, "Adopt this way of working?", before writing its
  file or changing your `CLAUDE.md`.

## Every file, and who writes it

`~` is your home folder: `C:\Users\<you>` on Windows, `/Users/<you>` on a Mac.
The `.claude` folder in it is hidden by default; you can also ask Claude to
open any of these files for you.

| What | Where | Written by |
|---|---|---|
| Your settings: who you are, registered projects, checkpoints (one commit per repository) | `~/.claude/daikenja/daikenja.yaml` (a plain-text settings file) | `setup-user`, `setup-project`; `project-catchup` for the checkpoint only |
| Your notes on the people you write to | `~/.claude/daikenja/personas.md`, or `daikenja/personas.md` in your Google Drive | you, plus `remember-persona` |
| How you write | `~/.claude/daikenja/writing-style.md`, or `daikenja/writing-style.md` in your Google Drive | you, plus `learn-voice`; `setup-user` appends the stance-check lines, only on your yes |
| Backups of your writing style, and what `learn-voice` noticed but kept out | `~/.claude/daikenja/writing-style.*.md`, dated | `learn-voice` |
| Your domain glossary -- a reference you keep by hand; no skill reads or writes it | `~/.claude/daikenja/glossary.md` | you; `setup-user` creates the blank file |
| Tensei, if you adopted it | `~/.claude/daikenja/tensei.md` and `.tensei-manifest.json`, plus one line in `~/.claude/CLAUDE.md` | `tensei` |
| Tensei backups | `~/.claude/backups/tensei-<timestamp>/` | `tensei` |
| A project's decisions in force | `DECISIONS.md` at the root of each of the project's repositories -- see note | `project-log` only; never committed for you |
| A project's open items, context links and sources | `.daikenja/open.md` in the project's home repository | `project-log` only; never committed for you |
| A project's card | `.daikenja/project.md` in the home repository | `setup-project`, when you accept it |
| The backup of a ledger in the old format | `ledger.<date>.bak.md` beside where the old ledger was | `setup-project`, when it migrates the project |
| The Slack bot's settings and log, if you run it | `~/.claude/daikenja/bot.yaml`, plus a log file wherever you point `--log-file` | you write `bot.yaml`; the bot writes the log |

**Ledger location note.** The two files sit at fixed places; there is no
setting to move them. For a project spanning several repositories, each has its
own `DECISIONS.md`, and `open.md` is in the home repository, the first one
registered. Every project lives in a git repository: projects without a folder
are gone, and an old one is migrated into a folder you choose -- see
[Moving from the old ledger](ledger.md#moving-from-the-old-ledger).

Backups are kept until you delete them. Nothing personal is stored in the
plugin's own folder, which is replaced on every update. The plugin ships blank
starting points in its `templates/` folder; they are copied out once, and the
copies are your live files.

## Google Drive, if you want it

**Local files are the default; Google Drive is opt-in.**

- **What can go there:** persona notes, your writing style, or both -- each is
  your own choice. The ledger is not part of this choice.
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
