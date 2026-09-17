# bot/

A personal-instance Slack bot for Daikenja. You run your own copy next to
your own install and your own project ledgers, and it answers in the thread
as its own Slack app -- never as you, and never with anyone else's records.

Two commands, both triggered by an @-mention:

| Command | What it posts |
|---|---|
| `@daikenja summary` | The five-line thread summary the [`thread`](../skills/thread/SKILL.md) skill produces at its Step 2: what the thread is, who is asking, what is open, what is waiting on you, and the tone -- plus the `Ledger:` line when the thread matches one of your projects. |
| `@daikenja verdict` | The shareable `message` form of the [`verdict`](../skills/verdict/SKILL.md) skill: what the thread claims or asks, checked against the project's ledger first and general knowledge second, with every statement labelled by where it came from. |

Either command takes a link as its argument and works on that instead of
the thread it was typed in:

```
@daikenja summary https://example.slack.com/archives/C0HARBOR/p1758067200000100
@daikenja verdict https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242/Cutover+plan
```

The answer still lands in the thread the command was typed in, so a verdict
on an external page is visible where somebody asked for it.

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
      - chat:write          # post the answer
      - channels:history    # read a public thread
      - groups:history      # read a private thread, if you use it there
      - channels:read       # name the channel in the summary
      - groups:read         # the same, for private channels
      - users:read          # turn user IDs into names in the transcript
      - reactions:write     # optional: the acknowledging reaction
settings:
  event_subscriptions:
    bot_events:
      - app_mention
  socket_mode_enabled: true
```

**Socket Mode rather than the Events API**, because a personal instance runs
on a laptop or a home server with no public URL and no certificate.
`reactions:write` is the one optional scope: without it the bot still
answers, it just cannot mark the mention as seen. Set `ack_reaction: null`
in the config to skip it deliberately.

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

## What it needs from the plugin

`summary` needs the `thread` skill and `verdict` needs the `verdict` skill,
both from a Daikenja install the headless session can see. The bot checks
this at startup rather than finding out mid-answer:

- With `claude.plugin_dir` set, it reads `skills/` in that tree.
- Otherwise it reads `claude plugin details daikenja`.

A command whose skill is missing is switched off, and asking for it gets one
line in the thread saying which skill is absent and where it looked.
`--check` prints the same thing:

```
  summary:    ready
  verdict:    unavailable
```

**This matters today**: `verdict` shipped after 0.9.1, so an installed
plugin at that version runs `summary` and refuses `verdict` until the next
release. Point `claude.plugin_dir` at a working tree in the meantime.

The check is not a nicety. A session asked for a skill it does not have will
answer anyway, in its own voice, from no source -- and without this the bot
would post that into a public thread as the verdict.

## How the answer is lifted out

The session is asked to mark its deliverable between two sentinel lines, and
usually does. When it does not, the deliverable is found by its own shape:
the `Thread:` / `Asking:` / `Open:` block for `summary`, and the
`AI review summary` header and its bullets for `verdict`. Both shapes are
fixed by the skills, so this is reading a contract rather than guessing.

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
| `slack.ack_reaction` | `eyes` | The emoji added to the mention while the answer is written. `null` turns it off. |
| `claude.command` | `claude` | The Claude Code CLI. A full path works. |
| `claude.model` | unset | Pin the model the headless session uses. |
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

**A mention from anyone not on the allowlist is ignored in silence**, with a
line in the log. A refusal posted back into the thread would turn any
passer-by into a way to fill it.

**`claude.working_dir` defaults to your home directory on purpose.** A bot
has no project of its own. `verdict` resolves a project by a key you named,
then by the working directory, then by the subject's own content -- and
running the session inside one of your registered projects would silently
attach every thread to that project. Home is almost never registered, so
resolution by content does its job.

**Widening `claude.allowed_tools` is the one setting to think twice about.**
Adding `Bash`, `Write` or `WebFetch` hands a capability to a session whose
input is text other people wrote.

### Confluence links

`verdict <confluence link>` needs credentials the Slack app does not have,
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
daikenja_bot/commands.py   parsing `summary` / `verdict` and its argument
daikenja_bot/links.py      Slack permalinks and Confluence URLs
daikenja_bot/slack_io.py   the only file that holds the Slack token
daikenja_bot/transcript.py a fetched thread, rendered for a reader
daikenja_bot/prompts.py    the prompt, and reading the answer back out
daikenja_bot/preflight.py  which skills the headless session will actually find
daikenja_bot/runner.py     the headless session, with the environment scrubbed
daikenja_bot/confluence.py optional page fetching, standard library only
daikenja_bot/mrkdwn.py     markdown to Slack's own dialect
daikenja_bot/config.py     bot.yaml
```

## What it does not do

- It does not write a reply for you. `summary` gathers and `verdict` judges;
  both skills refuse to draft, and this bot does not ask them to.
- It does not write your ledger. Only `/daikenja:project-log` does, on your
  approval, in a session of your own.
- It does not share records between people. Each instance answers from its
  own machine's ledgers. A shared-team bot would need a shared-record design
  -- concurrent writes, access control, whose record is authoritative -- and
  that has not been scoped.
- It does not read a channel it was not invited to, and it does not act on a
  message that is not an @-mention.
