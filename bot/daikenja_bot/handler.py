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

from .commands import (
    DELETE,
    HELP,
    JUDGEMENT,
    SUMMARY,
    USAGE,
    Command,
    parse_command,
)
from .config import BotConfig, ConfigError
from .confluence import ConfluenceError, ConfluenceNotConfigured
from .follow import follow
from .mrkdwn import to_mrkdwn, truncate
from .resolve import Resolved, Resolver
from .runner import RunnerError, run_command
from .slack_io import SlackError, SlackIO
from .subject import Subject

log = logging.getLogger(__name__)

UNKNOWN_LINK = (
    "I did not recognise that link. I can read a Slack message permalink, a "
    "Confluence page URL or a Jira issue URL."
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


@dataclass(frozen=True)
class ReactionEvent:
    """The parts of a ``reaction_added`` event this bot uses."""

    user_id: str
    channel_id: str
    message_ts: str
    reaction: str

    @classmethod
    def from_event(cls, event: Mapping[str, Any]) -> "ReactionEvent":
        item = event.get("item") or {}
        return cls(
            user_id=str(event.get("user") or ""),
            channel_id=str(item.get("channel") or ""),
            message_ts=str(item.get("ts") or ""),
            reaction=str(event.get("reaction") or ""),
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
        fetch_confluence: Any = None,
        fetch_jira: Any = None,
        resolver: Resolver | None = None,
        unavailable: Mapping[str, str] | None = None,
    ) -> None:
        self._config = config
        self._slack = slack
        self._environ = environ
        self._run = run
        # `fetch_confluence` and `fetch_jira` are the shortcuts the tests use
        # to stand in for one fetch; a whole `resolver` replaces every source.
        self._resolver = resolver or Resolver(
            config,
            slack,
            environ,
            fetch_confluence=fetch_confluence,
            fetch_jira=fetch_jira,
        )
        # Command name -> why it cannot run, from the startup skill check.
        self._unavailable = dict(unavailable or {})
        # Re-fire guard's own memory, backing the Slack ack reaction rather
        # than replacing it: (channel, ts) pairs answered this process's
        # lifetime, so a failed `add_reaction` write -- the message it was
        # meant to mark got deleted mid-answer, a scope issue, a network
        # blip -- does not leave the guard blind to the same trigger firing
        # again. Reset on restart, same as the rest of this instance's state.
        self._answered_reactions: set[tuple[str, str]] = set()

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
            resolved = self._resolve_subject(command, mention)
        except ConfluenceNotConfigured as exc:
            self._reply(mention, str(exc))
            return
        except (ConfluenceError, SlackError) as exc:
            self._reply(mention, f"I could not read that: {exc}")
            return
        except ConfigError as exc:
            self._reply(mention, f"I could not read that: {exc}")
            return

        if resolved is None:
            self._reply(mention, UNKNOWN_LINK)
            return

        # What the subject links to is read here, before the session starts.
        # Nothing about it can stop the run: a link that fails is noted for
        # the model and surfaces only through the answer.
        subject = follow(
            resolved.subject,
            command.extra,
            self._resolver,
            resolved.links,
            space_key=resolved.space_key,
        )

        try:
            answer = self._run(
                self._config,
                command.name,
                subject,
                environ=self._environ,
                project=command.project,
            )
        except RunnerError as exc:
            log.warning("%s failed: %s", command.name, exc)
            self._reply(mention, f"That did not work: {exc}")
            return

        self._reply(mention, answer, source=subject)

    def handle_reaction(self, event: Mapping[str, Any]) -> None:
        """The quiet path in: a reaction instead of a typed command.

        Nobody addressed the bot, so there is no ephemeral reply on any exit
        here -- a stranger's reaction, a wrong channel, or an emoji that is
        not the configured trigger all do nothing at all, silently.
        """
        reaction = ReactionEvent.from_event(event)
        trigger = self._config.slack.reaction_trigger
        if not trigger or reaction.reaction != trigger:
            return
        if not reaction.channel_id or not reaction.message_ts:
            log.warning("ignoring a reaction with no channel or timestamp")
            return

        if not self._config.slack.may_trigger(reaction.user_id, reaction.channel_id):
            log.info(
                "ignoring a :%s: reaction from %s in %s -- not on the allowlist",
                trigger,
                reaction.user_id,
                reaction.channel_id,
            )
            return

        try:
            message = self._slack.fetch_message(reaction.channel_id, reaction.message_ts)
        except SlackError as exc:
            log.warning("could not read the reacted message: %s", exc)
            return
        if message is None:
            log.warning("the reacted message could not be found")
            return

        ack = self._config.slack.ack_reaction
        answered_key = (reaction.channel_id, reaction.message_ts)
        if ack and (
            answered_key in self._answered_reactions
            or self._slack.has_reaction(message, ack)
        ):
            # Re-fire guard: removing and re-adding the trigger, or a second
            # person adding it, fires this event again for the same message.
            # The bot's own ack on it is treated as "already answered" --
            # backed by `_answered_reactions` for the case where that ack
            # write itself failed and so never landed on the message.
            log.info("already answered %s -- skipping", reaction.message_ts)
            return

        for command_name in (SUMMARY, JUDGEMENT):
            unavailable = self._unavailable.get(command_name)
            if unavailable:
                log.warning(
                    "cannot answer a reaction: %s is unavailable (%s)",
                    command_name,
                    unavailable,
                )
                return

        thread_ts = str(message.get("thread_ts") or reaction.message_ts)
        try:
            resolved = self._resolver.thread(
                reaction.channel_id, thread_ts, follow_forward=True
            )
        except SlackError as exc:
            log.warning("could not read the reacted thread: %s", exc)
            return
        subject = follow(resolved.subject, (), self._resolver, resolved.links)

        answers: list[str] = []
        for command_name in (SUMMARY, JUDGEMENT):
            try:
                answers.append(
                    self._run(self._config, command_name, subject, environ=self._environ)
                )
            except RunnerError as exc:
                log.warning("%s failed on a reaction trigger: %s", command_name, exc)
                return

        # No divider line between the two: `to_mrkdwn` drops a bare `---` as
        # a markdown rule, and each block already opens with its own label
        # (`Thread:` / `Verdict:`), so nothing is lost without one.
        body = to_mrkdwn("\n\n".join(answers))
        try:
            self._slack.post(reaction.channel_id, thread_ts, truncate(body))
        except SlackError as exc:
            log.error("could not post into %s: %s", reaction.channel_id, exc)
            return

        if ack:
            # Recorded regardless of whether the write below succeeds: the
            # answer has already been posted, and the point of this record
            # is precisely to keep the guard working when that write fails.
            self._answered_reactions.add(answered_key)
            self._slack.add_reaction(reaction.channel_id, reaction.message_ts, ack)

    # -- subjects ------------------------------------------------------

    def _resolve_subject(
        self, command: Command, mention: MentionEvent
    ) -> Resolved | None:
        if not command.argument:
            return self._resolver.thread(
                mention.channel_id, mention.thread_ts, follow_forward=True
            )
        # A link the user typed is what they asked for, whatever the thread
        # around it holds, so a permalink is not forward-followed.
        return self._resolver.resolve(command.argument)

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
            linked = len(source.attachments)
            also = f" + {linked} linked" if linked else ""
            body = f"_On_ <{source.source_url}>{also}\n\n{body}"
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
