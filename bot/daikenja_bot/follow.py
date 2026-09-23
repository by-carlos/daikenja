"""Read what a subject links to, one hop deep, and attach it.

A thread that says "please review this page" is judged without the page
unless something fetches the page. That happens here, in the bot, before the
model starts: the headless session has no network by design, and giving it
Atlassian tools would put the token inside the model process.

Nothing that goes wrong here stops a run. A link that cannot be read is
recorded with a short reason and shown to the model, so the answer can say
a linked page could not be read rather than guess at it.
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
import logging
from typing import TYPE_CHECKING, Iterable

from .config import ConfigError
from .confluence import ConfluenceError
from .links import PageTitleRef
from .slack_io import SlackError
from .subject import PAGE, Subject, UnreadLink

if TYPE_CHECKING:
    from .resolve import Link, Resolver

log = logging.getLogger(__name__)

# Limits are constants, not configuration: they bound the cost of one
# command, and nobody should have to tune them to get a sensible answer.
MAX_LINKS = 6
MAX_CHARS = 12_000
MAX_TOTAL_CHARS = 40_000
REQUEST_TIMEOUT = 15
DEADLINE = 45
# Below this much room left in the total, an attachment is dropped rather
# than clipped: a few hundred characters of a page say too little to use.
MIN_USEFUL_CHARS = 500

# Sources a link *found in content* is followed into. A Slack permalink is
# followed only when it was typed as an argument.
FOLLOWED_WHEN_FOUND = ("confluence", "jira")


def follow(
    subject: Subject,
    extra: Iterable[str],
    resolver: "Resolver",
    links_in: Iterable["Link"],
    *,
    space_key: str | None = None,
    deadline: float = DEADLINE,
) -> Subject:
    """The subject, with what it links to attached and what failed noted."""
    candidates: list[Link] = []
    unread: list[UnreadLink] = []
    seen: set[object] = {subject.source_url}

    for url in extra:
        if url in seen:
            continue
        seen.add(url)
        if resolver.kind_of(url) is None:
            unread.append(UnreadLink(url, "not a link I can read"))
            continue
        candidates.append(url)

    for link in links_in:
        if link in seen or _is_self(link, subject):
            continue
        seen.add(link)
        if resolver.kind_of(link, found=True) in FOLLOWED_WHEN_FOUND:
            candidates.append(link)

    for link in candidates[MAX_LINKS:]:
        unread.append(UnreadLink(_name(link), "over the link limit"))
    candidates = candidates[:MAX_LINKS]

    fetched = _fetch_all(candidates, resolver, space_key, deadline)

    attachments: list[Subject] = []
    budget = MAX_TOTAL_CHARS
    for link, outcome in zip(candidates, fetched):
        if isinstance(outcome, str):
            unread.append(UnreadLink(_name(link), outcome))
            continue
        if budget < MIN_USEFUL_CHARS:
            unread.append(UnreadLink(_name(link), "over the size limit"))
            continue
        body = truncate(outcome.body, min(MAX_CHARS, budget))
        budget -= len(body)
        attachments.append(dataclasses.replace(outcome, body=body))

    if not attachments and not unread:
        return subject
    return dataclasses.replace(
        subject, attachments=tuple(attachments), unread=tuple(unread)
    )


def truncate(body: str, limit: int) -> str:
    """Keep the start of a body and say where it was cut."""
    if len(body) <= limit:
        return body
    return f"{body[:limit].rstrip()}\n[truncated at {limit} characters]"


def reason_of(exc: BaseException) -> str:
    """The few words a failed link is recorded with."""
    if isinstance(exc, ConfluenceError):
        return exc.reason
    if isinstance(exc, ConfigError):
        return "credentials not set"
    if isinstance(exc, SlackError):
        return str(exc) or "Slack refused it"
    return "could not be read"


def _is_self(link: "Link", subject: Subject) -> bool:
    """A page's internal link back to itself, by title."""
    return (
        isinstance(link, PageTitleRef)
        and subject.kind == PAGE
        and link.title == subject.label
    )


def _name(link: "Link") -> str:
    return str(link) if isinstance(link, PageTitleRef) else link


def _fetch_all(
    links: list["Link"],
    resolver: "Resolver",
    space_key: str | None,
    deadline: float,
) -> list[Subject | str]:
    """Fetch every link in parallel. Each result is a subject or a reason."""
    if not links:
        return []

    def fetch(link: "Link") -> Subject | str:
        resolved = resolver.resolve(
            link,
            timeout=REQUEST_TIMEOUT,
            default_space=space_key,
            limit=MAX_CHARS,
        )
        if resolved is None:
            return "not a link I can read"
        return resolved.subject

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=len(links))
    try:
        futures = [pool.submit(fetch, link) for link in links]
        concurrent.futures.wait(futures, timeout=deadline)
        results: list[Subject | str] = []
        for link, future in zip(links, futures):
            if not future.done():
                # Abandoned, not waited for: its own request timeout ends it.
                results.append("timed out")
                continue
            exc = future.exception()
            if exc is not None:
                log.info("could not follow %s: %s", _name(link), exc)
                results.append(reason_of(exc))
            else:
                results.append(future.result())
        return results
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
