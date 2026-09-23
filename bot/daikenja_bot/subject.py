"""What the model is asked to read.

A subject is whatever a command works on: the thread the command was typed
in, a thread somewhere else, a page, or the list of items a feeder handed to
the digest. It is plain text by the time it reaches this type -- fetching is
done, and nothing downstream talks to Slack or Confluence again.
"""

from __future__ import annotations

from dataclasses import dataclass, field

THREAD = "Slack thread"
PAGE = "Confluence page"
ISSUE = "Jira issue"
# The digest's subject is not something anyone wrote: it is a list another
# process collected. It is still other people's words, so it is still data
# and not instruction, which is the only property the prompt cares about.
ITEMS = "digest item list"


@dataclass(frozen=True)
class UnreadLink:
    """A link the subject pointed at that could not be read, and why."""

    url: str
    reason: str


@dataclass(frozen=True)
class Subject:
    kind: str
    label: str
    body: str
    source_url: str | None = None
    # What the subject links to, fetched one hop deep by `follow`. Each is a
    # subject in its own right, and still other people's words.
    attachments: tuple["Subject", ...] = field(default=())
    unread: tuple[UnreadLink, ...] = field(default=())

    @property
    def is_empty(self) -> bool:
        return not self.body.strip()
