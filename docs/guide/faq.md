# FAQ

[Home](../../README.md) · [Install](install.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · [Tensei](tensei.md) · [Your data](your-data.md) · [Slack bot](slack-bot.md) · **FAQ** · [Why](why.md)

Short answers, each with a link to the full story.

- **Install and setup:** [it does not show up](#i-installed-it-but-it-does-not-show-up) ·
  [plain language does nothing](#i-asked-in-plain-words-and-nothing-happened) ·
  [re-run setup?](#do-i-have-to-re-run-setup-after-an-update) ·
  [git required?](#do-i-need-git-or-a-repository)
- **Privacy:** [does it send anything?](#does-it-ever-send-or-post-anything) ·
  [notes on colleagues](#who-can-see-what-i-told-it-about-a-colleague) ·
  [what the ledger shares](#who-can-see-the-ledger)
- **Using it:** [my style was not applied](#my-writing-style-was-not-applied) ·
  [wrong project](#it-answered-about-the-wrong-project) ·
  [ledger vs ADRs](#how-is-the-ledger-different-from-adrs-or-a-wiki) ·
  [persona, three meanings](#persona-means-three-different-things)

## Install and setup

### I installed it, but it does not show up.

Check where you are. Daikenja runs only in Claude Code: the CLI, or the
**Code** tab of the Claude Desktop app. It does not appear in the **Chat** or
**Cowork** tabs, on claude.ai, or in a Desktop **cloud** session, which loads
plugins from your claude.ai account rather than your machine. If you just
installed or updated, restart Claude Code or run `/reload-plugins`.
[Where it runs](install.md#where-it-runs)

### I asked in plain words and nothing happened.

Most Daikenja skills run only when you type them -- `/daikenja:project-catchup`,
not "catch me up". Six skills can also start from plain language, and even
those stop doing so when many plugins are installed on a smaller-context model.
Typing the slash command always works.
[When plain language does not start a skill](install.md#when-plain-language-does-not-start-a-skill)

### Do I have to re-run setup after an update?

Usually not. When a release does need it, the next skill you run prints one
line telling you to run `/daikenja:setup-user`.
[Do I have to re-run setup?](install.md#do-i-have-to-re-run-setup)

### Do I need git, or a repository?

No. The writing and reviewing skills work anywhere. A project's ledger is
happiest in a git repository, where it is versioned beside the code, but a
project with no repository can keep its ledger at any path you choose.
[One project, many places](ledger.md#one-project-many-places)

## Privacy

### Does it ever send or post anything?

No. Every skill hands its result back to you, and you send it yourself. The
one exception is the optional Slack bot, which you run yourself and which
posts only as its own Slack app.
[What it keeps, and where](../../README.md#what-it-keeps-and-where)

### Who can see what I told it about a colleague?

Only you. Persona notes live in `~/.claude/daikenja/personas.md` on your
machine, or in your own Google Drive if you chose that. They are never written
into a ledger or a project.
[Who can see what](your-data.md#who-can-see-what)

### Who can see the ledger?

Everyone who can read the project. It lives in the project, so in a git
repository it is shared with the repository. Write ledger lines for the team.
[Who can see what](your-data.md#who-can-see-what)

## Using it

### My writing style was not applied.

If your `writing-style.md` lives in Google Drive and Daikenja cannot read it,
the skill stops rather than drafting in the default voice. An unreadable file
and an empty one look the same, so it will not guess. Also check the file
actually has content: `learn-voice` writes it from your samples.
[Google Drive, if you want it](your-data.md#google-drive-if-you-want-it)

### It answered about the wrong project.

Run `/daikenja:project-list`. It shows which project your current directory
resolves to and whether each ledger exists. The reading skills also take a
project name, so `/daikenja:project-summary atlas-migration` reads that
project from anywhere.
[Reading it back](ledger.md#reading-it-back)

### How is the ledger different from ADRs or a wiki?

An architecture decision record (ADR) or a wiki page is a full document per
decision. A ledger line is one sentence, written as the decision happens, with
its owner and date, and marked when a later decision replaces it. The two work
together: the ledger can track your ADRs and wiki pages as sources.
[How it compares](why.md#how-it-compares)

### "Persona" means three different things?

Yes, and they are separate:

- **A persona** is your notes on a real person you write to, kept by
  `remember-persona`.
- **Reviewers** are the built-in readers `preflight` checks a draft against --
  the busy reader, the executive and so on.
- **Tensei** is an optional persona for how Claude talks to *you*.

[Writing a reply](writing.md) · [Tensei](tensei.md)
