"""The only layer that holds a Slack token.

Everything that talks to Slack lives here: fetching a thread, resolving
names, adding the acknowledging reaction, and posting the answer. The model
layer in `runner` is never handed one of these objects and never sees the
token, which is what makes "the bot posts, the model does not" a property of
the code rather than a promise in a README.

The client is injected rather than constructed, so the tests exercise this
file against a stand-in and the real Slack SDK is imported only by
`connect`.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Sequence

log = logging.getLogger(__name__)

# conversations.replies pages at 1000. Ten pages is far more thread than
# anyone summarises, and the cap stops a pathological thread from pinning
# the process on one command.
MAX_PAGES = 10
PAGE_SIZE = 200


class SlackError(Exception):
    """A Slack call failed in a way the user should be told about."""


class SlackIO:
    """A small, explicit surface over the Slack Web API."""

    def __init__(self, client: Any) -> None:
        self._client = client
        self._user_cache: dict[str, str] = {}
        self._channel_cache: dict[str, str] = {}
        self._bot_user_id: str | None = None

    # -- reading -------------------------------------------------------

    def bot_user_id(self) -> str:
        """This bot's own user id, looked up once.

        `auth.test` needs no scope beyond the token itself. An empty string
        when it fails: the only caller uses this to drop the bot's own
        messages out of a transcript, and a thread carrying one extra message
        is a far smaller problem than a command that will not run.
        """
        if self._bot_user_id is None:
            try:
                self._bot_user_id = str(self._call("auth_test").get("user_id") or "")
            except SlackError as exc:
                log.info("could not resolve the bot's own user id: %s", exc)
                self._bot_user_id = ""
        return self._bot_user_id

    def fetch_thread(self, channel_id: str, thread_ts: str) -> list[dict[str, Any]]:
        """Every message in one thread, parent first."""
        messages: list[dict[str, Any]] = []
        cursor: str | None = None

        for _ in range(MAX_PAGES):
            kwargs: dict[str, Any] = {
                "channel": channel_id,
                "ts": thread_ts,
                "limit": PAGE_SIZE,
            }
            if cursor:
                kwargs["cursor"] = cursor
            response = self._call("conversations_replies", **kwargs)
            messages.extend(response.get("messages") or [])
            if not response.get("has_more"):
                break
            cursor = (response.get("response_metadata") or {}).get("next_cursor")
            if not cursor:
                break

        return messages

    def fetch_message(self, channel_id: str, ts: str) -> dict[str, Any] | None:
        """The single message at `ts`, wherever it sits in a thread.

        `conversations.history` only returns top-level channel messages --
        handed a reply's `ts`, Slack does not error, it silently returns the
        nearest channel-level message instead. `conversations.replies`
        accepts either a thread's parent `ts` or any reply's `ts` within it,
        so it is tried first; a `ts` that belongs to no thread raises
        `thread_not_found`, which falls back to `conversations.history` for
        the plain channel-message case. Either way, the returned message's
        own `ts` is checked against the one requested before it is trusted --
        a mismatch is treated as not found rather than silently returned,
        since a wrong message read here decides both the re-fire guard and
        which thread the answer is posted into.
        """
        try:
            response = self._call(
                "conversations_replies", channel=channel_id, ts=ts, limit=PAGE_SIZE
            )
        except SlackError:
            response = None
        if response is not None:
            for message in response.get("messages") or []:
                if message.get("ts") == ts:
                    return message

        response = self._call(
            "conversations_history", channel=channel_id, latest=ts, inclusive=True, limit=1
        )
        messages = response.get("messages") or []
        message = messages[0] if messages else None
        return message if message is not None and message.get("ts") == ts else None

    def has_reaction(self, message: Mapping[str, Any], name: str) -> bool:
        """Has this bot already reacted to `message` with `name`?"""
        own = self.bot_user_id()
        if not own:
            return False
        for reaction in message.get("reactions") or []:
            if reaction.get("name") == name and own in (reaction.get("users") or []):
                return True
        return False

    def channel_label(self, channel_id: str) -> str:
        """``#name`` when the bot can see the channel, the raw id otherwise."""
        if channel_id in self._channel_cache:
            return self._channel_cache[channel_id]
        label = channel_id
        try:
            info = self._call("conversations_info", channel=channel_id)
            name = ((info.get("channel") or {}).get("name") or "").strip()
            if name:
                label = f"#{name}"
        except SlackError as exc:
            # A DM, or a channel the bot has no read scope for. The id is a
            # perfectly good label and this is not worth failing a command.
            log.info("could not name channel %s: %s", channel_id, exc)
        self._channel_cache[channel_id] = label
        return label

    def user_names(self, user_ids: Iterable[str]) -> dict[str, str]:
        """Display names for the people in a thread, looked up once each."""
        for user_id in {uid for uid in user_ids if uid}:
            if user_id in self._user_cache:
                continue
            try:
                info = self._call("users_info", user=user_id)
            except SlackError as exc:
                log.info("could not name user %s: %s", user_id, exc)
                self._user_cache[user_id] = user_id
                continue
            profile = (info.get("user") or {}).get("profile") or {}
            user = info.get("user") or {}
            self._user_cache[user_id] = (
                profile.get("display_name")
                or profile.get("real_name")
                or user.get("name")
                or user_id
            )
        return dict(self._user_cache)

    # -- writing -------------------------------------------------------

    def post(self, channel_id: str, thread_ts: str, text: str) -> None:
        """Post one message, always inside the thread it answers."""
        self._call(
            "chat_postMessage",
            channel=channel_id,
            thread_ts=thread_ts,
            text=text,
            unfurl_links=False,
            unfurl_media=False,
        )

    def post_direct(self, user_id: str, text: str) -> str:
        """Post one top-level message to a person's DM with this bot.

        `chat.postMessage` opens the conversation itself when `channel` is a
        user id, so this needs no `conversations.open` call and no scope
        beyond the `chat:write` the bot already has for everything else.

        Unlike `post` there is no `thread_ts`: a digest is its own message,
        not a reply to one. It raises rather than swallowing a failure --
        a digest nobody received must not look like a digest that was sent.
        """
        response = self._call(
            "chat_postMessage",
            channel=user_id,
            text=text,
            unfurl_links=False,
            unfurl_media=False,
        )
        return str(response.get("ts") or "")

    def post_ephemeral(
        self,
        channel_id: str,
        user_id: str,
        text: str,
        thread_ts: str | None = None,
    ) -> bool:
        """Post a message only one person can see. Never fails a command.

        `chat.postEphemeral` needs no scope beyond `chat:write`, notifies
        nobody, and leaves nothing behind in the channel -- which is what
        makes it safe to answer a stranger at all.
        """
        kwargs: dict[str, Any] = {"channel": channel_id, "user": user_id, "text": text}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        try:
            self._call("chat_postEphemeral", **kwargs)
            return True
        except SlackError as exc:
            log.info("could not post an ephemeral message to %s: %s", user_id, exc)
            return False

    def delete(self, channel_id: str, timestamp: str) -> None:
        """Remove one message this bot posted.

        A bot token may delete only what that same token posted, so this can
        never take somebody else's message down however it is called. It
        raises rather than swallowing a failure: the person asked for a
        message to go, and silence would leave them believing it had.
        """
        self._call("chat_delete", channel=channel_id, ts=timestamp)

    def add_reaction(self, channel_id: str, timestamp: str, name: str) -> bool:
        """Best-effort acknowledgement. Never fails a command.

        Warning, not info: for the reaction trigger this doubles as the
        re-fire guard's memory (`handler.py`), so a failure here can mean
        the same trigger answers twice.
        """
        try:
            self._call("reactions_add", channel=channel_id, timestamp=timestamp, name=name)
            return True
        except SlackError as exc:
            log.warning("could not add the %s reaction: %s", name, exc)
            return False

    # -- plumbing ------------------------------------------------------

    def _call(self, method: str, **kwargs: Any) -> Mapping[str, Any]:
        try:
            response = getattr(self._client, method)(**kwargs)
        except AttributeError as exc:  # pragma: no cover - programming error
            raise SlackError(f"the Slack client has no {method}") from exc
        except Exception as exc:  # slack_sdk raises SlackApiError
            raise SlackError(f"{method} failed: {_reason(exc)}") from exc
        if isinstance(response, Mapping) and response.get("ok") is False:
            raise SlackError(f"{method} failed: {response.get('error', 'unknown error')}")
        return response


def _reason(exc: Exception) -> str:
    """Pull Slack's own error string out of a SlackApiError if it is one."""
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            error = response["error"]
        except Exception:  # noqa: BLE001 - any shape but the expected one
            error = None
        if error:
            return str(error)
    return str(exc)


def thread_participants(messages: Sequence[Mapping[str, Any]]) -> set[str]:
    """Every user id that said something, for one batch of name lookups."""
    return {str(m["user"]) for m in messages if m.get("user")}


def connect(bot_token: str) -> SlackIO:
    """Build a `SlackIO` over the real Slack SDK."""
    from slack_sdk import WebClient  # imported here so the tests need no SDK

    return SlackIO(WebClient(token=bot_token))
