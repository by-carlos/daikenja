"""What the model is asked to read.

A subject is whatever `summary` or `judgement` works on: the thread the
command was typed in, a thread somewhere else, a page, or a Jira issue. It
is plain text by the time it reaches this type -- fetching is done, and
nothing downstream talks to Slack, Confluence or Jira again.
"""

from __future__ import annotations

from dataclasses import dataclass, field

THREAD = "Slack thread"
PAGE = "Confluence page"
ISSUE = "Jira issue"


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
