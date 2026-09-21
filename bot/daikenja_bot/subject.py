"""What the model is asked to read.

A subject is whatever `summary` or `judgement` works on: the thread the
command was typed in, a thread somewhere else, or a page. It is plain text
by the time it reaches this type -- fetching is done, and nothing downstream
talks to Slack or Confluence again.
"""

from __future__ import annotations

from dataclasses import dataclass

THREAD = "Slack thread"
PAGE = "Confluence page"


@dataclass(frozen=True)
class Subject:
    kind: str
    label: str
    body: str
    source_url: str | None = None

    @property
    def is_empty(self) -> bool:
        return not self.body.strip()
