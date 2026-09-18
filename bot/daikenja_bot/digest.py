"""The digest: a list a feeder collected, grouped and posted once.

The bot's other path is reactive -- somebody mentions it, it answers in the
thread. This one is pushed: a scheduled job hands over the messages it thinks
are worth reading, and the digest says which project each belongs to and what
that project still has open.

Three things are deliberate.

**Nothing here collects anything.** The feeder decides what is worth
digesting, and how it decided is its own business -- this module reads no
mailbox, opens no channel, and never looks at a `bucket` value to rank
anything. That is what makes the layer usable by a feeder it was not written
for.

**The grouping is not done here.** Placing an item against a project means
reading project cards and ledgers, which the skills own; `bot/` is transport.
So this module validates the list, formats it, and hands it to the same
headless session that answers a mention. A second copy of the card and ledger
grammar living in Python would be a second copy to keep true.

**It is outbound only.** The digest needs the bot token and nothing else: the
app-level token exists for Socket Mode, which is how events are *received*.
So a digest run never opens a socket and works fine on a machine where
`SLACK_APP_TOKEN` was never set.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .config import BotConfig
from .mrkdwn import to_mrkdwn, truncate
from .prompts import DIGEST
from .runner import CommandRunner, run_command
from .slack_io import SlackIO
from .subject import ITEMS, Subject

log = logging.getLogger(__name__)

# The item fields, in the order they are written into the block, paired with
# the label the skill reads them under. The labels are shorter and plainer
# than the JSON names on purpose: the block is prose a model reads, not a
# wire format, and `when` beats `ts` there.
FIELDS: tuple[tuple[str, str], ...] = (
    ("ts", "when"),
    ("channel", "channel"),
    ("sender", "from"),
    ("bucket", "bucket"),
    ("topic", "topic"),
    ("permalink", "link"),
    ("summary", "summary"),
)

# What a feeder may call each field instead. `project` for `topic` is in the
# issue that asked for this layer; the rest are the block's own labels, so a
# list dumped out of a block round-trips back in.
ALIASES: dict[str, str] = {
    "when": "ts",
    "timestamp": "ts",
    "from": "sender",
    "user": "sender",
    "link": "permalink",
    "url": "permalink",
    "project": "topic",
    "text": "summary",
}

ITEM_BEGIN = "--- ITEM {n} ---"


class DigestError(Exception):
    """The item list could not be read, or there was nothing in it."""


@dataclass(frozen=True)
class ItemList:
    """The items worth digesting, plus a line about each one dropped."""

    items: tuple[dict[str, str], ...]
    skipped: tuple[str, ...] = ()

    def __len__(self) -> int:
        return len(self.items)


def parse_items(raw: str) -> ItemList:
    """Read the feeder's JSON into items, or say exactly what is wrong.

    A structural problem raises: a list that does not parse, or an entry that
    is not an object, means the feeder is broken and digesting whatever
    survived would hide that. A *missing summary* only drops that one item --
    an item with nothing to say is not an item, and one of them is no reason
    to lose the other eleven.
    """
    text = (raw or "").strip()
    if not text:
        raise DigestError("there were no items on standard input")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DigestError(
            f"the item list is not valid JSON: {exc.msg} at line {exc.lineno}, "
            f"column {exc.colno}"
        ) from exc

    if isinstance(data, Mapping):
        data = data.get("items")
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        raise DigestError(
            "the item list must be a JSON array of objects, or an object with "
            "an `items` array"
        )

    items: list[dict[str, str]] = []
    skipped: list[str] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, Mapping):
            raise DigestError(f"item {position} is not an object: {entry!r}")
        item = _read_item(entry, position)
        if not item.get("summary"):
            skipped.append(f"Item {position} has no summary. Skipped.")
            continue
        items.append(item)

    if not items:
        raise DigestError("there were no items to digest")
    return ItemList(items=tuple(items), skipped=tuple(skipped))


def _read_item(entry: Mapping[str, Any], position: int) -> dict[str, str]:
    """One item, keyed by canonical field name, with unknown keys dropped.

    An unknown key is a feeder's own business -- a score, a message id, its
    own classification -- and is discarded rather than refused, so a feeder
    can hand over the records it already has instead of building a second
    shape for this.
    """
    known = {name for name, _ in FIELDS}
    item: dict[str, str] = {}
    for key, value in entry.items():
        name = ALIASES.get(str(key).strip().lower(), str(key).strip().lower())
        if name not in known or value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise DigestError(
                f"item {position}: {key} must be text, got {value!r}"
            )
        text = str(value).strip()
        if text:
            item[name] = text
    return item


def render_items(item_list: ItemList) -> str:
    """The labelled block the skill reads, one paragraph per item."""
    blocks: list[str] = []
    for position, item in enumerate(item_list.items, start=1):
        lines = [ITEM_BEGIN.format(n=position)]
        lines += [
            f"{label}: {item[name]}" for name, label in FIELDS if item.get(name)
        ]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def build_subject(item_list: ItemList) -> Subject:
    """The items, in the shape `runner.run_command` expects."""
    count = len(item_list)
    return Subject(
        kind=ITEMS,
        label=f"{count} item{'' if count == 1 else 's'} collected by a feeder",
        body=render_items(item_list),
    )


def build_digest(
    config: BotConfig,
    item_list: ItemList,
    *,
    environ: Mapping[str, str],
    runner: CommandRunner | None = None,
) -> str:
    """Run the headless session and return the digest. Posts nothing."""
    return run_command(
        config,
        DIGEST,
        build_subject(item_list),
        environ=environ,
        runner=runner,
    )


def post_digest(slack: SlackIO, config: BotConfig, text: str) -> str:
    """Post the digest to the owner's DM, converted and cut to fit."""
    body = truncate(to_mrkdwn(text))
    timestamp = slack.post_direct(config.slack.owner_user_id, body)
    log.info("posted the digest to %s", config.slack.owner_user_id)
    return timestamp
