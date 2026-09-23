import unittest

from daikenja_bot.commands import USAGE
from daikenja_bot.config import parse_config
from daikenja_bot.confluence import ConfluenceError
from daikenja_bot.handler import UNKNOWN_LINK, Handler, MentionEvent, ReactionEvent
from daikenja_bot.runner import RunnerError
from daikenja_bot.slack_io import SlackIO
from daikenja_bot.subject import ISSUE, PAGE, Subject

from .fakes import FakeSlackClient, load_fixture, make_config

THREAD = load_fixture("sample-thread.json")["messages"]
USERS = {"U0RIMURU": "rimuru", "U0HAKUROU": "hakurou", "U0RIGURD": "rigurd", "U0SHION": "shion"}

PERMALINK = "https://example.slack.com/archives/C0OTHER/p1758067200000100"
PAGE_URL = "https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242/Cutover+plan"


def mention(text: str, user: str = "U0RIMURU", thread_ts: str | None = None) -> dict:
    event = {
        "user": user,
        "channel": "C0HARBOR",
        "ts": "1758069600.000600",
        "text": text,
    }
    if thread_ts:
        event["thread_ts"] = thread_ts
    return event


class Recorder:
    """Stands in for `run_command`, recording what it was asked to do."""

    def __init__(self, answer: str = "Thread: four messages", error: Exception | None = None):
        self.answer = answer
        self.error = error
        self.calls: list[tuple] = []

    def __call__(self, config, command_name, subject, *, environ, project=None):
        self.calls.append((command_name, subject, project))
        if self.error:
            raise self.error
        return self.answer


def build(
    client: FakeSlackClient | None = None,
    run: Recorder | None = None,
    config=None,
    fetch_confluence=None,
):
    client = client or FakeSlackClient(replies=THREAD, users=USERS)
    run = run or Recorder()
    handler = Handler(
        config or make_config(),
        SlackIO(client),
        environ={"PATH": "/bin"},
        run=run,
        fetch_confluence=fetch_confluence or (lambda *a, **k: None),
    )
    return handler, client, run


class MentionEventTests(unittest.TestCase):
    def test_a_channel_mention_replies_in_a_new_thread_under_itself(self):
        event = MentionEvent.from_event(mention("<@U0BOT> summary"))
        self.assertEqual(event.thread_ts, event.message_ts)

    def test_a_thread_mention_keeps_the_thread(self):
        event = MentionEvent.from_event(
            mention("<@U0BOT> summary", thread_ts="1758067200.000100")
        )
        self.assertEqual(event.thread_ts, "1758067200.000100")
        self.assertNotEqual(event.thread_ts, event.message_ts)


class AllowlistTests(unittest.TestCase):
    def test_a_stranger_gets_nothing_in_the_thread_and_no_session(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        self.assertEqual(client.posted, [])
        self.assertEqual(client.reactions, [])
        self.assertEqual(run.calls, [])

    def test_a_stranger_is_told_why_where_only_they_can_see_it(self):
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        self.assertEqual(len(client.ephemeral), 1)
        sent = client.ephemeral[0]
        self.assertEqual(sent["user"], "U0GOBTA")
        self.assertEqual(sent["channel"], "C0HARBOR")
        self.assertIn("personal instance", sent["text"])

    def test_the_owner_placeholder_becomes_a_real_mention(self):
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        # Escaped angle brackets here would mean the substitution ran before
        # the mrkdwn conversion, and the name would post as literal text.
        self.assertIn("<@U0RIMURU>", client.ephemeral[0]["text"])
        self.assertNotIn("{owner}", client.ephemeral[0]["text"])
        self.assertNotIn("&lt;", client.ephemeral[0]["text"])

    def test_a_top_level_mention_gets_the_channel_form(self):
        # Slack only renders a threaded ephemeral message once the thread
        # exists, and a mention that is itself the top message has no replies.
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        self.assertNotIn("thread_ts", client.ephemeral[0])

    def test_a_mention_inside_a_thread_is_answered_in_that_thread(self):
        handler, client, _ = build()
        handler.handle_mention(
            mention("<@U0BOT> summary", user="U0GOBTA", thread_ts="1758067200.000100")
        )
        self.assertEqual(client.ephemeral[0]["thread_ts"], "1758067200.000100")

    def test_a_null_message_restores_the_silent_form(self):
        handler, client, run = build(config=make_config(unauthorized_message=None))
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        self.assertEqual(client.ephemeral, [])
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])

    def test_the_owner_in_the_wrong_channel_is_not_called_a_stranger(self):
        handler, client, run = build(
            config=make_config(allowed_channels=("C0ELSEWHERE",))
        )
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(run.calls, [])
        self.assertIn("not switched on in this channel", client.ephemeral[0]["text"])
        self.assertNotIn("personal instance", client.ephemeral[0]["text"])

    def test_a_failed_ephemeral_reply_is_swallowed(self):
        # The stranger may not be someone Slack will let the bot message.
        # Nothing about that should raise out of the event handler.
        client = FakeSlackClient(
            replies=THREAD, users=USERS, fail={"chat_postEphemeral": "user_not_in_channel"}
        )
        handler, client, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> summary", user="U0GOBTA"))
        self.assertEqual(client.posted, [])

    def test_the_owner_is_served(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(len(client.posted), 1)
        self.assertEqual(run.calls[0][0], "summary")

    def test_a_channel_outside_the_list_is_ignored(self):
        config = parse_config(
            {"slack": {"owner_user_id": "U0RIMURU", "allowed_channels": ["C0ELSEWHERE"]}}
        )
        handler, client, _ = build(config=config)
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(client.posted, [])


class UsageTests(unittest.TestCase):
    def test_a_bare_mention_gets_the_usage_line(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT>"))
        self.assertIn("three commands", client.posted[0]["text"])
        self.assertEqual(run.calls, [])

    def test_an_unknown_word_is_named_back(self):
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT> ledger"))
        self.assertIn("ledger", client.posted[0]["text"])
        self.assertIn(USAGE.split(".")[0][:20], client.posted[0]["text"])

    def test_usage_does_not_add_a_reaction(self):
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT>"))
        self.assertEqual(client.reactions, [])


class ThreadSubjectTests(unittest.TestCase):
    def test_the_invoking_thread_is_read_and_rendered(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> judgement", thread_ts="1758067200.000100"))
        command, subject, _ = run.calls[0]
        self.assertEqual(command, "judgement")
        self.assertEqual(subject.label, "#harbor-rollout, 4 messages")
        self.assertIn("@rigurd you owned the validation step", subject.body)
        self.assertEqual(client.replies_calls[0]["ts"], "1758067200.000100")

    def test_a_permalink_argument_reads_that_thread_instead(self):
        handler, client, run = build()
        handler.handle_mention(mention(f"<@U0BOT> summary {PERMALINK}"))
        self.assertEqual(client.replies_calls[0]["channel"], "C0OTHER")
        self.assertEqual(client.replies_calls[0]["ts"], "1758067200.000100")

    def test_a_linked_subject_is_answered_in_the_invoking_thread(self):
        handler, client, _ = build()
        handler.handle_mention(mention(f"<@U0BOT> summary {PERMALINK}"))
        self.assertEqual(client.posted[0]["channel"], "C0HARBOR")
        self.assertEqual(client.posted[0]["thread_ts"], "1758069600.000600")

    def test_a_linked_subject_names_its_source_above_the_answer(self):
        handler, client, _ = build()
        handler.handle_mention(mention(f"<@U0BOT> summary {PERMALINK}"))
        self.assertTrue(client.posted[0]["text"].startswith(f"_On_ <{PERMALINK}>"))

    def test_an_empty_thread_is_reported_not_summarised(self):
        handler, client, run = build(client=FakeSlackClient(replies=[], users=USERS))
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertIn("could not read that", client.posted[0]["text"])
        self.assertEqual(run.calls, [])

    def test_a_slack_failure_is_reported_in_the_thread(self):
        client = FakeSlackClient(fail={"conversations_replies": "not_in_channel"})
        handler, client, run = build(client=client)
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertIn("not_in_channel", client.posted[0]["text"])
        self.assertEqual(run.calls, [])


FORWARD = [
    {
        "type": "message",
        "user": "U0RIMURU",
        "ts": "1758069000.000500",
        "text": "",
        "attachments": [{"from_url": PERMALINK, "author_id": "U0HAKUROU"}],
    }
]


class ForwardedSubjectTests(unittest.TestCase):
    """A thread whose parent is a forward is a wrapper, not the subject."""

    def _client(self):
        return FakeSlackClient(
            pages=[
                {"ok": True, "messages": FORWARD, "has_more": False},
                {"ok": True, "messages": THREAD, "has_more": False},
            ],
            users=USERS,
        )

    def test_the_forwarded_thread_is_read_instead_of_the_wrapper(self):
        handler, client, run = build(client=self._client())
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts="1758069000.000500"))
        self.assertEqual(client.replies_calls[1]["channel"], "C0OTHER")
        self.assertEqual(client.replies_calls[1]["ts"], "1758067200.000100")
        _, subject, _ = run.calls[0]
        self.assertIn("Can we move the harbor cutover", subject.body)

    def test_the_forwarded_thread_is_named_as_the_source(self):
        handler, client, _ = build(client=self._client())
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts="1758069000.000500"))
        self.assertTrue(client.posted[0]["text"].startswith(f"_On_ <{PERMALINK}>"))

    def test_a_typed_link_is_not_overridden_by_the_thread_it_was_typed_in(self):
        handler, client, run = build(client=self._client())
        handler.handle_mention(
            mention(f"<@U0BOT> summary {PERMALINK}", thread_ts="1758069000.000500")
        )
        # One fetch only: the link the user typed, never the wrapper's own.
        self.assertEqual(len(client.replies_calls), 1)
        self.assertEqual(client.replies_calls[0]["channel"], "C0OTHER")


class OwnMessageTests(unittest.TestCase):
    """The bot's earlier answers are not thread content for the next command."""

    OWN_REPLY = {
        "type": "message",
        "user": "U0BOT",
        "bot_id": "B0DAIKENJA",
        "ts": "1758068900.000450",
        "thread_ts": "1758067200.000100",
        "text": "Thread: an earlier summary this bot posted, 8 messages",
    }

    def test_the_bots_own_reply_is_dropped_from_the_transcript(self):
        client = FakeSlackClient(replies=THREAD + [self.OWN_REPLY], users=USERS)
        handler, client, run = build(client=client)
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts="1758067200.000100"))
        _, subject, _ = run.calls[0]
        self.assertNotIn("an earlier summary this bot posted", subject.body)
        self.assertEqual(subject.label, "#harbor-rollout, 4 messages")

    def test_another_apps_message_is_kept(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts="1758067200.000100"))
        _, subject, _ = run.calls[0]
        self.assertIn("Build 412 is green.", subject.body)

    def test_a_thread_of_nothing_but_the_bot_is_reported_not_summarised(self):
        client = FakeSlackClient(replies=[self.OWN_REPLY], users=USERS)
        handler, client, run = build(client=client)
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts="1758067200.000100"))
        self.assertIn("could not read that", client.posted[0]["text"])
        self.assertEqual(run.calls, [])


class ConfluenceTests(unittest.TestCase):
    def _configured(self):
        return parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU"},
                "confluence": {
                    "base_url": "https://example.atlassian.net",
                    "email": "rimuru@example.com",
                    "token_env": "WIKI_TOKEN",
                },
            }
        )

    def test_unconfigured_says_so_and_stops(self):
        handler, client, run = build()
        handler.handle_mention(mention(f"<@U0BOT> judgement {PAGE_URL}"))
        self.assertIn("not configured", client.posted[0]["text"])
        self.assertEqual(run.calls, [])

    def test_a_configured_page_is_fetched_and_judged(self):
        page = Subject(kind=PAGE, label="Cutover plan", body="Friday", source_url=PAGE_URL)
        seen: list = []
        run = Recorder(answer="AI review summary")
        client = FakeSlackClient(replies=THREAD, users=USERS)
        handler = Handler(
            self._configured(),
            SlackIO(client),
            environ={"WIKI_TOKEN": "t"},
            run=run,
            fetch_confluence=lambda config, url, token: seen.append((url, token)) or page,
        )
        handler.handle_mention(mention(f"<@U0BOT> judgement {PAGE_URL}"))
        self.assertEqual(seen, [(PAGE_URL, "t")])
        self.assertEqual(run.calls[0][0], "judgement")
        self.assertEqual(run.calls[0][1].label, "Cutover plan")
        self.assertEqual(client.replies_calls, [])
        self.assertIn("AI review summary", client.posted[0]["text"])
        self.assertTrue(client.posted[0]["text"].startswith(f"_On_ <{PAGE_URL}>"))

    def test_a_missing_token_is_reported_not_raised(self):
        handler = Handler(
            self._configured(),
            SlackIO(FakeSlackClient(replies=THREAD, users=USERS)),
            environ={},
            run=Recorder(),
            fetch_confluence=lambda *a, **k: None,
        )
        client = handler._slack._client  # noqa: SLF001 - asserting on the stand-in
        handler.handle_mention(mention(f"<@U0BOT> judgement {PAGE_URL}"))
        self.assertIn("WIKI_TOKEN", client.posted[0]["text"])

    def test_a_fetch_failure_is_reported(self):
        handler = Handler(
            self._configured(),
            SlackIO(FakeSlackClient(replies=THREAD, users=USERS)),
            environ={"WIKI_TOKEN": "t"},
            run=Recorder(),
            fetch_confluence=_raise(ConfluenceError("that page does not exist")),
        )
        client = handler._slack._client  # noqa: SLF001
        handler.handle_mention(mention(f"<@U0BOT> judgement {PAGE_URL}"))
        self.assertIn("does not exist", client.posted[0]["text"])


class UnavailableCommandTests(unittest.TestCase):
    def test_a_disabled_command_says_so_and_runs_nothing(self):
        client = FakeSlackClient(replies=THREAD, users=USERS)
        run = Recorder()
        handler = Handler(
            make_config(),
            SlackIO(client),
            environ={},
            run=run,
            fetch_confluence=lambda *a, **k: None,
            unavailable={"judgement": "I cannot run `judgement`: the skill is missing."},
        )
        handler.handle_mention(mention("<@U0BOT> judgement"))
        self.assertIn("cannot run", client.posted[0]["text"])
        self.assertEqual(run.calls, [])
        self.assertEqual(client.replies_calls, [])

    def test_no_reaction_is_added_for_a_disabled_command(self):
        client = FakeSlackClient(replies=THREAD, users=USERS)
        handler = Handler(
            make_config(),
            SlackIO(client),
            environ={},
            run=Recorder(),
            fetch_confluence=lambda *a, **k: None,
            unavailable={"judgement": "nope"},
        )
        handler.handle_mention(mention("<@U0BOT> judgement"))
        self.assertEqual(client.reactions, [])

    def test_the_other_command_still_works(self):
        client = FakeSlackClient(replies=THREAD, users=USERS)
        run = Recorder()
        handler = Handler(
            make_config(),
            SlackIO(client),
            environ={},
            run=run,
            fetch_confluence=lambda *a, **k: None,
            unavailable={"judgement": "nope"},
        )
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(run.calls[0][0], "summary")


class UnknownLinkTests(unittest.TestCase):
    def test_an_unrecognised_link_gets_one_line(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> judgement https://example.com/harbor"))
        self.assertEqual(client.posted[0]["text"], UNKNOWN_LINK)
        self.assertEqual(run.calls, [])


class AcknowledgementTests(unittest.TestCase):
    def test_the_mention_is_reacted_to(self):
        handler, client, _ = build()
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(client.reactions[0]["name"], "eyes")
        self.assertEqual(client.reactions[0]["timestamp"], "1758069600.000600")

    def test_the_reaction_can_be_switched_off(self):
        config = parse_config({"slack": {"owner_user_id": "U0RIMURU", "ack_reaction": None}})
        handler, client, _ = build(config=config)
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(client.reactions, [])

    def test_a_missing_reaction_scope_does_not_stop_the_answer(self):
        client = FakeSlackClient(replies=THREAD, users=USERS, fail={"reactions_add": "missing_scope"})
        handler, client, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertEqual(len(client.posted), 1)


class AnswerTests(unittest.TestCase):
    def test_the_answer_is_converted_to_mrkdwn(self):
        handler, client, _ = build(run=Recorder(answer="**Ledger:** nothing on this"))
        handler.handle_mention(mention("<@U0BOT> judgement"))
        self.assertEqual(client.posted[0]["text"], "*Ledger:* nothing on this")

    def test_a_failed_run_is_reported_in_the_thread_and_logged(self):
        handler, client, _ = build(run=Recorder(error=RunnerError("the session timed out")))
        with self.assertLogs("daikenja_bot.handler", level="WARNING"):
            handler.handle_mention(mention("<@U0BOT> judgement"))
        self.assertIn("timed out", client.posted[0]["text"])

    def test_a_failed_post_is_logged_rather_than_raised(self):
        client = FakeSlackClient(replies=THREAD, users=USERS, fail={"chat_postMessage": "msg_too_long"})
        handler, _, _ = build(client=client)
        with self.assertLogs("daikenja_bot.handler", level="ERROR") as logged:
            handler.handle_mention(mention("<@U0BOT> summary"))
        self.assertIn("msg_too_long", "\n".join(logged.output))


class NamedProjectTests(unittest.TestCase):
    def test_the_key_reaches_the_session(self):
        handler, _, run = build()
        handler.handle_mention(mention("<@U0BOT> judgement project harbor"))
        self.assertEqual(run.calls[0][2], "harbor")

    def test_the_thread_is_still_the_subject(self):
        handler, _, run = build()
        handler.handle_mention(mention("<@U0BOT> summary project harbor"))
        _, subject, project = run.calls[0]
        self.assertEqual(project, "harbor")
        self.assertIn("hakurou", subject.body)

    def test_a_key_with_a_link_reads_the_linked_thread(self):
        handler, client, run = build()
        handler.handle_mention(mention(f"<@U0BOT> judgement project harbor <{PERMALINK}>"))
        _, subject, project = run.calls[0]
        self.assertEqual(project, "harbor")
        self.assertEqual(subject.source_url, PERMALINK)

    def test_without_the_keyword_no_project_is_named(self):
        handler, _, run = build()
        handler.handle_mention(mention("<@U0BOT> judgement"))
        self.assertIsNone(run.calls[0][2])

    def test_the_keyword_with_no_key_is_answered_with_usage(self):
        handler, client, run = build()
        handler.handle_mention(mention("<@U0BOT> judgement project"))
        self.assertEqual(run.calls, [])
        self.assertIn("three commands", client.posted[0]["text"])


class DeleteTests(unittest.TestCase):
    """`delete` takes down the bot's own last post and nothing else."""

    def thread_with_two_of_mine(self):
        return [
            {"user": "U0RIMURU", "ts": "1758067200.000100", "text": "the question"},
            {"user": "U0BOT", "ts": "1758067300.000200", "text": "an early answer"},
            {"user": "U0SHION", "ts": "1758067400.000300", "text": "a reply"},
            {"user": "U0BOT", "ts": "1758067500.000400", "text": "the latest answer"},
        ]

    def test_the_latest_own_message_is_deleted(self):
        client = FakeSlackClient(replies=self.thread_with_two_of_mine(), users=USERS)
        handler, _, run = build(client=client)
        handler.handle_mention(mention("<@U0BOT> delete", thread_ts="1758067200.000100"))
        self.assertEqual(len(client.deleted), 1)
        self.assertEqual(client.deleted[0]["ts"], "1758067500.000400")
        self.assertEqual(client.deleted[0]["channel"], "C0HARBOR")
        self.assertEqual(run.calls, [])

    def test_nothing_is_posted_into_the_thread(self):
        client = FakeSlackClient(replies=self.thread_with_two_of_mine(), users=USERS)
        handler, _, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> delete", thread_ts="1758067200.000100"))
        self.assertEqual(client.posted, [])
        self.assertEqual(len(client.ephemeral), 1)
        self.assertIn("Deleted my last post", client.ephemeral[0]["text"])

    def test_the_count_of_what_is_left_is_reported(self):
        client = FakeSlackClient(replies=self.thread_with_two_of_mine(), users=USERS)
        handler, _, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> delete", thread_ts="1758067200.000100"))
        self.assertIn("1 earlier post of mine is", client.ephemeral[0]["text"])

    def test_no_acknowledging_reaction(self):
        client = FakeSlackClient(replies=self.thread_with_two_of_mine(), users=USERS)
        handler, _, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> delete", thread_ts="1758067200.000100"))
        self.assertEqual(client.reactions, [])

    def test_a_thread_with_nothing_of_mine_deletes_nothing(self):
        client = FakeSlackClient(replies=THREAD, users=USERS)
        handler, _, _ = build(client=client)
        handler.handle_mention(mention("<@U0BOT> delete", thread_ts="1758067200.000100"))
        self.assertEqual(client.deleted, [])
        self.assertIn("have not posted", client.ephemeral[0]["text"])

    def test_a_stranger_cannot_delete(self):
        client = FakeSlackClient(replies=self.thread_with_two_of_mine(), users=USERS)
        handler, _, _ = build(client=client)
        handler.handle_mention(
            mention("<@U0BOT> delete", user="U0GOBTA", thread_ts="1758067200.000100")
        )
        self.assertEqual(client.deleted, [])

    def test_a_failed_delete_is_reported_and_logged(self):
        client = FakeSlackClient(
            replies=self.thread_with_two_of_mine(),
            users=USERS,
            fail={"chat_delete": "message_not_found"},
        )
        handler, _, _ = build(client=client)
        with self.assertLogs("daikenja_bot.handler", level="WARNING"):
            handler.handle_mention(
                mention("<@U0BOT> delete", thread_ts="1758067200.000100")
            )
        self.assertIn("message_not_found", client.ephemeral[0]["text"])


def _raise(exc: Exception):
    def fetch(*args, **kwargs):
        raise exc

    return fetch


def reaction(name: str = "daikenja", user: str = "U0RIMURU", ts: str = "1758067200.000100") -> dict:
    return {"user": user, "reaction": name, "item": {"type": "message", "channel": "C0HARBOR", "ts": ts}}


class ReactionEventTests(unittest.TestCase):
    def test_the_event_is_read_out(self):
        event = ReactionEvent.from_event(reaction())
        self.assertEqual(event.user_id, "U0RIMURU")
        self.assertEqual(event.channel_id, "C0HARBOR")
        self.assertEqual(event.message_ts, "1758067200.000100")
        self.assertEqual(event.reaction, "daikenja")


class CombinedRecorder:
    """Stands in for `run_command`, answering `summary` and `judgement` differently."""

    def __init__(self, answers: dict | None = None, error_on: str | None = None):
        self.answers = answers or {
            "summary": "Thread: four messages",
            "judgement": "Verdict: fine",
        }
        self.error_on = error_on
        self.calls: list[tuple] = []

    def __call__(self, config, command_name, subject, *, environ):
        self.calls.append((command_name, subject))
        if command_name == self.error_on:
            raise RunnerError("the session timed out")
        return self.answers[command_name]


class ReactionTriggerTests(unittest.TestCase):
    PARENT = THREAD[0]
    REPLY = THREAD[2]

    def _client(self, history=None, replies=None, **kwargs):
        return FakeSlackClient(
            replies=THREAD if replies is None else replies,
            users=USERS,
            history=history,
            **kwargs,
        )

    def _handler(self, client, run=None, config=None, unavailable=None):
        run = run or CombinedRecorder()
        handler = Handler(
            config or make_config(reaction_trigger="daikenja"),
            SlackIO(client),
            environ={"PATH": "/bin"},
            run=run,
            fetch_confluence=lambda *a, **k: None,
            unavailable=unavailable,
        )
        return handler, run

    def test_a_non_trigger_emoji_does_nothing(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction(name="thumbsup"))
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])
        self.assertEqual(client.history_calls, [])

    def test_no_trigger_configured_does_nothing(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client, config=make_config())
        handler.handle_reaction(reaction())
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])

    def test_a_stranger_gets_nothing_and_no_session(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction(user="U0GOBTA"))
        self.assertEqual(client.posted, [])
        self.assertEqual(client.ephemeral, [])
        self.assertEqual(run.calls, [])

    def test_the_owner_gets_one_combined_post(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(len(client.posted), 1)
        self.assertEqual([c[0] for c in run.calls], ["summary", "judgement"])
        self.assertIn("Thread: four messages", client.posted[0]["text"])
        self.assertIn("Verdict: fine", client.posted[0]["text"])

    def test_the_post_lands_in_the_reacted_threads_thread(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(client.posted[0]["channel"], "C0HARBOR")
        self.assertEqual(client.posted[0]["thread_ts"], "1758067200.000100")

    def test_a_reaction_on_a_reply_resolves_to_the_parent_thread(self):
        client = self._client(history=self.REPLY)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction(ts="1758067800.000300"))
        # replies_calls[0] is fetch_message resolving the reacted-to reply
        # itself; replies_calls[1] is fetch_thread reading the whole thread
        # once thread_ts is known.
        self.assertEqual(client.replies_calls[1]["ts"], "1758067200.000100")
        self.assertEqual(client.posted[0]["thread_ts"], "1758067200.000100")

    def test_the_bot_marks_the_message_it_answered(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(client.reactions[0]["name"], "eyes")
        self.assertEqual(client.reactions[0]["timestamp"], "1758067200.000100")

    def test_a_failed_ack_still_stops_a_second_answer(self):
        # The re-fire guard's usual memory is the bot's own eyes reaction on
        # the message. When adding it fails -- the message was deleted while
        # the two headless sessions ran, for instance -- this in-memory
        # record is what keeps a second trigger on the same message from
        # producing a second answer.
        client = self._client(
            history=self.PARENT, fail={"reactions_add": "message_not_found"}
        )
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        handler.handle_reaction(reaction())
        self.assertEqual(len(client.posted), 1)
        self.assertEqual([c[0] for c in run.calls], ["summary", "judgement"])

    def test_an_already_answered_message_is_skipped(self):
        # fetch_message now resolves via conversations.replies before ever
        # trying conversations.history, so the thread it searches -- not
        # just `history` -- has to carry the ack reaction.
        answered = {**self.PARENT, "reactions": [{"name": "eyes", "users": ["U0BOT"]}]}
        client = self._client(replies=[answered, *THREAD[1:]], history=answered)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])

    def test_someone_elses_eyes_reaction_does_not_count_as_answered(self):
        answered = {**self.PARENT, "reactions": [{"name": "eyes", "users": ["U0RIMURU"]}]}
        client = self._client(replies=[answered, *THREAD[1:]], history=answered)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(len(client.posted), 1)

    def test_no_message_found_does_nothing(self):
        # An empty thread lookup alongside `history=None` -- both of
        # fetch_message's lookups come back empty, not just one.
        client = self._client(replies=[], history=None)
        handler, run = self._handler(client)
        handler.handle_reaction(reaction())
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])

    def test_a_failed_command_posts_nothing(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client, run=CombinedRecorder(error_on="judgement"))
        with self.assertLogs("daikenja_bot.handler", level="WARNING"):
            handler.handle_reaction(reaction())
        self.assertEqual(client.posted, [])

    def test_a_disabled_command_posts_nothing(self):
        client = self._client(history=self.PARENT)
        handler, run = self._handler(client, unavailable={"judgement": "nope"})
        handler.handle_reaction(reaction())
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])


class DeleteReactionTests(unittest.TestCase):
    """An `:x:` on one of the bot's own messages deletes it."""

    OWN_MESSAGE = {"user": "U0BOT", "ts": "1758067500.000400", "text": "an answer"}
    OTHERS_MESSAGE = {"user": "U0SHION", "ts": "1758067500.000400", "text": "not mine"}

    def _handler(self, client, config=None):
        handler = Handler(
            config or make_config(),
            SlackIO(client),
            environ={"PATH": "/bin"},
            fetch_confluence=lambda *a, **k: None,
        )
        return handler

    def test_x_on_the_bots_own_message_deletes_it(self):
        client = FakeSlackClient(history=self.OWN_MESSAGE, users=USERS)
        handler = self._handler(client)
        handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))
        self.assertEqual(len(client.deleted), 1)
        self.assertEqual(client.deleted[0]["ts"], "1758067500.000400")
        self.assertEqual(client.deleted[0]["channel"], "C0HARBOR")

    def test_x_on_someone_elses_message_deletes_nothing(self):
        client = FakeSlackClient(history=self.OTHERS_MESSAGE, users=USERS)
        handler = self._handler(client)
        handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))
        self.assertEqual(client.deleted, [])

    def test_a_stranger_cannot_delete_via_reaction(self):
        client = FakeSlackClient(history=self.OWN_MESSAGE, users=USERS)
        handler = self._handler(client)
        handler.handle_reaction(
            reaction(name="x", user="U0GOBTA", ts="1758067500.000400")
        )
        self.assertEqual(client.deleted, [])

    def test_no_message_found_deletes_nothing(self):
        client = FakeSlackClient(history=None, users=USERS)
        handler = self._handler(client)
        handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))
        self.assertEqual(client.deleted, [])

    def test_delete_reaction_can_be_turned_off(self):
        client = FakeSlackClient(history=self.OWN_MESSAGE, users=USERS)
        handler = self._handler(client, config=make_config(delete_reaction=None))
        handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))
        self.assertEqual(client.deleted, [])

    def test_a_failed_delete_is_logged(self):
        client = FakeSlackClient(
            history=self.OWN_MESSAGE,
            users=USERS,
            fail={"chat_delete": "message_not_found"},
        )
        handler = self._handler(client)
        with self.assertLogs("daikenja_bot.handler", level="WARNING"):
            handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))

    def test_x_does_not_run_the_summary_judgement_path(self):
        # `x` is not the reaction_trigger, so nothing else should fire even
        # when that trigger is configured too.
        client = FakeSlackClient(history=self.OWN_MESSAGE, users=USERS)
        run = CombinedRecorder()
        handler = Handler(
            make_config(reaction_trigger="daikenja"),
            SlackIO(client),
            environ={"PATH": "/bin"},
            run=run,
            fetch_confluence=lambda *a, **k: None,
        )
        handler.handle_reaction(reaction(name="x", ts="1758067500.000400"))
        self.assertEqual(len(client.deleted), 1)
        self.assertEqual(client.posted, [])
        self.assertEqual(run.calls, [])


if __name__ == "__main__":
    unittest.main()


LINKED_PAGE_URL = "https://example.atlassian.net/wiki/spaces/HARBOR/pages/555/Runbook"
LINKED_PAGE = Subject(kind=PAGE, label="Runbook", body="Step 1: drain", source_url=LINKED_PAGE_URL)
THREAD_WITH_LINK = THREAD + [
    {
        "type": "message",
        "user": "U0SHION",
        "ts": "1758067500.000500",
        "thread_ts": THREAD[0]["ts"],
        "text": f"please review <{LINKED_PAGE_URL}|the runbook>",
    }
]


def _wiki_config():
    return parse_config(
        {
            "slack": {"owner_user_id": "U0RIMURU", "reaction_trigger": "daikenja"},
            "confluence": {
                "base_url": "https://example.atlassian.net",
                "email": "rimuru@example.com",
                "token_env": "WIKI_TOKEN",
            },
        }
    )


def _pages(table):
    def fetch(config, url, token):
        if url not in table:
            raise ConfluenceError("gone", reason="not found or not visible")
        return table[url]

    return fetch


class FollowedLinkTests(unittest.TestCase):
    def _handler(self, replies, table, run=None, config=None):
        client = FakeSlackClient(replies=replies, users=USERS, history=replies[0])
        run = run or Recorder()
        handler = Handler(
            config or _wiki_config(),
            SlackIO(client),
            environ={"WIKI_TOKEN": "t"},
            run=run,
            fetch_confluence=_pages(table),
        )
        return handler, client, run

    def test_a_page_linked_in_the_thread_is_attached(self):
        handler, client, run = self._handler(THREAD_WITH_LINK, {LINKED_PAGE_URL: LINKED_PAGE})
        handler.handle_mention(mention("<@U0BOT> judgement", thread_ts=THREAD[0]["ts"]))
        subject = run.calls[0][1]
        self.assertEqual([a.label for a in subject.attachments], ["Runbook"])
        self.assertEqual(subject.unread, ())

    def test_a_linked_page_that_fails_is_noted_and_the_run_goes_on(self):
        handler, client, run = self._handler(THREAD_WITH_LINK, {})
        handler.handle_mention(mention("<@U0BOT> judgement", thread_ts=THREAD[0]["ts"]))
        subject = run.calls[0][1]
        self.assertEqual(subject.attachments, ())
        self.assertEqual(subject.unread[0].reason, "not found or not visible")
        self.assertEqual(len(client.posted), 1)

    def test_an_unconfigured_bot_notes_the_page_and_still_answers(self):
        handler, client, run = self._handler(
            THREAD_WITH_LINK, {}, config=make_config()
        )
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts=THREAD[0]["ts"]))
        self.assertEqual(run.calls[0][1].unread[0].reason, "Confluence not configured")
        self.assertIn("Thread: four messages", client.posted[0]["text"])

    def test_an_extra_argument_is_attached_and_counted_in_the_header(self):
        main = Subject(kind=PAGE, label="Cutover plan", body="Friday", source_url=PAGE_URL)
        handler, client, run = self._handler(
            THREAD, {PAGE_URL: main, LINKED_PAGE_URL: LINKED_PAGE}
        )
        handler.handle_mention(
            mention(f"<@U0BOT> judgement <{PAGE_URL}> and <{LINKED_PAGE_URL}>")
        )
        self.assertEqual(run.calls[0][1].label, "Cutover plan")
        self.assertEqual(run.calls[0][1].attachments[0].label, "Runbook")
        self.assertTrue(
            client.posted[0]["text"].startswith(f"_On_ <{PAGE_URL}> + 1 linked")
        )

    def test_the_header_is_unchanged_with_nothing_linked(self):
        main = Subject(kind=PAGE, label="Cutover plan", body="Friday", source_url=PAGE_URL)
        handler, client, run = self._handler(THREAD, {PAGE_URL: main})
        handler.handle_mention(mention(f"<@U0BOT> judgement <{PAGE_URL}>"))
        self.assertTrue(client.posted[0]["text"].startswith(f"_On_ <{PAGE_URL}>\n"))

    def test_the_reaction_path_attaches_too(self):
        run = CombinedRecorder()
        handler, client, _ = self._handler(
            THREAD_WITH_LINK, {LINKED_PAGE_URL: LINKED_PAGE}, run=run
        )
        handler.handle_reaction(reaction(ts=THREAD[0]["ts"]))
        self.assertEqual([c[0] for c in run.calls], ["summary", "judgement"])
        for _, subject in run.calls:
            self.assertEqual([a.label for a in subject.attachments], ["Runbook"])


ISSUE_URL = "https://example.atlassian.net/browse/HAR-12"
ISSUE_SUBJECT = Subject(kind=ISSUE, label="HAR-12: Move the cutover", body="HAR-12 (Story, Done)", source_url=ISSUE_URL)


class JiraLinkTests(unittest.TestCase):
    def _handler(self, replies=None, config=None):
        client = FakeSlackClient(replies=replies or THREAD, users=USERS)
        run = Recorder()
        seen = []

        def fetch_jira(config, url, token, limit=None):
            seen.append((url, limit))
            return ISSUE_SUBJECT

        handler = Handler(
            config or _wiki_config(),
            SlackIO(client),
            environ={"WIKI_TOKEN": "t"},
            run=run,
            fetch_jira=fetch_jira,
        )
        return handler, client, run, seen

    def test_an_issue_is_a_subject_in_its_own_right(self):
        handler, client, run, seen = self._handler()
        handler.handle_mention(mention(f"<@U0BOT> judgement <{ISSUE_URL}>"))
        self.assertEqual(seen, [(ISSUE_URL, None)])
        self.assertEqual(run.calls[0][1].kind, ISSUE)
        self.assertTrue(client.posted[0]["text"].startswith(f"_On_ <{ISSUE_URL}>"))

    def test_an_issue_linked_in_the_thread_is_attached(self):
        replies = THREAD + [
            {
                "type": "message",
                "user": "U0SHION",
                "ts": "1758067500.000500",
                "thread_ts": THREAD[0]["ts"],
                "text": f"tracked in <{ISSUE_URL}|HAR-12>",
            }
        ]
        handler, client, run, seen = self._handler(replies=replies)
        handler.handle_mention(mention("<@U0BOT> summary", thread_ts=THREAD[0]["ts"]))
        self.assertEqual(run.calls[0][1].attachments, (ISSUE_SUBJECT,))

    def test_unconfigured_jira_says_so_and_stops(self):
        handler, client, run, _ = self._handler(config=make_config())
        handler.handle_mention(mention(f"<@U0BOT> judgement <{ISSUE_URL}>"))
        self.assertIn("Jira links are not configured", client.posted[0]["text"])
        self.assertEqual(run.calls, [])
