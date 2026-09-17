"""What happens when someone mentions the bot.

The whole flow lives here and none of it imports Slack's SDK: the transport
in `app` turns a Socket Mode event into a `MentionEvent` and hands it over,
so every branch below -- who may trigger it, which subject gets fetched,
what is posted when something fails -- is exercised by the tests against a
stand-in client.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping

from .commands import HELP, USAGE, Command, parse_command
from .config import BotConfig, ConfigError, resolve_secret
from .confluence import ConfluenceError, ConfluenceNotConfigured, fetch_page
from .links import looks_like_confluence, parse_slack_permalink
from .mrkdwn import to_mrkdwn, truncate
from .runner import RunnerError, run_command
from .slack_io import SlackError, SlackIO, thread_participants
from .subject import Subject
from .transcript import render_thread

log = logging.getLogger(__name__)

UNKNOWN_LINK = (
    "I did not recognise that link. I can read a Slack message permalink or a "
    "Confluence page URL."
)


@dataclass(frozen=True)
class MentionEvent:
    """The parts of an ``app_mention`` event this bot uses."""

    user_id: str
    channel_id: str
    message_ts: str
    thread_ts: str
    text: str

    @classmethod
    def from_event(cls, event: Mapping[str, Any]) -> "MentionEvent":
        message_ts = str(event.get("ts") or "")
        return cls(
            user_id=str(event.get("user") or ""),
            channel_id=str(event.get("channel") or ""),
            message_ts=message_ts,
            # A mention in the channel rather than in a thread still gets a
            # threaded reply: answering in the channel would drop a wall of
            # summary into everyone's view.
            thread_ts=str(event.get("thread_ts") or message_ts),
            text=str(event.get("text") or ""),
        )


class Handler:
    """One bot instance's behaviour, independent of how events arrive."""

    def __init__(
        self,
        config: BotConfig,
        slack: SlackIO,
        *,
        environ: Mapping[str, str],
        run: Any = run_command,
        fetch_confluence: Any = fetch_page,
        unavailable: Mapping[str, str] | None = None,
    ) -> None:
        self._config = config
        self._slack = slack
        self._environ = environ
        self._run = run
        self._fetch_confluence = fetch_confluence
        # Command name -> why it cannot run, from the startup skill check.
        self._unavailable = dict(unavailable or {})

    # -- entry point ---------------------------------------------------

    def handle_mention(self, event: Mapping[str, Any]) -> None:
        mention = MentionEvent.from_event(event)
        if not mention.channel_id or not mention.message_ts:
            log.warning("ignoring a mention with no channel or timestamp")
            return

        if not self._config.slack.may_trigger(mention.user_id, mention.channel_id):
            # Silence rather than a refusal: this bot sits in shared
            # channels, and a reply to everyone who mentions it turns any
            # passer-by into a way to fill the thread.
            log.info(
                "ignoring a mention from %s in %s -- not on the allowlist",
                mention.user_id,
                mention.channel_id,
            )
            return

        command = parse_command(mention.text)
        if command.name == HELP:
            if command.unknown_word:
                self._reply(mention, f"I do not know `{command.unknown_word}`. {USAGE}")
            else:
                self._reply(mention, USAGE)
            return

        unavailable = self._unavailable.get(command.name)
        if unavailable:
            # Said before any work, and before the reaction: there is
            # nothing to wait for and nothing that will make it work.
            self._reply(mention, unavailable)
            return

        self._acknowledge(mention)

        try:
            subject = self._resolve_subject(command, mention)
        except ConfluenceNotConfigured as exc:
            self._reply(mention, str(exc))
            return
        except (ConfluenceError, SlackError) as exc:
            self._reply(mention, f"I could not read that: {exc}")
            return
        except ConfigError as exc:
            self._reply(mention, f"I could not read that: {exc}")
            return

        if subject is None:
            self._reply(mention, UNKNOWN_LINK)
            return

        try:
            answer = self._run(
                self._config, command.name, subject, environ=self._environ
            )
        except RunnerError as exc:
            log.warning("%s failed: %s", command.name, exc)
            self._reply(mention, f"That did not work: {exc}")
            return

        self._reply(mention, answer, source=subject)

    # -- subjects ------------------------------------------------------

    def _resolve_subject(
        self, command: Command, mention: MentionEvent
    ) -> Subject | None:
        if not command.argument:
            return self._thread_subject(mention.channel_id, mention.thread_ts)

        permalink = parse_slack_permalink(command.argument)
        if permalink:
            return self._thread_subject(
                permalink.channel_id,
                permalink.thread_ts,
                source_url=command.argument,
            )

        base_url = (
            self._config.confluence.base_url if self._config.confluence else None
        )
        if looks_like_confluence(command.argument, base_url):
            return self._confluence_subject(command.argument)

        return None

    def _thread_subject(
        self, channel_id: str, thread_ts: str, source_url: str | None = None
    ) -> Subject:
        messages = self._slack.fetch_thread(channel_id, thread_ts)
        if not messages:
            raise SlackError("that thread came back empty")
        users = self._slack.user_names(thread_participants(messages))
        return render_thread(
            messages,
            users=users,
            channel_label=self._slack.channel_label(channel_id),
            source_url=source_url,
        )

    def _confluence_subject(self, url: str) -> Subject:
        confluence = self._config.confluence
        if confluence is None:
            raise ConfluenceNotConfigured(
                "Confluence links are not configured on this bot. Add a "
                "`confluence` block to bot.yaml to turn them on."
            )
        token = resolve_secret(
            label="the Confluence token",
            env_name=confluence.token_env,
            file_path=confluence.token_file,
            inline=confluence.token,
            environ=dict(self._environ),
        )
        return self._fetch_confluence(confluence, url, token)

    # -- posting -------------------------------------------------------

    def _acknowledge(self, mention: MentionEvent) -> None:
        reaction = self._config.slack.ack_reaction
        if not reaction:
            return
        self._slack.add_reaction(mention.channel_id, mention.message_ts, reaction)

    def _reply(
        self, mention: MentionEvent, text: str, source: Subject | None = None
    ) -> None:
        body = to_mrkdwn(text)
        if source is not None and source.source_url:
            # Angle brackets, not a bare URL: a Slack permalink carries
            # `?thread_ts=...&cid=...`, and a bare `&` is markup to Slack's
            # renderer. `<...>` is the documented form for a link, and the
            # post already has unfurling switched off.
            body = f"_On_ <{source.source_url}>\n\n{body}"
        try:
            self._slack.post(mention.channel_id, mention.thread_ts, truncate(body))
        except SlackError as exc:
            # Nothing left to say in the thread, so the log is the only
            # place this can surface.
            log.error("could not post into %s: %s", mention.channel_id, exc)
