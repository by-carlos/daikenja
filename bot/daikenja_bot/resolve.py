"""Turn one link into one subject, whichever source it belongs to.

The handler used to decide this in a chain of `if permalink ... elif
confluence`. Following links out of a subject needs the same decision for
every link it finds, so it lives here, once: `kind_of` says which source a
link belongs to without fetching anything, and `resolve` fetches it.

A resolved subject comes back with the links it holds, read from the raw
source -- Slack's message payloads, a page's storage format -- because by
the time a subject is plain text an unfurl card's URL or a page's internal
link is gone.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Union
from urllib.parse import urlparse

from .config import BotConfig, resolve_secret
from .confluence import (
    ConfluenceNotConfigured,
    Page,
    _default_fetch,
    fetcher,
    find_page,
    read_page,
)
from .jira import JiraNotConfigured, fetch_issue
from .jira import _default_fetch as jira_default_fetch
from .jira import fetcher as jira_fetcher
from .links import (
    PageTitleRef,
    extract_links,
    forwarded_permalink,
    looks_like_confluence,
    looks_like_jira,
    parse_slack_permalink,
    unwrap_link,
)
from .slack_io import SlackError, SlackIO, thread_participants
from .subject import Subject
from .transcript import render_thread

log = logging.getLogger(__name__)

SLACK = "slack"
CONFLUENCE = "confluence"
JIRA = "jira"

# A link as `follow` handles it: a URL, or a page named only by its title.
Link = Union[str, PageTitleRef]


@dataclass(frozen=True)
class Resolved:
    """A fetched subject, the links it holds, and the space it lives in."""

    subject: Subject
    links: tuple[Link, ...] = ()
    # A page's own space, which a title-only link inside it defaults to.
    space_key: str | None = None


class Resolver:
    """Fetches whatever a link points at, with the bot's own credentials."""

    def __init__(
        self,
        config: BotConfig,
        slack: SlackIO,
        environ: Mapping[str, str],
        *,
        fetch_confluence: Callable[..., Any] | None = None,
        find_confluence_page: Callable[..., str] | None = None,
        fetch_jira: Callable[..., Subject] | None = None,
    ) -> None:
        self._config = config
        self._slack = slack
        self._environ = environ
        # Stand-ins from the tests take `(config, url, token)` and may hand
        # back a bare subject; None means the real HTTP calls.
        self._fetch_confluence = fetch_confluence
        self._find_confluence_page = find_confluence_page
        self._fetch_jira = fetch_jira

    # -- what a link is --------------------------------------------------

    def kind_of(self, link: Link, *, found: bool = False) -> str | None:
        """Which source a link belongs to, or None when it is none of them.

        ``found`` is for a link read out of content rather than typed as an
        argument. The loose Confluence test that lets an unconfigured bot say
        why it is not answering would also claim every ``/wiki/`` URL on the
        web, so a found link must be on the configured site -- or, with no
        site configured, on Atlassian Cloud's own wiki path, which is then
        recorded as not configured rather than ignored.
        """
        if isinstance(link, PageTitleRef):
            return CONFLUENCE
        url = unwrap_link(link)
        if parse_slack_permalink(url):
            return SLACK
        base_url = self._config.confluence.base_url if self._config.confluence else None
        # Before Confluence: the loose Confluence test claims every
        # `*.atlassian.net` URL, and a Jira link is one of those.
        if looks_like_jira(url, base_url):
            return JIRA
        if found:
            parsed = urlparse(url)
            if base_url:
                base = urlparse(base_url if "//" in base_url else f"https://{base_url}")
                on_site = bool(base.netloc) and parsed.netloc == base.netloc
            else:
                on_site = parsed.netloc.endswith(".atlassian.net")
            if on_site and parsed.path.startswith("/wiki/"):
                return CONFLUENCE
            return None
        if looks_like_confluence(url, base_url):
            return CONFLUENCE
        return None

    # -- fetching --------------------------------------------------------

    def resolve(
        self,
        link: Link,
        *,
        timeout: float | None = None,
        default_space: str | None = None,
        limit: int | None = None,
    ) -> Resolved | None:
        """Fetch one link. None when it belongs to no source this bot reads.

        ``timeout`` shortens each HTTP request, for a followed link; the main
        subject keeps the fetcher's own default. ``limit`` lets a Jira issue
        trim itself to size from its oldest comments, where cutting the end
        would lose the latest decision.
        """
        kind = self.kind_of(link)
        if kind == SLACK:
            url = unwrap_link(str(link))
            ref = parse_slack_permalink(url)
            assert ref is not None
            return self.thread(ref.channel_id, ref.thread_ts, source_url=url)
        if kind == CONFLUENCE:
            return self._page(link, timeout=timeout, default_space=default_space)
        if kind == JIRA:
            return self._issue(str(link), timeout=timeout, limit=limit)
        return None

    def thread(
        self,
        channel_id: str,
        thread_ts: str,
        source_url: str | None = None,
        follow_forward: bool = False,
    ) -> Resolved:
        messages = self._slack.fetch_thread(channel_id, thread_ts)
        if not messages:
            raise SlackError("that thread came back empty")

        if follow_forward:
            # A thread whose parent is a forwarded message is a wrapper around
            # the real subject. Followed once and only from the no-argument
            # path: a link the user typed is what they asked for, whatever the
            # thread around it holds. A failure here is reported rather than
            # quietly falling back -- summarising the wrapper is the defect
            # this exists to stop, and doing it silently is worse.
            forwarded = forwarded_permalink(messages[0])
            ref = parse_slack_permalink(forwarded) if forwarded else None
            if ref:
                return self.thread(ref.channel_id, ref.thread_ts, source_url=forwarded)

        messages = self._without_own_messages(messages)
        if not messages:
            raise SlackError("that thread came back empty")
        users = self._slack.user_names(thread_participants(messages))
        subject = render_thread(
            messages,
            users=users,
            channel_label=self._slack.channel_label(channel_id),
            source_url=source_url,
        )
        return Resolved(subject=subject, links=tuple(thread_links(messages)))

    def _without_own_messages(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Drop what this bot itself has already posted into the thread.

        A second command in a thread the bot has answered would otherwise be
        handed its own earlier answer as thread content, and summarise the
        summary. Only this bot's messages go: another app's post is somebody's
        actual content and stays.
        """
        own = self._slack.bot_user_id()
        if not own:
            return messages
        return [m for m in messages if str(m.get("user") or "") != own]

    def _token(self) -> str:
        confluence = self._config.confluence
        assert confluence is not None
        return resolve_secret(
            label="the Confluence token",
            env_name=confluence.token_env,
            file_path=confluence.token_file,
            inline=confluence.token,
            environ=dict(self._environ),
        )

    def _issue(self, url: str, *, timeout: float | None, limit: int | None) -> Resolved:
        # Jira rides on the `confluence` block: one site, one token.
        confluence = self._config.confluence
        if confluence is None:
            raise JiraNotConfigured()
        token = self._token()
        url = unwrap_link(url)
        if self._fetch_jira is not None:
            subject = self._fetch_jira(confluence, url, token, limit=limit)
        else:
            fetch = jira_fetcher(timeout) if timeout else jira_default_fetch
            subject = fetch_issue(confluence, url, token, fetch, limit)
        return Resolved(subject=subject)

    def _page(
        self, link: Link, *, timeout: float | None, default_space: str | None
    ) -> Resolved:
        confluence = self._config.confluence
        if confluence is None:
            raise ConfluenceNotConfigured()
        token = self._token()
        fetch = fetcher(timeout) if timeout else _default_fetch

        if isinstance(link, PageTitleRef):
            if self._find_confluence_page is not None:
                url = self._find_confluence_page(confluence, link, token)
            else:
                url = find_page(confluence, link, token, fetch, default_space)
        else:
            url = unwrap_link(link)

        if self._fetch_confluence is not None:
            page = self._fetch_confluence(confluence, url, token)
        else:
            page = read_page(confluence, url, token, fetch)
        if isinstance(page, Subject):
            page = Page(subject=page)
        return Resolved(subject=page.subject, links=page.links, space_key=page.space_key)


def thread_links(messages: list[Mapping[str, Any]]) -> list[str]:
    """The links in a thread's raw messages, in order, each once.

    The text alone misses one case that matters: a Confluence page pasted as
    an unfurl card ("Added by Confluence Cloud") keeps its URL on the
    attachment, as ``title_link`` or ``original_url``.
    """
    found: list[str] = []
    for message in messages:
        candidates = extract_links(str(message.get("text") or ""))
        for attachment in message.get("attachments") or []:
            if not isinstance(attachment, Mapping):
                continue
            for key in ("title_link", "original_url"):
                value = str(attachment.get(key) or "").strip()
                if value:
                    candidates.extend(extract_links(value) or [value])
        for url in candidates:
            if url not in found:
                found.append(url)
    return found
