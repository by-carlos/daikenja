# bot/

A personal-instance Slack bot for Daikenja. You run your own copy next to
your own install and your own project ledgers, and it answers in the thread
as its own Slack app -- never as you, and never with anyone else's records.

Three commands, all triggered by an @-mention:

| Command | What it posts |
|---|---|
| `@daikenja summary` | The `message` form of the [`thread`](../skills/thread/SKILL.md) skill's Step 2 summary: what the thread is, who is asking, what is open and who it is waiting on -- named, never "you", since every reader of a channel is a "you" -- plus the `Ledger` line when the thread matches one of your projects. |
| `@daikenja judgement` | The shareable `message` form of the [`judgement`](../skills/judgement/SKILL.md) skill: what the thread claims or asks, checked against the project's ledger first and general knowledge second, with every statement labelled by where it came from. |
| `@daikenja delete` | Nothing. It takes down the bot's own most recent post in that thread, and confirms to the person who asked in a message only they can see. |

`judgement` can also be written as :point_up_2: -- `@daikenja :point_up_2:`,
either as the shortcode or as the character your keyboard produces, with or
without a skin tone. It is the same command and takes the same argument.

`summary` and `judgement` each take a link as their argument and work on
that instead of the thread they were typed in:

```
@daikenja summary https://example.slack.com/archives/C0HARBOR/p1758067200000100
@daikenja judgement https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242/Cutover+plan
```

The answer still lands in the thread the command was typed in, so a verdict
on an external page is visible where somebody asked for it.

**A third way in: react instead of typing.** Set `slack.reaction_trigger` to a
custom emoji's name and adding that reaction to any message runs `summary`
and `judgement` together and posts one combined reply in that message's
thread -- no @-mention, no command word. A reaction on a thread reply is
resolved to the thread's parent, the same as a reply someone typed a command
into. The existing allowlist still decides who may trigger it, and a
reaction from anybody else does nothing at all -- there is no ephemeral
reply on this path, because nobody addressed the bot. The bot's own
`ack_reaction` doubles as the record that a message has already been
answered: removing and re-adding the trigger, or a second person adding it,
does nothing once that reaction is there. This is off by default; the emoji
it reacts to has to be created in your workspace first (see below).

**And one way out that nobody triggers**: `--digest` takes a list of messages
something else collected and posts one project-grouped summary of them to
your own DM, with each project's open ledger items beside its group. It is a
separate run on a schedule, not a fourth command -- see
[The digest](#the-digest).

## Naming a project

`summary` and `judgement` both take `project <key>` ahead of any link, to say
which project's ledger to check:

```
@daikenja judgement project harbor
@daikenja summary project harbor https://example.slack.com/archives/C0HARBOR/p1758067200000100
```

A key named this way is decisive: the session reads that project's ledger and
falls back to nothing else. The bot does not check the key -- it has never
read your `daikenja.yaml` -- so an unknown one comes back as an answer naming
the keys that are registered, not as a parse error.

**Without it, a project is resolved from the thread itself**, per
[`project-card.md`](../docs/project-card.md) § Resolving a project by content:
a channel, a tracker key or a repository that exactly one card owns decides
it outright. A match on a card's *Scope* paragraph alone is weaker, and in a
conversation the skill would stop and ask you to confirm it. **Here it never
asks.** Nobody in a thread can answer, so the candidate is treated as no
match: the answer comes back on general knowledge and states which project it
assumed, in one of two fixed sentences --

```
No ledger read. This looks like Harbor rollout -- say `@daikenja judgement project harbor` to check it.
No project context. Add `@daikenja judgement project <key>` if you want a ledger checked.
```

-- so the answer always lands, and naming the project is a rephrase rather
than a conversation. Run the command if it was the right project; ignore the
line if it was not.

Two things happen on its own to the thread a command with no argument reads.
**A forwarded message is followed to its original.** Sharing a message into
another channel leaves its text in an attachment rather than in the message,
so the thread under one is a wrapper with an empty parent; the permalink in
that attachment is followed once, and named above the answer. **The bot's own
earlier answers are dropped.** Otherwise a second command in a thread it has
already answered summarises its own summary. Another app's messages stay --
those are somebody's actual content.

**`delete` can only ever remove the bot's own messages.** A bot token deletes
what that same token posted and nothing else, so the command cannot take
anybody else's message down however it is phrased -- including the `@daikenja
delete` mention itself, which stays where you typed it. It removes one
message per invocation, the most recent, and says how many of its own posts
are still in the thread; run it again for the next one. Who may run it is the
same allowlist as the other two commands.

## The split that matters

**The model produces text. A separate layer posts it.** The model never
holds a Slack token and has no way to send anything:

- `runner.py` starts `claude -p` as a subprocess, pipes the thread in on
  standard input, and reads text back. It is handed no Slack client.
- `scrubbed_env()` strips every credential from the environment that
  subprocess inherits -- the two tokens the config names, and anything else
  beginning `SLACK`. Without this, "the model cannot post" would hold only
  until it read `os.environ` and called the Web API itself.
- The headless session runs with `--allowedTools Read,Glob,Grep` and
  `--permission-prompts none`, so it can find a ledger and read nothing
  else. No shell, no writes, no network fetches.
- `slack_io.py` is the only file that holds the token, and the only one
  that calls the Slack API.

This is a requirement, not a preference. The thread being summarised is
untrusted input written by other people, and a model that can both read it
and post is one instruction away from posting somewhere it should not. The
same reasoning is why this bot does not post through a hosted Slack MCP
connector: that would post as *you* rather than as an app, would not
notify, and would hand the model exactly the send capability this design
removes.

## Set up the Slack app

1. Create an app at [api.slack.com/apps](https://api.slack.com/apps) --
   **From an app manifest** is quickest. The manifest below asks for
   everything this bot uses.
2. Under **Socket Mode**, turn it on and generate an **app-level token**
   with the `connections:write` scope. That is the `xapp-` token.
3. Under **Install App**, install it to your workspace and copy the **Bot
   User OAuth Token**. That is the `xoxb-` token.
4. Invite the bot to each channel you want it to work in: `/invite @daikenja`.
   In a group DM there is no `/invite` -- mention it and Slack offers to add
   it to the conversation.

```yaml
display_information:
  name: daikenja
  description: Thread summaries and ledger-checked verdicts, in the thread.
features:
  bot_user:
    display_name: daikenja
    always_online: false
oauth_config:
  scopes:
    bot:
      - app_mentions:read   # receive the @-mention that triggers it
      - chat:write          # post the answer, and delete it again
      - channels:history    # read a public thread
      - groups:history      # read a private thread, if you use it there
      - mpim:history        # read a thread in a group DM
      - im:history          # read a thread in a one-to-one DM
      - channels:read       # name the channel in the summary
      - groups:read         # the same, for private channels
      - mpim:read           # the same, for group DMs
      - im:read             # the same, for one-to-one DMs
      - users:read          # turn user IDs into names in the transcript
      - reactions:write     # optional: the acknowledging reaction
      - reactions:read      # optional: trigger by reacting, see below
settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - reaction_added
  socket_mode_enabled: true
```

**Socket Mode rather than the Events API**, because a personal instance runs
on a laptop or a home server with no public URL and no certificate.
`reactions:write` is optional: without it the bot still answers, it just
cannot mark the mention as seen. Set `ack_reaction: null` in the config to
skip it deliberately. `reactions:read` and the `reaction_added` subscription
are needed only for `slack.reaction_trigger`; leave both out if you never set
it. Adding a scope or an event subscription to an installed app takes effect
only after you reinstall it under **Install App**.

Reacting with a custom emoji needs the emoji itself to exist first: an
**Emoji** admin under your workspace's settings, uploaded once by a workspace
admin -- this bot cannot create it.

**A DM is its own scope.** `channels:history` and `groups:history` cover
public and private channels only. Without `mpim:history` and `im:history`
the bot receives the mention in a DM and then answers `conversations_replies
failed: missing_scope`, because it can see the mention but not the thread
around it. Adding a scope to an installed app only takes effect after you
reinstall it under **Install App**.

## Install and run

Python 3.10 or newer.

```bash
pip install -r bot/requirements.txt
cp bot/bot.yaml.example ~/.claude/daikenja/bot.yaml   # then edit it
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
cd bot && python -m daikenja_bot --check              # validate, then:
cd bot && python -m daikenja_bot
```

`--check` reads the config and the credentials, works out which commands can
run, and prints what it found without connecting to Slack or spending a
token. Run it after every edit to `bot.yaml`.

The bot answers one command at a time. A headless session takes tens of
seconds, so the reaction goes on immediately and the answer arrives when it
is written.

## Run it without a window

Started by hand, it holds a console for as long as it runs. Two things have
to change before it can run unattended, and both are easy to miss:

- **`--log-file`.** A windowless process has nowhere to write, so without it
  a bot that fails to start leaves no evidence at all. It rotates at 1 MB and
  keeps three files.
- **The tokens.** A service or a scheduled task does not inherit the
  environment of the shell you exported them in. Either set them as
  *persistent* user environment variables, or point `bot_token_file` and
  `app_token_file` at files -- the file route is the better one here, because
  a file can be locked down and read only at startup.

### Windows: a scheduled task at logon

Use `pythonw.exe` rather than `python.exe`: same interpreter, no console
window. `-WorkingDirectory` is what puts `daikenja_bot` on the import path,
so no `PYTHONPATH` is needed.

```powershell
Register-ScheduledTask -TaskName "Daikenja bot" -Description "Daikenja's personal Slack bot" -Action (New-ScheduledTaskAction -Execute "C:/Python313/pythonw.exe" -Argument "-m daikenja_bot --log-file C:/Users/you/.claude/daikenja/bot.log" -WorkingDirectory "C:/GitHub/daikenja/bot") -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1))
```

`-ExecutionTimeLimit ([TimeSpan]::Zero)` matters: the default stops the task
after three days. Afterwards, `Start-ScheduledTask -TaskName "Daikenja bot"`,
`Stop-ScheduledTask` and `Unregister-ScheduledTask` are the controls, and
`Get-ScheduledTaskInfo -TaskName "Daikenja bot"` says whether it is running.

### Linux or macOS: a systemd user unit

```ini
# ~/.config/systemd/user/daikenja-bot.service
[Service]
WorkingDirectory=%h/daikenja/bot
ExecStart=/usr/bin/python3 -m daikenja_bot
Restart=on-failure

[Install]
WantedBy=default.target
```

`systemctl --user enable --now daikenja-bot`, and `journalctl --user -u
daikenja-bot -f` for the log -- no `--log-file` needed, since journald
captures the console. `loginctl enable-linger $USER` keeps it running when
you are not logged in.

**The config is read once, at startup.** Editing `bot.yaml` changes nothing
until the process is restarted.

## The digest

Everything above is reactive: somebody mentions the bot, it answers in the
thread. `--digest` is the other direction. Hand it a list of messages
something else collected, and it posts one grouped message to your own DM:

```bash
cd bot && python -m daikenja_bot --digest items.json
cd bot && python -m daikenja_bot --digest - < items.json   # or on stdin
cd bot && python -m daikenja_bot --digest items.json --dry-run
```

It groups the items by project, adds each project's open ledger items beside
its group, posts, and exits. `--dry-run` prints the digest instead of posting
it, which is how to see what it will say before putting it on a schedule.

**The items are JSON**, an array of objects (or an object with an `items`
array). Only `summary` is required:

```json
[
  {
    "ts": "2026-09-18T08:14:00Z",
    "channel": "#harbor-rollout",
    "sender": "@souei",
    "bucket": "to:me",
    "topic": "harbor",
    "permalink": "https://example.com/slack/harbor-rollout/p11",
    "summary": "Asked whether the ramp pauses at 25% if p99 doubles."
  }
]
```

`topic` is a registered project key and is decisive when it is one -- the
feeder usually knows. Without it the item is placed by what it names: the
channel, a repository, a tracker key that exactly one project card owns. A
card that only *nearly* fits decides nothing, because nobody is reading a
digest live to confirm it, so that item comes back under **Unmatched** with
the command that would settle it. `bucket` is whatever your feeder calls its
own categories; it is shown and never interpreted, so nothing here decides
what is urgent. Any other field your feeder already carries -- a score, a
message id -- is dropped rather than refused.

**Nothing collects the items.** That is the feeder's job, and deliberately
not this bot's: how a list is gathered, filtered and ranked is specific to
one person's setup, and the half worth sharing is the grouping. A cron entry,
a scheduled task, or a script that writes `items.json` and then runs the two
lines above is the whole integration.

**It needs only the bot token.** `SLACK_APP_TOKEN` is for Socket Mode, which
is how events are *received* -- a digest only sends. So a digest runs on a
schedule beside the listener, or on a machine that never runs the listener at
all, and it opens no socket either way. It posts to the DM using the same
`chat:write` scope as everything else: no extra scope, and nothing to
reinstall.

## What it needs from the plugin

`summary` needs the `thread` skill and `judgement` needs the `judgement` skill,
both from a Daikenja install the headless session can see. The bot checks
this at startup rather than finding out mid-answer:

- With `claude.plugin_dir` set, it reads `skills/` in that tree.
- Otherwise it reads `claude plugin details daikenja`.

A command whose skill is missing is switched off, and asking for it gets one
line in the thread saying which skill is absent and where it looked.
`--check` prints the same thing:

```
  summary:    ready
  judgement:  unavailable
```

**This matters today**: `judgement` shipped after 0.9.1, so an installed
plugin at that version runs `summary` and refuses `judgement` until the next
release. Point `claude.plugin_dir` at a working tree in the meantime.

The check is not a nicety. A session asked for a skill it does not have will
answer anyway, in its own voice, from no source -- and without this the bot
would post that into a public thread as the verdict.

`--digest` needs the `digest` skill the same way, but is not part of the
startup check: nothing is running yet when it is invoked. It fails at the
point of use instead -- one line naming the skill, and nothing posted --
which is the same protection arriving a few seconds later.

## How the answer is lifted out

The session is asked to mark its deliverable between two sentinel lines, and
usually does. When it does not, the deliverable is found by its own shape:
the `Thread` / `Asking` / `Open` block for `summary`, and the `Verdict`
header and the sections that follow it for `judgement`. Both shapes are
fixed by the skills, so this is reading a contract rather than guessing.

**A question is never posted.** If no block is recognised *and* the output
asks something, a fixed line goes out instead -- *"I could not produce an
answer for that. Ask me again, or name the project with `project <key>`."* --
and the raw output goes to the log. The rules above tell the session not to
ask, and a real run asked anyway; nobody in a thread can answer a question
the bot is not waiting on, so the thread would simply stop there. Anything
else unrecognised is still posted as it came.

Whatever comes out is then cleaned: stray code fences are dropped, and every
absolute path is replaced with `a local path`. Both skills already say a
`Ledger` line names the project and never the path -- a path carries the
machine's own username and nobody in a channel can open it -- but that held
only while the model complied, and once it did not, one went into a public
thread. Links are left alone.

That matters because the headless session is not a private one. It reads the
user's own `CLAUDE.md` like any other session, so a personal conversational
register -- labelled response parts, emoji markers, an announcement of which
skill is running -- applies, and `thread` ends by asking the reader
questions. None of that belongs in a public thread, and none of it is inside
the block.

## Configuration

[`bot.yaml.example`](bot.yaml.example) is the annotated copy. It goes to
`~/.claude/daikenja/bot.yaml` -- the same directory as the rest of your
Daikenja settings -- and **never into this repository**. The only required
key is `slack.owner_user_id`.

| Key | Default | What it does |
|---|---|---|
| `slack.owner_user_id` | required | Your Slack user ID. The only person who can trigger the bot unless the next key widens it, and always allowed. |
| `slack.allowed_users` | `[]` | Other people who may trigger it. |
| `slack.allowed_channels` | `[]` | Restrict it to named channels. Empty means every channel it was invited to. |
| `slack.bot_token_env` / `slack.app_token_env` | `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` | Where the tokens are read from. |
| `slack.bot_token_file` / `slack.app_token_file` | unset | A file holding the token instead, for people who would rather not export one. |
| `slack.bot_token` / `slack.app_token` | unset | The token written into the config file itself. Accepted, and the last choice -- see below. |
| `slack.ack_reaction` | `eyes` | The emoji added to the mention while the answer is written. Also doubles as the re-fire guard on the reaction-trigger path. `null` turns it off. |
| `slack.reaction_trigger` | unset | An emoji name (no colons) that runs `summary` + `judgement` on the reacted message's thread when added by an allowed person. Unset means the reaction path is off. |
| `slack.unauthorized_message` | a line saying it is a personal instance | What someone not on the allowlist is told, privately. `{owner}` becomes a mention of `owner_user_id`. `null` says nothing at all. |
| `claude.command` | `claude` | The Claude Code CLI. A full path works. |
| `claude.model` | `claude-sonnet-5` | The model the headless session runs on. An empty value follows your account's default. |
| `claude.effort` | `medium` | The reasoning effort: `low`, `medium`, `high`, `xhigh`, `max`. An empty value follows your account's default. This is separate from the model -- `claude-sonnet-5-medium` is not a model name and is refused at startup. |
| `claude.plugin_dir` | unset | Only for running against a working tree of this repository. An installed plugin needs nothing here. |
| `claude.working_dir` | your home directory | Where the headless session runs. |
| `claude.allowed_tools` | `Read, Glob, Grep` | The tools the session may use. |
| `claude.extra_args` | `[]` | Extra arguments for `claude`. |
| `claude.timeout_seconds` | `300` | How long one answer may take. |
| `confluence.*` | unset | Optional. Turns on Confluence links. |

**Where a token lives: environment, then a file, then the config.** Each
credential is looked for in that order, and the first one found wins. The
environment is the recommendation, because a long-lived process needs the
value in memory and not in a file anybody can read. A `*_token_file` is the
alternative for a file you have chmodded yourself. Writing the token
straight into `bot.yaml` as `slack.bot_token`, `slack.app_token` or
`confluence.token` works and is the last choice: `bot.yaml` is
`.gitignore`d here, but it is still a plaintext secret in a config
directory, and every backup of that directory now carries it.

**A mention from anyone not on the allowlist gets an ephemeral reply**, and a
line in the log. Only the person who mentioned the bot sees it: nobody is
notified, and nothing is left behind in the channel. That is the whole reason
it can answer at all -- a refusal posted into the thread as a normal message
would turn any passer-by into a way to fill it, which is why
`unauthorized_message: null` is there for anyone who would rather the bot
stayed completely silent.

Set it to whatever fits. `{owner}` is replaced with a mention of
`owner_user_id`, which renders as a name and notifies nobody, because an
ephemeral message never does:

```yaml
unauthorized_message: >-
  Sorry, this bot is in beta and runs on {owner}'s own account.
```

Someone who *is* allowed but is in a channel `allowed_channels` excludes gets
a different line saying so, since telling them they are not on the allowlist
would not be true.

**`claude.working_dir` defaults to your home directory on purpose.** A bot
has no project of its own. `judgement` resolves a project by a key you named,
then by the working directory, then by the subject's own content -- and
running the session inside one of your registered projects would silently
attach every thread to that project. Home is almost never registered, so
resolution by content does its job.

**Widening `claude.allowed_tools` is the one setting to think twice about.**
Adding `Bash`, `Write` or `WebFetch` hands a capability to a session whose
input is text other people wrote.

### Confluence links

`judgement <confluence link>` needs credentials the Slack app does not have,
so it is off until you add a `confluence` block. Without one, the bot
replies in the thread that Confluence links are not configured and stops.

```yaml
confluence:
  base_url: https://example.atlassian.net
  email: you@example.com
  token_env: CONFLUENCE_API_TOKEN
```

The token is an [Atlassian API
token](https://id.atlassian.com/manage-profile/security/api-tokens). Only
the full page URL works -- a short `/wiki/x/...` link carries no page id,
and the bot says so rather than guessing.

## Tests

```bash
cd bot && python -m unittest discover -s tests -t .
```

No Slack workspace, no network, and no Claude Code CLI: the Slack client and
the headless session are both injected, so every branch runs against a
stand-in. CI runs the same command in the `bot` job of
[`ci.yml`](../.github/workflows/ci.yml).

Fixtures follow this repository's rule -- invented projects, invented
people, `example.com` links, and never real work content.

## Why `slack-bolt` and not `slack-sdk`

Socket Mode needs a WebSocket client, envelope acknowledgement, and
reconnection handling. `slack-sdk` has the pieces; `slack-bolt` is the
supported assembly of them, and it is a thinner thing to depend on than a
hand-rolled socket loop that has to get reconnection right. Bolt depends on
`slack-sdk`, so the Web API client in `slack_io.py` comes with it and there
is no second dependency.

Bolt's listener decorators are used for routing and nothing else. The
listener hands the event to a worker and returns immediately, because Slack
expects an acknowledgement within three seconds and a headless session takes
far longer than that. Bolt's `say` helper is deliberately unused: every post
goes through `slack_io.py`, which is the layer that is allowed to.

## Layout

```
daikenja_bot/__main__.py   the entry point and --check
daikenja_bot/app.py        Socket Mode transport; the only slack_bolt import
daikenja_bot/handler.py    what happens on a mention, start to finish
daikenja_bot/commands.py   parsing `summary` / `judgement` / `delete`, `project <key>` and the argument
daikenja_bot/links.py      Slack permalinks and Confluence URLs
daikenja_bot/slack_io.py   the only file that holds the Slack token
daikenja_bot/transcript.py a fetched thread, rendered for a reader
daikenja_bot/prompts.py    the prompt, and reading the answer back out
daikenja_bot/preflight.py  which skills the headless session will actually find
daikenja_bot/runner.py     the headless session, with the environment scrubbed
daikenja_bot/confluence.py optional page fetching, standard library only
daikenja_bot/mrkdwn.py     markdown to Slack's own dialect
daikenja_bot/digest.py     the scheduled digest: a feeder's item list in, one DM out
daikenja_bot/config.py     bot.yaml
```

## What it does not do

- It does not write a reply for you. `summary` gathers and `judgement` judges;
  both skills refuse to draft, and this bot does not ask them to.
- It does not write your ledger. Only `/daikenja:project-log` does, on your
  approval, in a session of your own.
- It does not share records between people. Each instance answers from its
  own machine's ledgers. A shared-team bot would need a shared-record design
  -- concurrent writes, access control, whose record is authoritative -- and
  that has not been scoped.
- It does not read a channel it was not invited to, and it does not act on a
  message that is not an @-mention.
- It does not decide what is worth digesting, and it does not page anyone.
  `--digest` groups a list something else collected; what goes on that list,
  and whether anything on it is urgent, was settled before this bot saw it.
