# Install and update

## Install

Daikenja is listed on the shared
[`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins)
marketplace, and this repo is also a marketplace in its own right -- so you can
install it on its own, without adding anything else first. Pick whichever of
these matches how you use Claude Code.

### Claude Desktop app

No terminal needed. Open the **Plugins** pane (the **+** button next to the
prompt box, then **Plugins**) and click **Add**. Put `by-carlos/daikenja` in the
**URL** box -- it takes a GitHub `owner/repo` directly, so there is nothing else
to paste -- then click **Sync**.

![The Add marketplace dialog in the Claude Desktop app, with by-carlos/daikenja entered in the URL field](../images/claude_desktop_marketplace.png)

The plugin directory opens on its own once the sync finishes. Daikenja is under
the **Code** tab, with a **+** beside it -- click that, and it is installed.

![The plugin directory in the Claude Desktop app, showing the Daikenja card with a + button to install it](../images/claude_desktop_plugin.png)

The same **Plugins** pane is where you later enable, disable or remove it.

### Claude Code CLI

From inside a session:

```
/plugin marketplace add by-carlos/daikenja
/plugin install daikenja@daikenja
```

Or from your shell, without starting a session first:

```bash
claude plugin marketplace add by-carlos/daikenja
claude plugin install daikenja@daikenja
```

### After installing

However you installed it, run `/daikenja:setup-user` once. It checks the
environment and writes your configuration into `~/.claude/daikenja/`.

Then run `/daikenja:setup-project` in each project you want Daikenja to track.
It registers the directory, sets that project's own settings, and can seed its
ledger from a decision log, a wiki space or a Slack channel you already have.
`setup-user` is once per person; `setup-project` is once per project.

**A project does not have to be one directory.** A programme spanning three
repositories is registered once and every one of its directories resolves to
it; a body of work with no repository at all is registered with no directory,
reached by name, and keeps its ledger wherever its `ledger:` key points.
`/daikenja:project-list` shows the whole index back to you.

## Where it runs

**Daikenja is a Claude Code plugin.** It runs everywhere Claude Code does: the
**Claude Code CLI**, and the **Code** tab of the **Claude Desktop app**. You can
install it from either one -- the Desktop app has its own plugin menu, so you
never have to open a terminal. Local and SSH sessions both work.

It is not a claude.ai skill. The Claude Desktop app has three tabs, and only
**Code** runs Claude Code plugins -- **Chat** and **Cowork** (for Dispatch and
longer agentic work) do not, and neither does claude.ai itself, so Daikenja will
not show up in any of them. One more case worth knowing: a desktop **cloud**
session loads plugins from your claude.ai account rather than from your own
machine, so a Daikenja you installed locally will not be there either.

Settings come from `~/.claude/daikenja/`, or the `daikenja` folder in your
Google Drive if you opt into that -- see below.

**Typing `/daikenja:<skill>` always works, on every model.** Claude Code can
also start a skill just from plain language ("help me answer this thread"
triggering `/daikenja:thread`), but only if it has room to read that skill's
description -- and on a smaller-context model, a full Daikenja install plus a
couple of other plugins can be more than Claude Code has room for, so it falls
back to skill *names* only and plain-language triggering stops working for
Daikenja's skills. If that happens to you, use the slash form, or raise
`skillListingBudgetFraction` in your Claude Code settings to give skill
descriptions more room. Since the ledger, setup, drafting and self-review
skills moved to slash-only, Daikenja's five auto-invocable descriptions run
about 3,600 characters, under Claude Code's 8,000-character default budget, so
the setting is only needed when other plugins fill the rest. (Measured 24 Aug 2026
on Claude Code 2.1.240,
[by-carlos/daikenja#199](https://github.com/by-carlos/daikenja/issues/199), on
a 200K-context model: the thirteen auto-invocable descriptions of that time
ran about 8,600 characters, and `skillListingBudgetFraction: 0.03` covered it.
On a 1M-context model nothing is cut.)

## Setup skills

- `/daikenja:setup-user` -- one-time, re-runnable personal setup. Checks the
  environment, writes your `daikenja.yaml` and captures your profile. It does
  not register a project.
- `/daikenja:setup-project` -- once per project. Registers the directory you are
  in, offers that project's own settings, and can optionally seed its ledger
  from sources the project already has. Seeding proposes entries and hands them
  to `/daikenja:project-log` for your approval; it never writes the ledger
  itself.

## Updating

New versions ship on the `release` branch.

### Claude Desktop app

Open the **Plugins** pane and select Daikenja. Its page shows the version you
have, how many skills it ships, and an **Update** button.

**Do not count on the desktop app noticing a new release.** Its updating has
been inconsistent in testing: a plugin sat on an old version across a release,
with the **Update** button inactive and **Check for updates** reporting nothing
available, days after the new version was out.

So if that page shows a version behind the one you expect, do not wait for it.
Remove Daikenja and install it again -- a reinstall always lands on the current
version. If you have a terminal, the CLI commands below are the dependable
route.

### Claude Code CLI

Run `/plugin` and open the **Marketplaces** tab. Selecting the Daikenja
marketplace gives you **Update marketplace** for a one-off, and **Enable
auto-update**, which has Claude Code refresh the marketplace and its installed
plugins in the background shortly after each session starts. That tab also tells
you which state you are currently in.

Auto-update is worth turning on, and worth checking rather than assuming:
Claude Code enables it by default for Anthropic's own marketplaces, not
necessarily for others. The toggle lives here in the CLI, and the desktop app
has no equivalent -- which, with the caveat above, makes the CLI the reliable
way to keep Daikenja current.

The same two actions from your shell:

```bash
claude plugin marketplace update
claude plugin update daikenja
```

However you update, a new version does not load into a session that is already
running: restart Claude Code, or run `/reload-plugins`.

### Do I have to re-run setup?

Usually not. Most releases change nothing that is already on your disk, and
Daikenja tells you when one does -- every skill that reads your configuration
compares the version that wrote it against the version installed, and prints a
single line when there is something to do:

```
daikenja.yaml was written by Daikenja 0.6.0; 0.7.0 is installed -- run /daikenja:setup-user.
```

That line is the signal. Run `/daikenja:setup-user` when you see it and it
proposes the exact edits and waits for your approval; ignore updating otherwise.
The notice deliberately stays quiet for releases that need nothing, so it does
not become something you learn to skip.

[`docs/upgrading.md`](../upgrading.md) is the same information written out to
apply by hand, newest version first.
