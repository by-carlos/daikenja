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

No. The writing and reviewing skills work anywhere, and a project with no
folder keeps its ledger wherever you choose.
[A project with no folder](install.md#a-project-with-no-folder)

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

Everyone who can read the project -- in a git repository, everyone with access
to it. A project with no folder keeps its ledger in your own files.
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
decision; a ledger line is one sentence, written as the decision happens. The
two work together. [How it compares](why.md#how-it-compares)

### Persona, reviewer, Tensei -- what is the difference?

- **A persona** is your notes on a real person you write to, kept by
  `remember-persona`. [Writing](writing.md#remember-how-someone-reads-remember-persona)
- **Reviewers** are the built-in readers `preflight` checks a draft against.
  [Writing](writing.md#challenge-a-draft-before-it-goes-out-preflight)
- **Tensei** is an optional persona for how Claude talks to *you*.
  [Tensei](tensei.md)
