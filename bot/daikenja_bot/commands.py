"""Read what was asked for out of the text of an @-mention.

Three commands. `summary` and `judgement` each may carry a link as their
argument, and further links after it, which are read alongside as
attachments; with no argument, the subject is the thread the mention was
typed in. `delete` takes no argument and removes the bot's own last post in
that thread. Anything else comes back as `help`, which the transport answers
with one line of usage rather than guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .links import unwrap_link

MENTION_RE = re.compile(r"<@[UWB][A-Z0-9]+(?:\|[^>]*)?>")
# One argument token: a Slack-wrapped link, label and all, or a bare word.
TOKEN_RE = re.compile(r"<[^>]*>|\S+")

SUMMARY = "summary"
JUDGEMENT = "judgement"
DELETE = "delete"
HELP = "help"

KNOWN_COMMANDS = (SUMMARY, JUDGEMENT, DELETE)

# Commands that read a subject and run a headless session. `delete` does
# neither: it is answered out of Slack alone.
SUBJECT_COMMANDS = (SUMMARY, JUDGEMENT)

# A command word may also be written as an emoji. Slack sends whichever form
# the client produced -- the picker writes the `:shortcode:`, a phone keyboard
# writes the character -- so both are accepted.
ALIASES = {
    ":point_up_2:": JUDGEMENT,
    "\N{WHITE UP POINTING BACKHAND INDEX}": JUDGEMENT,
}

# Skin-tone modifiers and the emoji variation selector, dropped before an
# alias is looked up: 👆🏽 is the same command as 👆.
EMOJI_MODIFIERS = "️\U0001f3fb\U0001f3fc\U0001f3fd\U0001f3fe\U0001f3ff"

# The word that names a project explicitly, ahead of any link: `judgement
# project harbor`. The bot does not check the key against anything -- it has
# never read `daikenja.yaml` and this is not the place to start. The skill
# already treats a named key as decisive and stops on one it does not
# recognise, naming the keys it does, so an unknown key comes back as an
# answer rather than as a parse failure.
PROJECT_KEYWORD = "project"

USAGE = (
    "I take three commands. `@daikenja summary` for what this thread is "
    "asking and what is still open, `@daikenja judgement` (or :point_up_2:) "
    "for a check of the thread against the project's ledger, and "
    "`@daikenja delete` to remove my own last post here. `summary` and "
    "`judgement` each take a link -- a Slack thread, a Confluence page or a "
    "Jira issue -- "
    "to work on that instead of this thread, further links after it to read "
    "alongside, and `project <key>` before it to say which project's ledger "
    "to check."
)


@dataclass(frozen=True)
class Command:
    """One parsed invocation."""

    name: str
    argument: str | None = None
    unknown_word: str | None = None
    project: str | None = None
    # Links after the first, read as attachments to the subject.
    extra: tuple[str, ...] = ()

    @property
    def is_known(self) -> bool:
        return self.name in KNOWN_COMMANDS


def strip_mentions(text: str) -> str:
    """Remove every ``<@U...>`` so the command word is the first token."""
    return MENTION_RE.sub(" ", text or "").strip()


def parse_command(text: str) -> Command:
    """Parse the text of an app mention.

    The command word is matched case-insensitively, so `Judgement` and
    `JUDGEMENT` both work -- someone typing into Slack on a phone gets an
    initial capital for free.
    """
    body = strip_mentions(text)
    if not body:
        return Command(name=HELP)

    parts = body.split()
    word = alias_for(parts[0])
    if word is None:
        # Not an emoji: the trailing `:` an alias needs is punctuation here.
        word = parts[0].strip().lower().lstrip("/").rstrip(":,.")

    if word not in KNOWN_COMMANDS:
        return Command(name=HELP, unknown_word=parts[0])

    rest = parts[1:]
    if not rest or word not in SUBJECT_COMMANDS:
        # `delete` acts on the thread it was typed in and nothing else, so
        # anything after it is not an argument and is not treated as one --
        # neither a link nor a `project <key>`.
        return Command(name=word)

    project = None
    if rest[0].strip().lower().rstrip(":,.") == PROJECT_KEYWORD:
        if len(rest) < 2:
            # `judgement project` with nothing after it. The usage line names
            # the form, so answering with it says more than guessing which
            # project was meant.
            return Command(name=HELP)
        project = rest[1]
        rest = rest[2:]

    remainder = " ".join(rest).strip()
    argument = first_argument(remainder) if remainder else None
    return Command(
        name=word,
        argument=argument or None,
        project=project,
        extra=extra_links(remainder),
    )


def extra_links(remainder: str) -> tuple[str, ...]:
    """Every link after the first argument, in order, each once.

    Words between them -- `and`, a comma -- are not arguments and are
    dropped, so `judgement <a> and <b>` reads the same as `judgement <a> <b>`.
    """
    tokens = TOKEN_RE.findall(remainder or "")[1:]
    found: list[str] = []
    for token in tokens:
        url = unwrap_link(token.rstrip(",;"))
        if url.startswith(("http://", "https://")) and url not in found:
            found.append(url)
    return tuple(found)


def alias_for(token: str) -> str | None:
    """The command an emoji token stands for, or None if it is not one."""
    candidate = (token or "").strip().lower()
    candidate = candidate.strip(EMOJI_MODIFIERS)
    return ALIASES.get(candidate)


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
