"""Read what was asked for out of the text of an @-mention.

Two commands, `summary` and `verdict`. Either may carry one link as its
argument; with no argument, the subject is the thread the mention was typed
in. Anything else comes back as `help`, which the transport answers with one
line of usage rather than guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .links import unwrap_link

MENTION_RE = re.compile(r"<@[UWB][A-Z0-9]+(?:\|[^>]*)?>")

SUMMARY = "summary"
VERDICT = "verdict"
HELP = "help"

KNOWN_COMMANDS = (SUMMARY, VERDICT)

USAGE = (
    "I take two commands. `@daikenja summary` for what this thread is asking "
    "and what is still open, and `@daikenja verdict` for a check of the "
    "thread against the project's ledger. Either one takes a link -- a Slack "
    "thread or a Confluence page -- to work on that instead of this thread."
)


@dataclass(frozen=True)
class Command:
    """One parsed invocation."""

    name: str
    argument: str | None = None
    unknown_word: str | None = None

    @property
    def is_known(self) -> bool:
        return self.name in KNOWN_COMMANDS


def strip_mentions(text: str) -> str:
    """Remove every ``<@U...>`` so the command word is the first token."""
    return MENTION_RE.sub(" ", text or "").strip()


def parse_command(text: str) -> Command:
    """Parse the text of an app mention.

    The command word is matched case-insensitively, so `Verdict` and
    `VERDICT` both work -- someone typing into Slack on a phone gets an
    initial capital for free.
    """
    body = strip_mentions(text)
    if not body:
        return Command(name=HELP)

    parts = body.split()
    word = parts[0].strip().lower().lstrip("/")
    word = word.rstrip(":,.")

    if word not in KNOWN_COMMANDS:
        return Command(name=HELP, unknown_word=parts[0])

    remainder = " ".join(parts[1:]).strip()
    if not remainder:
        return Command(name=word)

    return Command(name=word, argument=first_argument(remainder) or None)


def first_argument(remainder: str) -> str:
    """Take the first argument out of what follows the command word.

    Splitting on whitespace is not enough: Slack writes a link with a label
    as ``<https://example.com/page|the page>``, and the label has spaces in
    it, so the first whitespace-delimited token is half a link.
    """
    if remainder.startswith("<"):
        end = remainder.find(">")
        if end != -1:
            return unwrap_link(remainder[: end + 1])
    return unwrap_link(remainder.split()[0])
