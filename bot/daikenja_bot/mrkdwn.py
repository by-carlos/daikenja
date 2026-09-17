"""Convert the plugin's markdown into Slack's mrkdwn.

The two are not the same dialect and the differences are not cosmetic:
Slack has no headings, writes bold with one asterisk rather than two, writes
a link as ``<url|text>``, and reads a bare ``<``, ``>`` or ``&`` as markup
unless it is escaped. Posting raw markdown produces a message full of
literal asterisks and swallowed angle brackets.

Everything here is a pure string transform, so the whole dialect is covered
by unit tests with no Slack workspace in sight.
"""

from __future__ import annotations

import re

# chat.postMessage accepts 40,000 characters in `text`. Leave room for the
# note appended when a message is cut.
MAX_MESSAGE_CHARS = 39_000
TRUNCATION_NOTE = "\n\n_(cut here -- the full answer was longer than Slack allows)_"

FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
RULE_RE = re.compile(r"^\s*(?:[-*_]\s*){3,}$")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\(\s*<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
BARE_ANGLE_URL_RE = re.compile(r"<(https?://[^>\s|]+)>")
BOLD_DOUBLE_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.DOTALL)
BOLD_UNDERSCORE_RE = re.compile(r"__(?=\S)(.+?)(?<=\S)__", re.DOTALL)
ITALIC_SINGLE_RE = re.compile(r"(?<![*\w])\*(?=[^*\s])([^*\n]+?)(?<=[^*\s])\*(?![*\w])")

_PLACEHOLDER = "\x00{}\x00"
_PLACEHOLDER_RE = re.compile(r"\x00(\d+)\x00")


def escape_entities(text: str) -> str:
    """Escape the three characters Slack reads as markup.

    ``&`` goes first, or the ampersands introduced by the other two get
    escaped a second time.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class _Vault:
    """Holds finished fragments so later passes cannot rewrite them."""

    def __init__(self) -> None:
        self._items: list[str] = []

    def store(self, value: str) -> str:
        self._items.append(value)
        return _PLACEHOLDER.format(len(self._items) - 1)

    def restore(self, text: str) -> str:
        return _PLACEHOLDER_RE.sub(lambda m: self._items[int(m.group(1))], text)


def _convert_links(text: str, vault: _Vault) -> str:
    """Rewrite markdown links, and park them beyond the escaping pass.

    The label is escaped here because the escaping pass will not see it
    again; the URL is not, since Slack expects a raw URL inside ``<...>``.
    """

    def replace(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        url = match.group(2).strip()
        if not url:
            return escape_entities(label)
        if label and label != url:
            return vault.store(f"<{url}|{escape_entities(label)}>")
        return vault.store(f"<{url}>")

    text = MD_LINK_RE.sub(replace, text)
    return BARE_ANGLE_URL_RE.sub(lambda m: vault.store(f"<{m.group(1)}>"), text)


def _convert_emphasis(text: str) -> str:
    """Italics first, then bold.

    The order matters and is not obvious: bold becomes a single asterisk in
    mrkdwn, so converting it first leaves output the italic rule would then
    eat. Running italics first is safe because its pattern refuses a run of
    two asterisks at either end.
    """
    text = ITALIC_SINGLE_RE.sub(r"_\1_", text)
    text = BOLD_DOUBLE_RE.sub(r"*\1*", text)
    return BOLD_UNDERSCORE_RE.sub(r"*\1*", text)


def _convert_line(line: str, vault: _Vault) -> str | None:
    """Convert one line of prose. None means drop the line."""
    if RULE_RE.match(line) and line.strip():
        return None

    quote_prefix = ""
    quote = BLOCKQUOTE_RE.match(line)
    if quote:
        quote_prefix = "> "
        line = quote.group(1)

    heading = HEADING_RE.match(line)
    bullet_indent = ""
    if heading:
        line = heading.group(2)
        emphasise_whole_line = bool(line)
    else:
        emphasise_whole_line = False
        bullet = BULLET_RE.match(line)
        if bullet:
            bullet_indent = f"{bullet.group(1)}• "
            line = bullet.group(2)

    line = _convert_links(line, vault)
    line = INLINE_CODE_RE.sub(lambda m: vault.store(f"`{escape_entities(m.group(1))}`"), line)
    line = escape_entities(line)
    line = _convert_emphasis(line)

    if emphasise_whole_line:
        line = f"*{line.strip()}*"

    return f"{quote_prefix}{bullet_indent}{line}"


def to_mrkdwn(text: str) -> str:
    """Convert a markdown document to Slack mrkdwn.

    Fenced code blocks pass through with their content escaped but not
    otherwise touched, so a ledger excerpt or a command keeps its asterisks
    and its indentation.
    """
    if not text:
        return ""

    vault = _Vault()
    out: list[str] = []
    in_fence = False

    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("```")
            continue
        if in_fence:
            out.append(escape_entities(line))
            continue
        converted = _convert_line(line, vault)
        if converted is not None:
            out.append(converted)

    if in_fence:
        # An unbalanced fence would swallow the rest of the message in
        # Slack's renderer. Close it rather than post something unreadable.
        out.append("```")

    return vault.restore("\n".join(out)).strip()


def truncate(text: str, limit: int = MAX_MESSAGE_CHARS) -> str:
    """Cut an over-long message at a line break and say that it was cut."""
    if len(text) <= limit:
        return text
    head = text[: limit - len(TRUNCATION_NOTE)]
    break_at = head.rfind("\n")
    if break_at > limit // 2:
        head = head[:break_at]
    return head.rstrip() + TRUNCATION_NOTE
