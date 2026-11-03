# FAQ

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · **FAQ** · [Why](why.md)

> **In short:** most surprises come from three things -- being outside Claude
> Code, expecting plain words to start a command that has to be typed, or a
> Google Drive file Daikenja cannot read. Each answer below is short and links
> to the full story.

Jump to: [Install and setup](#install-and-setup) · [Privacy](#privacy) ·
[Using it](#using-it)

## Install and setup

### I installed it, but it does not show up.

It appears only in a **local** session of Claude Code -- not in the Desktop
app's Chat or Cowork tabs, a cloud session, or claude.ai. After installing or
updating, start a new session. [Where it runs](install.md#where-it-runs)

### I asked in plain words and nothing happened.

Most commands run only when you type them: `/daikenja:project-catchup`, not
"catch me up". [Commands](commands.md) shows the six that also answer to plain
words, and [why that can stop working](install.md#when-plain-words-do-not-start-a-skill).

### Do I have to re-run setup after an update?

Only when a skill prints a line telling you to.
[Do I have to re-run setup?](install.md#do-i-have-to-re-run-setup)

### Do I need git, or a code repository?

Not for writing and reviewing: those skills work anywhere. A project's ledger
needs git, but not code: a folder of notes works once `git init` has run in
it, which `setup-project` offers to do, and nothing has to be pushed.
[A project that is not code](install.md#a-project-that-is-not-code)

### Where did my project with no folder go?

Projects without a folder are gone. Skills report such a project as needing
migration; `/daikenja:setup-user` lists it with the command that moves its
ledger into a git repository you choose, with a dated backup of the old file.
[Moving from the old ledger](ledger.md#moving-from-the-old-ledger)

## Privacy

### Does it send or post anything?

It never sends a message or posts anything for you; the optional Slack bot,
which you run yourself, is the one exception. What a skill reads is processed
by Claude, as in any Claude Code session.
[What leaves your machine](your-data.md#what-leaves-your-machine)

### Who can see what I told it about a colleague?

You, and the Claude session that reads the notes when drafting -- plus Google
and anyone you share the folder with, if you keep them in Drive. They are
never written into a project.
[Who can see what](your-data.md#who-can-see-what)

### Who can see the ledger?

Everyone who can read the project's git repository -- and nobody else, if it
is a local repository you never push.
[Who can see what](your-data.md#who-can-see-what)

## Using it

### My writing style was not applied.

If your writing style lives in Google Drive and Daikenja cannot read it, the
skill stops rather than drafting in the default voice. Otherwise check the file
has content: `/daikenja:learn-voice` writes it from your samples.
[Google Drive, if you want it](your-data.md#google-drive-if-you-want-it)

### It answered about the wrong project.

Run `/daikenja:project-list` to see which project your folder resolves to, or
name the project: `/daikenja:project-summary atlas-migration`.
[Reading it back](ledger.md#reading-it-back)

### How is the ledger different from ADRs or a wiki?

An architecture decision record (ADR) or a wiki page is a full document per
decision; a `DECISIONS.md` entry is a sentence or two, kept current as the
decision changes. The two work together: an entry can link to its ADR.
[How it compares](why.md#how-it-compares)

### I logged something, but my colleagues cannot see it.

`project-log` writes the files and never commits them. Commit and push them
like any other change; until then, `project-catchup` lists them as "not
committed yet". [Writing to it](ledger.md#writing-to-it-project-log)

### Persona, reviewer, Tensei -- what is the difference?

- **A persona** is your notes on a real person you write to, kept by
  `remember-persona`. [Writing](writing.md#remember-how-someone-reads-remember-persona)
- **Reviewers** are the built-in readers `preflight` checks a draft against.
  [Writing](writing.md#challenge-a-draft-before-it-goes-out-preflight)
- **Tensei** is not a persona at all: it is the optional Daikenja way of
  working, for how Claude answers and works with *you*.
  [Tensei](tensei.md)
