"""Optional: fetch a Confluence page so `judgement` can be run against it.

A Slack bot token opens nothing in Confluence, so this needs credentials of
its own. They are optional by design: with no `confluence` block in
`bot.yaml` the bot answers in the thread that Confluence links are not
configured and stops, which is a config gap rather than a failure.

Only the standard library is used. The repository ships inside every plugin
install, so a second HTTP client for one optional feature is weight
everybody would carry.
"""

from __future__ import annotations

import base64
import html
import json
import logging
import re
import urllib.error
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Union

from .config import ConfluenceConfig
from .links import PageTitleRef, parse_confluence_page_id
from .subject import PAGE, Subject

log = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30

CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
BREAK_RE = re.compile(
    r"</(?:p|div|h[1-6]|tr|li|ul|ol|table|blockquote)>|<br\s*/?>", re.IGNORECASE
)
LIST_ITEM_RE = re.compile(r"<li[^>]*>", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
BLANK_LINES_RE = re.compile(r"\n{3,}")

# The links a page holds, read from storage format before it is flattened:
# an ordinary anchor, and an internal link, which names a page by title.
# A page reference inside an attachment or image names where a file lives,
# not a document to read, so those blocks are dropped before the scan.
LINK_RE = re.compile(
    r"<a\s[^>]*?href=\"(?P<href>[^\"]+)\""
    r"|<ri:page\s(?P<page>[^>]*?)/?>"
    r"|<ac:structured-macro\s[^>]*?ac:name=\"jira\"[^>]*>(?P<jira>.*?)</ac:structured-macro>",
    re.IGNORECASE | re.DOTALL,
)
JIRA_KEY_PARAM_RE = re.compile(
    r"<ac:parameter\s[^>]*?ac:name=\"key\"[^>]*>\s*(?P<key>[^<\s]+)\s*</ac:parameter>",
    re.IGNORECASE,
)
ATTR_RE = re.compile(r"(?P<name>[\w:-]+)=\"(?P<value>[^\"]*)\"")
FILE_BLOCK_RE = re.compile(
    r"<(?P<tag>ri:attachment|ac:image)\b.*?</(?P=tag)>", re.DOTALL | re.IGNORECASE
)
SPACE_IN_URL_RE = re.compile(r"/spaces/(?P<key>[^/]+)/")

# What a page links to: a URL, or a title still to be looked up.
PageLink = Union[str, PageTitleRef]
Fetch = Callable[..., bytes]


class ConfluenceError(Exception):
    """The page could not be fetched, or the link was not one we can read.

    ``reason`` is the few words a followed link's failure is recorded with;
    the message is the sentence a person is told when the page they asked for
    fails.
    """

    def __init__(self, message: str, reason: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason or message


class ConfluenceNotConfigured(ConfluenceError):
    """There is no `confluence` block in the config."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or "Confluence links are not configured on this bot. Add a "
            "`confluence` block to bot.yaml to turn them on.",
            reason="Confluence not configured",
        )


@dataclass(frozen=True)
class Page:
    """A fetched page and the links it holds, read from one payload."""

    subject: Subject
    links: tuple[PageLink, ...] = ()
    space_key: str | None = None


def storage_to_text(storage: str) -> str:
    """Flatten Confluence storage format into readable plain text.

    Not a full XHTML parser, and it does not need to be: the model is
    reading the page's words, not rendering it. Block ends become line
    breaks, list items get a dash, macro bodies in CDATA are kept, and every
    remaining tag is dropped.
    """
    if not storage:
        return ""
    text = CDATA_RE.sub(lambda m: m.group(1), storage)
    text = LIST_ITEM_RE.sub("\n- ", text)
    text = BREAK_RE.sub("\n", text)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    lines = [line.rstrip() for line in text.split("\n")]
    return BLANK_LINES_RE.sub("\n\n", "\n".join(lines)).strip()


def storage_links(storage: str, base_url: str | None = None) -> list[PageLink]:
    """The links in a page's storage format, in order, each once.

    A `jira` macro names an issue by key, which becomes a link on
    ``base_url`` -- the one site both products share. Without a base URL
    there is nowhere to point it, and it is skipped.
    """
    scanned = FILE_BLOCK_RE.sub("", storage or "")
    found: list[PageLink] = []
    for match in LINK_RE.finditer(scanned):
        link: PageLink | None = None
        if match.group("href") is not None:
            href = html.unescape(match.group("href")).strip()
            if href.startswith(("http://", "https://")):
                link = href
        elif match.group("jira") is not None:
            key = JIRA_KEY_PARAM_RE.search(match.group("jira"))
            if key and base_url:
                link = f"{base_url.rstrip('/')}/browse/{key.group('key')}"
        else:
            attrs = {
                a.group("name").lower(): html.unescape(a.group("value"))
                for a in ATTR_RE.finditer(match.group("page"))
            }
            title = attrs.get("ri:content-title", "").strip()
            if title:
                link = PageTitleRef(
                    title=title, space_key=attrs.get("ri:space-key") or None
                )
        if link is not None and link not in found:
            found.append(link)
    return found


def space_key_of(url: str) -> str | None:
    """The space key a long page URL names, if it names one."""
    match = SPACE_IN_URL_RE.search(urllib.parse.urlparse(url).path)
    return urllib.parse.unquote(match.group("key")) if match else None


def _auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _default_fetch(
    url: str, headers: dict[str, str], timeout: float = REQUEST_TIMEOUT
) -> bytes:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ConfluenceError(
                "Confluence rejected the credentials in bot.yaml",
                reason=f"HTTP {exc.code}, credentials rejected",
            ) from exc
        if exc.code == 404:
            raise ConfluenceError(
                "that page does not exist, or this Confluence account cannot see it",
                reason="not found or not visible",
            ) from exc
        raise ConfluenceError(
            f"Confluence returned HTTP {exc.code}", reason=f"HTTP {exc.code}"
        ) from exc
    except TimeoutError as exc:
        raise ConfluenceError(
            "Confluence did not answer in time", reason="timed out"
        ) from exc
    except urllib.error.URLError as exc:
        raise ConfluenceError(
            f"could not reach Confluence: {exc.reason}", reason="unreachable"
        ) from exc


def fetcher(timeout: float) -> Fetch:
    """The default HTTP call with a different per-request timeout."""

    def fetch(url: str, headers: dict[str, str]) -> bytes:
        return _default_fetch(url, headers, timeout)

    return fetch


def _check(config: ConfluenceConfig | None, token: str | None) -> ConfluenceConfig:
    if config is None:
        raise ConfluenceNotConfigured()
    if not token:
        raise ConfluenceError(
            "no Confluence token is set. Export the variable named by "
            "confluence.token_env before starting the bot.",
            reason="no Confluence token",
        )
    return config


def _get_json(fetch: Fetch, url: str, config: ConfluenceConfig, token: str) -> Any:
    payload = fetch(
        url,
        {
            "Authorization": _auth_header(config.email, token),
            "Accept": "application/json",
        },
    )
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfluenceError(
            "Confluence returned something that is not JSON", reason="not JSON"
        ) from exc


def read_page(
    config: ConfluenceConfig | None,
    url: str,
    token: str | None,
    fetch: Fetch = _default_fetch,
) -> Page:
    """Fetch one page, and the links it holds, from a single request."""
    config = _check(config, token)
    assert token  # _check refused a missing one

    page_id = parse_confluence_page_id(url)
    if not page_id:
        raise ConfluenceError(
            "that Confluence link carries no page id. Open the page and copy "
            "the full URL from the address bar -- a short /wiki/x/ link cannot "
            "be resolved without following it.",
            reason="short link has no page id",
        )

    endpoint = f"{config.base_url}/wiki/api/v2/pages/{page_id}?body-format=storage"
    data = _get_json(fetch, endpoint, config, token)
    if not isinstance(data, dict):
        raise ConfluenceError(
            "Confluence returned something that is not a page", reason="not a page"
        )

    title = str(data.get("title") or f"page {page_id}")
    storage = ((data.get("body") or {}).get("storage") or {}).get("value") or ""
    body = storage_to_text(storage)
    if not body:
        raise ConfluenceError(
            f"'{title}' came back empty, so there is nothing to judge",
            reason="page is empty",
        )

    return Page(
        subject=Subject(kind=PAGE, label=title, body=body, source_url=url),
        links=tuple(storage_links(storage, config.base_url)),
        space_key=space_key_of(url),
    )


def fetch_page(
    config: ConfluenceConfig | None,
    url: str,
    token: str | None,
    fetch: Fetch = _default_fetch,
) -> Subject:
    """Fetch one page and return it as a subject the prompt builders accept."""
    return read_page(config, url, token, fetch).subject


def find_page(
    config: ConfluenceConfig | None,
    ref: PageTitleRef,
    token: str | None,
    fetch: Fetch = _default_fetch,
    default_space: str | None = None,
) -> str:
    """Look up a page linked by title, and return a URL `read_page` accepts.

    The space defaults to the linking page's own, as Confluence does. With no
    space known at all the title is searched everywhere, and only a single
    match is taken: two pages with the same title in different spaces is a
    guess, and a wrong page read confidently is worse than one not read.
    """
    config = _check(config, token)
    assert token
    query = {"title": ref.title, "limit": "2"}
    space = ref.space_key or default_space
    if space:
        query["spaceKey"] = space
    endpoint = (
        f"{config.base_url}/wiki/rest/api/content?"
        + urllib.parse.urlencode(query)
    )
    data = _get_json(fetch, endpoint, config, token)
    results = data.get("results") if isinstance(data, dict) else None
    if not results:
        raise ConfluenceError(
            f"no page titled '{ref.title}'", reason="not found or not visible"
        )
    if len(results) > 1:
        raise ConfluenceError(
            f"several pages are titled '{ref.title}'",
            reason="title matches several pages",
        )
    page_id = str(results[0].get("id") or "")
    if not page_id.isdigit():
        raise ConfluenceError(
            f"the page titled '{ref.title}' came back with no id",
            reason="lookup returned no page id",
        )
    return f"{config.base_url}/wiki/pages/viewpage.action?pageId={page_id}"
