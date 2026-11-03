# The Slack bot (optional)


[`bot/`](../../bot/) is a small Python service you can run alongside your install
so a thread gets an answer without anyone leaving Slack. Mention it and it
replies in the same thread:

```
@daikenja summary     what this thread is asking, what is open, who it waits on
@daikenja judgement   that thread checked against your project's ledger
```

Either command takes a Slack permalink or a Confluence page link as an
argument and works on that instead, still answering in the thread you asked
from.

**It is a personal instance.** It runs on your machine, reads your ledgers,
and posts as its own Slack app -- never as you, and never with anybody
else's records. By default only you can trigger it.

**The model never holds the Slack token.** The bot runs Claude Code headless
to produce the text, with the credentials stripped out of that process's
environment and its tools limited to reading files; a separate layer that
the model cannot reach does the posting. Thread content is written by other
people, and a model that could both read it and post would be one
instruction away from posting somewhere it should not.

Nothing above happens unless you set it up: installing the plugin downloads
`bot/` and does not run it. [`bot/README.md`](../../bot/README.md) has the Slack
app manifest, the scopes, the config file and the tests.
