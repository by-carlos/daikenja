# Daikenja

**Not an assistant -- a sage you consult. It knows your work, the work around
you, and where to go next.**

Daikenja does not do your work. It reads the conversations, documents, meetings
and code you are buried in, asks what you are actually trying to do, and hands
back something you can act on -- a verdict on a draft, a review of how you
handled a thread, a plain markdown ledger of what a project decided and what is
still open. In a codebase that ledger is the why behind the code, which `git
blame` cannot give you. It never sends, never publishes, and never writes a word
you did not ask for.

The writing and remembering side of a working week.

**Status:** in active development.

## What using it looks like

A colleague drops a long thread on you and wants an answer today.

You paste it into `/daikenja:thread`. It does not write a reply. It tells you
what is actually being asked and by whom, then asks you the few things only you
know -- what you have already promised, what you are not willing to commit to.

You answer, and `/daikenja:compose` drafts the reply: clear and calm, in your
words, with your ask and your stance intact. If the message is one you cannot
afford to get wrong, `/daikenja:preflight` puts the draft in front of readers
who each look for a different failure -- the busy one, the executive, the one
who hunts for risk, the specific colleague you described to it -- then hands
back a revised draft plus the questions only you can answer. Nothing is sent.
You copy it out and send it yourself.

That thread settled two things, so you say so, and `/daikenja:project-log` shows
you the exact lines it wants to add to the project's ledger and waits for your
yes. The ledger is a markdown file that lives in the project, so git versions
it beside the code.

Three weeks later you come back and ask `/daikenja:project-catchup` what you
missed. It tells you what was decided while you were away, what is still open,
and who owes it.

Read, draft, record, come back to it later. That is the whole loop.

## Documentation

- [Install and update](docs/guide/install.md)
- [Writing a reply](docs/guide/writing.md)
- [The project ledger](docs/guide/ledger.md)
- [Reviewing things](docs/guide/reviewing.md)
- [Tensei](docs/guide/tensei.md)
- [Where your data lives](docs/guide/your-data.md)
- [The Slack bot (optional)](docs/guide/slack-bot.md)

## Contributing

Bugs and ideas go to [the issue tracker](https://github.com/by-carlos/daikenja/issues).
A problem with the marketplace listing itself belongs in
[`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins),
which owns the catalog.

[`CONTRIBUTING.md`](CONTRIBUTING.md) has the rest: what an issue needs, the
branch and commit conventions, when a change owes a changelog entry or an
upgrade note, and the conventions that are easiest to trip over. Read it before
opening a pull request.

**Do not report a security problem in a public issue.**
[`SECURITY.md`](SECURITY.md) says how to reach the maintainer privately.

## License

[FSL-1.1-ALv2](LICENSE) -- free for any use except building a competing
commercial product, and each release becomes Apache-2.0 two years after it is
made available. Versions released before this change remain MIT.
