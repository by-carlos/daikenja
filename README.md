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

**Status:** in active development. Thirteen skills ship today.

## Claude Code only

Daikenja does not work on claude.ai or in Cowork, and this is not a temporary
gap.

Two things make it Claude Code specific:

- It reads your configuration from `~/.claude/daikenja/` on your own machine.
- It writes a ledger into the project you are working in.

Neither a home directory nor a project working tree exists in a browser session.
A plugin manifest has no field that can restrict which surface loads a plugin,
so the `setup-user` skill checks at runtime and stops with an explanation if the
environment is wrong.

## Install

```bash
claude plugin install by-carlos/daikenja
```

Then run `/daikenja:setup-user` once. It checks the environment and writes your
configuration into `~/.claude/daikenja/`.

## Skills

Thirteen skills, grouped by what they do.

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

- `/daikenja:log` -- records decisions and open items in a project's ledger.
  The only skill that writes ledger content; every other skill reads it.

**Reading the ledger**

- `/daikenja:catchup` -- reports what changed in a project's ledger since you
  last checked, then advances the checkpoint on approval.
- `/daikenja:summary` -- gives a full-state overview of a project's ledger,
  written for someone with no prior context.
- `/daikenja:decisions` -- looks up what was decided about a specific topic,
  including its supersession history.
- `/daikenja:gaps` -- audits a project's ledger for open items with no owner or
  that have sat too long.

**Reviewing things**

- `/daikenja:meeting-review` -- turns a meeting transcript into proposed ledger
  entries, then hands them to `/daikenja:log` for your approval.
- `/daikenja:doc-review` -- reviews a document against a fixed checklist before
  it is published or shared.
- `/daikenja:self-review` -- reviews how you handled a thread you took part in,
  with private, evidence-backed coaching on your own moves.

**Setup**

- `/daikenja:setup-user` -- one-time, re-runnable setup. Checks the
  environment, writes your `daikenja.yaml`, captures your profile, and
  registers the current project.

## Where your data lives

Nothing personal is stored in this repository, and nothing personal should ever
be written into the installed plugin directory -- plugin directories are managed
and get overwritten on update.

| What | Where | Written by |
|---|---|---|
| Profile, per-project settings, checkpoints | `~/.claude/daikenja/daikenja.yaml` | `setup-user`, plus `catchup` for the `last_checkpoint` key only |
| Your notes on the people you work with | `~/.claude/daikenja/personas.md` | you, plus `remember-persona` for people you describe to it |
| How you write | `~/.claude/daikenja/writing-style.md` | you |
| A project's decision ledger | `<project>/.daikenja/ledger.md` | `log` only |

The plugin ships blank starting points in `templates/`. Those get copied out to
your directories; the copies are the live files.

Two rules the skills follow:

- **One writer for the ledger.** Only the `log` skill writes ledger content.
  `catchup` writes one config key, `last_checkpoint`, because reporting a delta
  and moving the checkpoint is its job -- it never touches the ledger itself.
  Every other skill only reads.
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

MIT -- see [LICENSE](LICENSE).
