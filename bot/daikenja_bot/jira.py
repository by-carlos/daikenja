"""Optional: fetch a Jira issue, comments included, as a subject.

It rides on the `confluence` block in `bot.yaml`. On Atlassian Cloud both
products live on one host and accept one API token, so a second block would
only be the same three values written twice. Without the block, a Jira link
is answered the same way an unconfigured Confluence link is.

REST API v2 rather than v3: v2 hands back the description and comments as
wiki-markup text, which the model reads as it is, where v3's Atlassian
Document Format would need a flattener of its own. Standard library only,
for the same reason as `confluence.py`.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from .config import ConfluenceConfig
from .confluence import ConfluenceError, ConfluenceNotConfigured, _auth_header
from .links import parse_jira_key
from .subject import ISSUE, Subject

log = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
ISSUE_FIELDS = "summary,status,issuetype,assignee,reporter,description"
# One page of comments, newest first, so a long ticket loses its oldest
# discussion rather than its latest decision.
COMMENT_PAGE = 100

Fetch = Callable[..., bytes]


class JiraError(ConfluenceError):
    """The issue could not be fetched. The same shape as a page failure, so
    everything that reports one reports the other."""


class JiraNotConfigured(ConfluenceNotConfigured):
    """There is no `confluence` block, which is what turns Jira on too."""

    def __init__(self) -> None:
        super().__init__(
            "Jira links are not configured on this bot. They use the "
            "`confluence` block in bot.yaml -- add one to turn on both."
        )
        self.reason = "Jira not configured"


def _default_fetch(
    url: str, headers: dict[str, str], timeout: float = REQUEST_TIMEOUT
) -> bytes:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise JiraError(
                "Jira rejected the credentials in bot.yaml",
                reason=f"HTTP {exc.code}, credentials rejected",
            ) from exc
        if exc.code == 404:
            raise JiraError(
                "that issue does not exist, or this Jira account cannot see it",
                reason="not found or not visible",
            ) from exc
        raise JiraError(
            f"Jira returned HTTP {exc.code}", reason=f"HTTP {exc.code}"
        ) from exc
    except TimeoutError as exc:
        raise JiraError("Jira did not answer in time", reason="timed out") from exc
    except urllib.error.URLError as exc:
        raise JiraError(
            f"could not reach Jira: {exc.reason}", reason="unreachable"
        ) from exc


def fetcher(timeout: float) -> Fetch:
    """The default HTTP call with a different per-request timeout."""

    def fetch(url: str, headers: dict[str, str]) -> bytes:
        return _default_fetch(url, headers, timeout)

    return fetch


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
        raise JiraError(
            "Jira returned something that is not JSON", reason="not JSON"
        ) from exc


def _name(person: Any, missing: str) -> str:
    if isinstance(person, dict):
        return str(person.get("displayName") or person.get("name") or missing)
    return missing


def _field_name(value: Any) -> str:
    return str(value.get("name") or "") if isinstance(value, dict) else ""


def render_issue(
    key: str,
    fields: dict[str, Any],
    comments: list[dict[str, Any]],
    limit: int | None = None,
) -> str:
    """The issue as text: a header, the description, then comments oldest
    to newest.

    Over ``limit``, whole comments go from the oldest end first, and the body
    says how many went; the description is cut only when it alone does not
    fit, and then no comment is kept.
    """
    kind = _field_name(fields.get("issuetype")) or "Issue"
    status = _field_name(fields.get("status")) or "no status"
    header = "\n".join(
        [
            f"{key} ({kind}, {status})",
            f"Assignee: {_name(fields.get('assignee'), 'unassigned')}",
            f"Reporter: {_name(fields.get('reporter'), 'unknown')}",
        ]
    )
    description = str(fields.get("description") or "").strip() or "(none)"
    head = f"{header}\n\nDescription:\n{description}"

    blocks = [
        f"[{str(c.get('created') or '')[:10]}] "
        f"{_name(c.get('author'), 'someone')}:\n{str(c.get('body') or '').strip()}"
        for c in comments
    ]
    total = len(blocks)

    def assemble(kept: list[str], dropped: int) -> str:
        if not total:
            return head
        out = f"{head}\n\nComments ({total}):"
        if dropped:
            out += f"\n[{dropped} older comment{'s' if dropped != 1 else ''} dropped]"
        if kept:
            out += "\n\n" + "\n\n".join(kept)
        return out

    if limit is not None and len(head) > limit:
        # The description alone is over: keep its start, drop every comment.
        marker = f"\n[truncated at {limit} characters]"
        head = head[: max(limit - len(marker), 0)].rstrip() + marker
        return assemble([], total)

    kept = blocks
    while limit is not None and kept and len(assemble(kept, total - len(kept))) > limit:
        kept = kept[1:]
    return assemble(kept, total - len(kept))


def fetch_issue(
    config: ConfluenceConfig | None,
    url: str,
    token: str | None,
    fetch: Fetch = _default_fetch,
    limit: int | None = None,
) -> Subject:
    """Fetch one issue and its comments as a subject."""
    if config is None:
        raise JiraNotConfigured()
    if not token:
        raise JiraError(
            "no Atlassian token is set. Export the variable named by "
            "confluence.token_env before starting the bot.",
            reason="no Atlassian token",
        )
    key = parse_jira_key(url)
    if not key:
        raise JiraError(
            "that Jira link names no issue key", reason="no issue key in link"
        )

    quoted = urllib.parse.quote(key)
    issue = _get_json(
        fetch,
        f"{config.base_url}/rest/api/2/issue/{quoted}?fields={ISSUE_FIELDS}",
        config,
        token,
    )
    fields = issue.get("fields") if isinstance(issue, dict) else None
    if not isinstance(fields, dict):
        raise JiraError("Jira returned something that is not an issue", reason="not an issue")

    page = _get_json(
        fetch,
        f"{config.base_url}/rest/api/2/issue/{quoted}/comment"
        f"?orderBy=-created&maxResults={COMMENT_PAGE}",
        config,
        token,
    )
    newest_first = page.get("comments") if isinstance(page, dict) else None
    comments = [c for c in (newest_first or []) if isinstance(c, dict)]
    comments.reverse()

    summary = str(fields.get("summary") or "").strip()
    return Subject(
        kind=ISSUE,
        label=f"{key}: {summary}" if summary else key,
        body=render_issue(key, fields, comments, limit),
        source_url=url,
    )
