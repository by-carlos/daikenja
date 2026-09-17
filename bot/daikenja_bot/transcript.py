"""Turn the Slack API's message dicts into a transcript a person could read.

`thread` and `judgement` both work from pasted thread text, so the cleanest
thing to hand the headless session is exactly that: numbered messages, a
name and a timestamp on each, and the user IDs inside the text resolved to
names so attribution does not depend on the model recognising ``<@U04…>``.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .subject import THREAD, Subject

USER_MENTION_RE = re.compile(r"<@([UWB][A-Z0-9]+)(?:\|([^>]*))?>")
CHANNEL_MENTION_RE = re.compile(r"<#(C[A-Z0-9]+)(?:\|([^>]*))?>")
LINK_RE = re.compile(r"<(https?://[^>|]+)(?:\|([^>]*))?>")

# Joins, leaves and topic changes are noise in a thread summary and there is
# no finding to be made from them.
SKIPPED_SUBTYPES = frozenset(
    {
        "channel_join",
        "channel_leave",
        "group_join",
        "group_leave",
        "channel_topic",
        "channel_purpose",
        "channel_name",
    }
)


def format_timestamp(ts: str | float) -> str:
    """Render a Slack timestamp as UTC, or hand back what came in."""
    try:
        moment = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    except (TypeError, ValueError):
        return str(ts)
    return moment.strftime("%Y-%m-%d %H:%M UTC")


def speaker_name(message: Mapping[str, Any], users: Mapping[str, str]) -> str:
    """Who sent this message, preferring a real name over an ID."""
    user_id = message.get("user")
    if user_id and users.get(user_id):
        return users[user_id]
    if message.get("username"):
        return str(message["username"])
    if message.get("bot_id"):
        return f"bot {message['bot_id']}"
    return str(user_id or "unknown")


def resolve_mentions(text: str, users: Mapping[str, str]) -> str:
    """Replace Slack's ID markup with names, and unwrap links to plain URLs."""

    def user(match: re.Match[str]) -> str:
        user_id, label = match.group(1), match.group(2)
        return f"@{users.get(user_id) or label or user_id}"

    def channel(match: re.Match[str]) -> str:
        return f"#{match.group(2) or match.group(1)}"

    def link(match: re.Match[str]) -> str:
        url, label = match.group(1), match.group(2)
        return f"{label} ({url})" if label and label != url else url

    text = USER_MENTION_RE.sub(user, text or "")
    text = CHANNEL_MENTION_RE.sub(channel, text)
    return LINK_RE.sub(link, text)


def _attachment_lines(message: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for file in message.get("files") or []:
        name = file.get("name") or file.get("title") or "unnamed file"
        lines.append(f"    [attachment: {name} -- not read]")
    for attachment in message.get("attachments") or []:
        text = (attachment.get("text") or attachment.get("fallback") or "").strip()
        if text:
            lines.append(f"    [attachment] {text}")
    return lines


def render_thread(
    messages: Iterable[Mapping[str, Any]],
    users: Mapping[str, str] | None = None,
    channel_label: str = "a Slack channel",
    source_url: str | None = None,
) -> Subject:
    """Render a fetched thread as a numbered transcript."""
    users = users or {}
    lines: list[str] = []
    counted = 0

    for message in messages:
        if message.get("subtype") in SKIPPED_SUBTYPES:
            continue
        counted += 1
        body = resolve_mentions(str(message.get("text") or "").strip(), users)
        header = (
            f"[{counted}] {speaker_name(message, users)} "
            f"({format_timestamp(message.get('ts', ''))}):"
        )
        if body:
            lines.append(f"{header} {body}")
        else:
            lines.append(f"{header} (no text)")
        lines.extend(_attachment_lines(message))

    plural = "message" if counted == 1 else "messages"
    label = f"{channel_label}, {counted} {plural}"
    return Subject(kind=THREAD, label=label, body="\n".join(lines), source_url=source_url)
