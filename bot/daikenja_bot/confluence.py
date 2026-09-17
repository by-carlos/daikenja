"""Optional: fetch a Confluence page so `verdict` can be run against it.

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
from typing import Any, Callable

from .config import ConfluenceConfig
from .links import parse_confluence_page_id
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


class ConfluenceError(Exception):
    """The page could not be fetched, or the link was not one we can read."""


class ConfluenceNotConfigured(ConfluenceError):
    """There is no `confluence` block in the config."""


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


def _auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _default_fetch(url: str, headers: dict[str, str]) -> bytes:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ConfluenceError(
                "Confluence rejected the credentials in bot.yaml"
            ) from exc
        if exc.code == 404:
            raise ConfluenceError(
                "that page does not exist, or this Confluence account cannot see it"
            ) from exc
        raise ConfluenceError(f"Confluence returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ConfluenceError(f"could not reach Confluence: {exc.reason}") from exc


def fetch_page(
    config: ConfluenceConfig | None,
    url: str,
    token: str | None,
    fetch: Callable[[str, dict[str, str]], bytes] = _default_fetch,
) -> Subject:
    """Fetch one page and return it as a subject the prompt builders accept."""
    if config is None:
        raise ConfluenceNotConfigured(
            "Confluence links are not configured on this bot. Add a "
            "`confluence` block to bot.yaml to turn them on."
        )
    if not token:
        raise ConfluenceError(
            "no Confluence token is set. Export the variable named by "
            "confluence.token_env before starting the bot."
        )

    page_id = parse_confluence_page_id(url)
    if not page_id:
        raise ConfluenceError(
            "that Confluence link carries no page id. Open the page and copy "
            "the full URL from the address bar -- a short /wiki/x/ link cannot "
            "be resolved without following it."
        )

    endpoint = f"{config.base_url}/wiki/api/v2/pages/{page_id}?body-format=storage"
    payload = fetch(
        endpoint,
        {
            "Authorization": _auth_header(config.email, token),
            "Accept": "application/json",
        },
    )

    try:
        data: dict[str, Any] = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfluenceError("Confluence returned something that is not JSON") from exc

    title = str(data.get("title") or f"page {page_id}")
    storage = ((data.get("body") or {}).get("storage") or {}).get("value") or ""
    body = storage_to_text(storage)
    if not body:
        raise ConfluenceError(f"'{title}' came back empty, so there is nothing to judge")

    return Subject(kind=PAGE, label=title, body=body, source_url=url)
