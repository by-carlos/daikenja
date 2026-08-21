# Daikenja

**Not an assistant -- a sage you consult. It knows your work, the work around
you, and where to go next.**

Daikenja does not do your work. It reads the conversations, documents, meetings
and code you are buried in, asks what you are actually trying to do, and hands
back something you can act on -- a verdict on a draft, a review of how you
handled a thread, a plain markdown ledger of what a project decided and what is
still open. In a codebase that ledger is the why behind the code, which `git
blame` cannot give you. It never sends, never publishes, and never writes a word
you have not approved.

The writing and remembering side of a working week.

**Status:** in active development. Fifteen skills ship today.

## Where each half runs

**The `project-*` skills, plus `meeting-review`, are Claude Code only**, and
this is by design rather than a gap waiting to be closed. They read and write a
ledger inside the project you are working in, and a project working tree is not
something a browser session has. Claude Code is where the state lives, and it
stays the source of truth: it accumulates a ledger and a config, claude.ai does
not, so the drift only ever runs one way.

Both setup skills are Claude Code only for the same reason. `setup-user`'s
whole job is creating `~/.claude/daikenja/`, and `setup-project` registers a
directory in it and can seed a ledger inside that directory -- neither a home
directory nor a project working tree exists in a browser session. A plugin
manifest has no field that can restrict which surface loads a plugin, so
`setup-user` checks at runtime and stops with an explanation if the environment
cannot give it a home directory. `setup-project` needs no check of its own: it
stops when there is no `daikenja.yaml`, which is the same fact one step later.

**The writing skills also run on claude.ai.** `compose`, `doc-review`,
`preflight`, `remember-persona`, `self-review` and `thread` need your settings
and something you paste in, never project state. Build the upload zips and add
them there yourself:

```
python scripts/build-claude-ai-skills.py
```

That writes one zip per skill into `dist/claude-ai/`. Upload each at
**Settings > Customize > Skills > Add > Upload a skill**. It needs code
execution enabled, on a Pro, Max, Team or Enterprise plan.

Settings come from the `daikenja` folder in your Google Drive, which
`/daikenja:setup-user` creates when you ask it to -- so the files follow you
without anything to upload or keep in sync. Skills do not sync between
surfaces, so re-upload a zip when a skill changes.

`remember-persona` writes its entry into the Drive file rather than a local
one, and asks for connector approval at each step.

`learn-voice` is not in that set yet. It writes `writing-style.md`, which on
claude.ai exists only as a Drive file, and that path has not been exercised
there -- so it ships to Claude Code alone for now.

What claude.ai cannot do -- no reviewer dispatch for `preflight`, no ledger, no
`setup-user` -- is recorded in [`docs/future-work.md`](docs/future-work.md).

## Install

```bash
claude plugin install by-carlos/daikenja
```

Then run `/daikenja:setup-user` once. It checks the environment and writes your
configuration into `~/.claude/daikenja/`.

After that, run `/daikenja:setup-project` in each project you want Daikenja to
track. It registers the directory, sets that project's own settings, and can
seed its ledger from a decision log, a wiki space or a Slack channel you already
have. `setup-user` is once per person; `setup-project` is once per project.

**A project does not have to be one directory.** A programme spanning three
repositories is registered once and every one of its directories resolves to
it; a body of work with no repository at all is registered with no directory,
reached by name, and keeps its ledger wherever its `ledger:` key points.
`/daikenja:project-list` shows the whole index back to you.

## Skills

Sixteen skills, grouped by what they do.

**Writing a reply**

- `/daikenja:thread` -- reads a Slack or email thread, summarizes what is being
  asked and by whom, then collects context from you before any reply is
  drafted.
- `/daikenja:compose` -- rewrites or drafts a work message (Slack, Teams, email)
  so it stays clear, calm and easy to read, without changing the ask, the
  stance or the confidence level.
- `/daikenja:preflight` -- challenges a draft before it goes out. It runs the
  substance checks, puts the draft in front of reviewers who each read it for
  a different failure mode, fixes the wording problems they raise, and hands
  back a revised draft plus the facts only you can supply. It changes wording
  and never content.
- `/daikenja:remember-persona` -- records what you say about a person you write
  to, so later messages are written for that reader. The only skill that writes
  persona content.

**Writing the ledger**

- `/daikenja:project-log` -- records decisions and open items in a project's
  ledger. The only skill that writes ledger content; every other skill reads it.

**Reading the ledger**

- `/daikenja:project-catchup` -- reports what changed in a project's ledger
  since you last checked, then advances the checkpoint on approval.
- `/daikenja:project-summary` -- gives a full-state overview of a project's
  ledger, written for someone with no prior context.
- `/daikenja:project-decisions` -- looks up what was decided about a specific
  topic, including its supersession history.
- `/daikenja:project-gaps` -- audits a project's ledger for open items with no
  owner or that have sat too long.
- `/daikenja:project-sources` -- reports which of the documents a project is
  tracked from moved since you last read them, by comparing each source's
  stored last-modified value against what its system reports now. The mirror
  image of `project-catchup`: that one reports what Daikenja wrote, this one
  reports what moved outside.
- `/daikenja:project-list` -- lists every project Daikenja knows about, says
  which one you are standing in, and reports whether each ledger actually
  exists. The one to run when a read skill answered about a project you did not
  expect.

All five reading skills take an **optional project name**:
`/daikenja:project-summary atlas-migration` reads that project from anywhere,
without being in its directory.

**Reviewing things**

- `/daikenja:meeting-review` -- turns a meeting transcript into proposed ledger
  entries, then hands them to `/daikenja:project-log` for your approval.
- `/daikenja:doc-review` -- reviews a document against a fixed checklist before
  it is published or shared.
- `/daikenja:self-review` -- reviews how you handled a thread you took part in,
  with private, evidence-backed coaching on your own moves.

**Setup**

- `/daikenja:setup-user` -- one-time, re-runnable personal setup. Checks the
  environment, writes your `daikenja.yaml` and captures your profile. It does
  not register a project.
- `/daikenja:setup-project` -- once per project. Registers the directory you are
  in, offers that project's own settings, and can optionally seed its ledger
  from sources the project already has. Seeding proposes entries and hands them
  to `/daikenja:project-log` for your approval; it never writes the ledger
  itself.
- `/daikenja:learn-voice` (**beta**) -- works out how you write from writing
  samples you supply, and proposes the whole of your `writing-style.md`. Beta
  because it has been walked by hand against a fixture but not yet used on a
  real corpus, so read the proposal before you approve it. It reads only
  samples you say you wrote yourself, records style and never facts about
  people or projects, shows the complete file -- as a diff if you already have
  one -- and writes nothing until you approve it. Run it whenever you have more
  samples, not only at setup.

## Where your data lives

Nothing personal is stored in this repository, and nothing personal should ever
be written into the installed plugin directory -- plugin directories are managed
and get overwritten on update.

| What | Where | Written by |
|---|---|---|
| Profile, per-project settings, checkpoints | `~/.claude/daikenja/daikenja.yaml` | `setup-user` for your profile, `setup-project` for a project's entry, and `project-catchup` for the `last_checkpoint` key only |
| Your notes on the people you work with | `~/.claude/daikenja/personas.md`, or `daikenja/personas.md` in your Google Drive | you, plus `remember-persona` for people you describe to it |
| How you write | `~/.claude/daikenja/writing-style.md`, or `daikenja/writing-style.md` in your Google Drive | you, plus `learn-voice` for a proposal you approve |
| A project's decision ledger | `<project root>/.daikenja/ledger.md`, or wherever that project's `ledger:` key points -- including outside the project. For a project spanning several directories the root is the first one registered | `project-log` only |

The plugin ships blank starting points in `templates/`. Those get copied out to
your directories; the copies are the live files.

**Local files are the default, and Google Drive is opt-in.** If you want your
persona notes or your writing style reachable from another machine, either one
can live in Google Drive instead -- `setup-user` offers this once, works fine
without it, and never asks you to sign up for anything. Drive is reached through
Google's own connector, under your own account, so nothing goes through the
plugin author. The two settings are independent: keeping personal notes on
colleagues local while sharing a writing style is a normal setup. The ledger
does not move -- it stays in the project, where git already versions it.

Everything Daikenja puts in Drive goes in **one `daikenja` folder** it creates
for you, mirroring `~/.claude/daikenja/` on your machine. Nothing is left loose
at the top level of your Drive.

Two things are worth knowing before you choose Drive. **`setup-user` has to
create the file**: the connector only shows Claude the files it created itself,
so a document already in your Drive cannot be pointed at, however you share it.
And **a Drive file that Daikenja cannot read stops the skill** rather than
quietly carrying on, because an unreadable file and an empty one look identical
from here -- the alternative is drafting in the default voice while you think
your own style was applied.

Two rules the skills follow:

- **One writer for the ledger.** Only the `project-log` skill writes ledger
  content. `project-catchup` writes one config key, `last_checkpoint`, because
  reporting a delta and moving the checkpoint is its job -- it never touches
  the ledger itself. `setup-project` can propose a whole ledger's worth of
  entries when it seeds one, and every last line still goes through
  `project-log` for your approval. Every other skill only reads.
- **You approve first.** A skill proposes a ledger entry, you confirm, then it
  writes.

## Development

Load the working tree straight into a session, from the repo root:

```bash
claude --plugin-dir .
```

Run `/reload-plugins` after editing a skill to pick up the change without
restarting. Validate the manifest with:

```bash
claude plugin validate .
```

Installing this repo as a **local marketplace** is not a substitute for the
above: it copies the tree into the plugin cache at install time rather than
referencing it live, so edits go stale until you reinstall. Use
`--plugin-dir .` for development.

Layout:

```
.claude-plugin/plugin.json   the manifest
skills/                      one directory per skill, each with a SKILL.md
templates/                   blank files copied out to the user
docs/                        the ledger and config specifications
```

`docs/` holds the contracts. A skill implements a contract and never redefines
one, so a format change happens in `docs/` first.

## License

[FSL-1.1-ALv2](LICENSE) -- free for any use except building a competing
commercial product, and each release becomes Apache-2.0 two years after it is
made available. Versions released before this change remain MIT.
