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

from .commands import DELETE, HELP, USAGE, Command, parse_command
from .config import BotConfig, ConfigError, resolve_secret
from .confluence import ConfluenceError, ConfluenceNotConfigured, fetch_page
from .links import forwarded_permalink, looks_like_confluence, parse_slack_permalink
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

# What `slack.unauthorized_message` writes to mean "the owner, by name".
OWNER_PLACEHOLDER = "{owner}"

WRONG_CHANNEL = (
    "I am not switched on in this channel. `slack.allowed_channels` in "
    "`bot.yaml` decides where I answer."
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
            log.info(
                "ignoring a mention from %s in %s -- not on the allowlist",
                mention.user_id,
                mention.channel_id,
            )
            self._decline(mention)
            return

        command = parse_command(mention.text)
        if command.name == HELP:
            if command.unknown_word:
                self._reply(mention, f"I do not know `{command.unknown_word}`. {USAGE}")
            else:
                self._reply(mention, USAGE)
            return

        if command.name == DELETE:
            # Answered out of Slack alone: no subject, no skill, no session,
            # and no acknowledging reaction -- there is nothing to wait for.
            self._delete_last_answer(mention)
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
            return self._thread_subject(
                mention.channel_id, mention.thread_ts, follow_forward=True
            )

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
        self,
        channel_id: str,
        thread_ts: str,
        source_url: str | None = None,
        follow_forward: bool = False,
    ) -> Subject:
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
                return self._thread_subject(
                    ref.channel_id, ref.thread_ts, source_url=forwarded
                )

        messages = self._without_own_messages(messages)
        if not messages:
            raise SlackError("that thread came back empty")
        users = self._slack.user_names(thread_participants(messages))
        return render_thread(
            messages,
            users=users,
            channel_label=self._slack.channel_label(channel_id),
            source_url=source_url,
        )

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

    # -- deleting ------------------------------------------------------

    def _delete_last_answer(self, mention: MentionEvent) -> None:
        """Take down the most recent message this bot posted in the thread.

        Every outcome is reported back to the person who asked and to nobody
        else. A confirmation posted into the thread would replace the message
        just removed with another one, which is the opposite of what was
        asked for.
        """
        own = self._slack.bot_user_id()
        if not own:
            self._tell_only(
                mention,
                "I could not work out which messages are mine, so I have "
                "deleted nothing.",
            )
            return

        try:
            messages = self._slack.fetch_thread(mention.channel_id, mention.thread_ts)
        except SlackError as exc:
            self._tell_only(mention, f"I could not read this thread: {exc}")
            return

        mine = [
            m
            for m in messages
            if str(m.get("user") or "") == own and m.get("ts")
        ]
        if not mine:
            self._tell_only(mention, "I have not posted anything in this thread.")
            return

        timestamp = str(mine[-1]["ts"])
        try:
            self._slack.delete(mention.channel_id, timestamp)
        except SlackError as exc:
            log.warning("could not delete %s in %s: %s", timestamp, mention.channel_id, exc)
            self._tell_only(mention, f"I could not delete that: {exc}")
            return

        remaining = len(mine) - 1
        text = "Deleted my last post here."
        if remaining:
            text += (
                f" {remaining} earlier "
                f"{'post of mine is' if remaining == 1 else 'posts of mine are'} "
                "still in this thread -- say `delete` again for the next one."
            )
        self._tell_only(mention, text)

    # -- posting -------------------------------------------------------

    def _tell_only(self, mention: MentionEvent, text: str) -> None:
        """Say something to the person who asked, and leave nothing behind."""
        self._slack.post_ephemeral(
            mention.channel_id,
            mention.user_id,
            to_mrkdwn(text),
            thread_ts=_ephemeral_thread_ts(mention),
        )

    def _decline(self, mention: MentionEvent) -> None:
        """Tell a stranger why nothing happened -- and tell only them.

        A refusal posted into the thread would turn any passer-by into a way
        to fill it, so this goes out as an ephemeral message: the person who
        mentioned the bot sees it, nobody else does, nothing is notified and
        nothing is left in the channel. `unauthorized_message: null` in the
        config restores the wholly silent behaviour.
        """
        slack = self._config.slack
        if slack.allows_user(mention.user_id):
            # The person is allowed; the channel is not. Telling them they
            # are not on the allowlist would be simply untrue, and this one
            # is not configurable because only the owner ever sees it.
            text = WRONG_CHANNEL
        else:
            text = slack.unauthorized_message or ""
        if not text:
            return
        # Substituted after the conversion, never before: `to_mrkdwn` escapes
        # `<` and `>`, so a mention inserted first would arrive as literal
        # text rather than as the owner's name.
        body = to_mrkdwn(text).replace(
            OWNER_PLACEHOLDER, f"<@{slack.owner_user_id}>"
        )
        self._slack.post_ephemeral(
            mention.channel_id,
            mention.user_id,
            body,
            thread_ts=_ephemeral_thread_ts(mention),
        )

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


def _ephemeral_thread_ts(mention: MentionEvent) -> str | None:
    """Where an ephemeral message for this mention should go.

    Slack renders a threaded ephemeral message only when the thread already
    exists. A mention that was itself a top-level message has no replies yet,
    so that one goes to the channel view instead -- still visible to one
    person only.
    """
    return mention.thread_ts if mention.thread_ts != mention.message_ts else None
