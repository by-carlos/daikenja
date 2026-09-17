"""Read the two kinds of link a command can take as its argument.

Slack rewrites a URL inside a message as ``<https://...>``, or
``<https://...|the text the user saw>``. Everything here starts by undoing
that, because a link that still carries the angle brackets matches nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import parse_qs, unquote, urlparse

SLACK_ARCHIVE_RE = re.compile(
    r"^/archives/(?P<channel>[A-Z][A-Z0-9]+)/p(?P<ts>\d{10,}\d{6})/?$"
)
CONFLUENCE_PAGE_RE = re.compile(r"/pages/(?P<page_id>\d+)")


@dataclass(frozen=True)
class SlackThreadRef:
    """Where a Slack permalink points."""

    channel_id: str
    thread_ts: str
    message_ts: str

    @property
    def is_thread_parent(self) -> bool:
        return self.thread_ts == self.message_ts


def unwrap_link(text: str) -> str:
    """Strip Slack's ``<...>`` and ``<...|label>`` wrapping from one token."""
    token = text.strip()
    if token.startswith("<") and token.endswith(">"):
        token = token[1:-1]
        if "|" in token:
            token = token.split("|", 1)[0]
    return token.strip()


def parse_slack_permalink(url: str) -> SlackThreadRef | None:
    """Turn a Slack message permalink into a channel and a thread timestamp.

    A permalink's ``p1726531200123456`` is the message timestamp with its
    dot removed, and the last six digits are the fractional part. When the
    link points at a reply rather than at the parent, Slack adds
    ``?thread_ts=``; that value is the thread to fetch.
    """
    parsed = urlparse(unwrap_link(url))
    if parsed.scheme not in ("http", "https"):
        return None
    if not parsed.netloc.endswith(".slack.com"):
        return None

    match = SLACK_ARCHIVE_RE.match(parsed.path)
    if not match:
        return None

    raw_ts = match.group("ts")
    message_ts = f"{raw_ts[:-6]}.{raw_ts[-6:]}"

    query = parse_qs(parsed.query)
    thread_ts = message_ts
    if query.get("thread_ts"):
        candidate = query["thread_ts"][0].strip()
        if candidate:
            thread_ts = candidate

    channel_id = match.group("channel")
    if query.get("cid"):
        # `cid` is authoritative when both are present: a shared-channel
        # permalink can carry the other workspace's id in the path.
        candidate = query["cid"][0].strip()
        if candidate:
            channel_id = candidate

    return SlackThreadRef(
        channel_id=channel_id, thread_ts=thread_ts, message_ts=message_ts
    )


def forwarded_permalink(message: Mapping[str, Any]) -> str | None:
    """The permalink a forwarded Slack message carries, if this is one.

    Sharing a message into another channel leaves almost nothing in the text
    of the message that lands: the whole of it travels in an attachment, and
    the original's permalink is that attachment's ``from_url``. Without this,
    a command working on the enclosing thread gets an empty parent and
    summarises the wrapper instead of what was forwarded.

    The URL is handed back rather than the parsed reference so the caller can
    both fetch the original and name it as the source of its answer.
    """
    for attachment in message.get("attachments") or []:
        if not isinstance(attachment, Mapping):
            continue
        url = str(attachment.get("from_url") or "").strip()
        if url and parse_slack_permalink(url):
            return url
    return None


def parse_confluence_page_id(url: str) -> str | None:
    """Pull the numeric page id out of a Confluence URL.

    Handles the two long forms -- ``/wiki/spaces/SPACE/pages/123/Title`` and
    ``viewpage.action?pageId=123``. A ``/wiki/x/SHORT`` tiny link carries no
    id and needs a redirect to resolve, so it comes back as None and the
    caller says the link is not supported.
    """
    parsed = urlparse(unwrap_link(url))
    if parsed.scheme not in ("http", "https"):
        return None

    query = parse_qs(parsed.query)
    if query.get("pageId"):
        candidate = query["pageId"][0].strip()
        if candidate.isdigit():
            return candidate

    match = CONFLUENCE_PAGE_RE.search(unquote(parsed.path))
    if match:
        return match.group("page_id")
    return None


def looks_like_confluence(url: str, base_url: str | None = None) -> bool:
    """Is this a Confluence link?

    A configured ``base_url`` is the reliable test. Without one, fall back
    to the shape every Atlassian Cloud wiki URL has, so an unconfigured bot
    can still tell the user *why* it is not answering.
    """
    parsed = urlparse(unwrap_link(url))
    if parsed.scheme not in ("http", "https"):
        return False
    if base_url:
        base = urlparse(base_url if "//" in base_url else f"https://{base_url}")
        if base.netloc and parsed.netloc == base.netloc:
            return True
    if parsed.netloc.endswith(".atlassian.net"):
        return True
    return "/wiki/" in parsed.path or "confluence" in parsed.netloc
