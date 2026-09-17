"""What the model is asked to read.

A subject is whatever a command works on: the thread the command was typed
in, a thread somewhere else, a page, or the list of items a feeder handed to
the digest. It is plain text by the time it reaches this type -- fetching is
done, and nothing downstream talks to Slack or Confluence again.
"""

from __future__ import annotations

from dataclasses import dataclass

THREAD = "Slack thread"
PAGE = "Confluence page"
# The digest's subject is not something anyone wrote: it is a list another
# process collected. It is still other people's words, so it is still data
# and not instruction, which is the only property the prompt cares about.
ITEMS = "digest item list"


@dataclass(frozen=True)
class Subject:
    kind: str
    label: str
    body: str
    source_url: str | None = None

    @property
    def is_empty(self) -> bool:
        return not self.body.strip()
