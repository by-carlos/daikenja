import unittest

from daikenja_bot.commands import USAGE
from daikenja_bot.config import parse_config
from daikenja_bot.confluence import ConfluenceError
from daikenja_bot.handler import UNKNOWN_LINK, Handler, MentionEvent
from daikenja_bot.runner import RunnerError
from daikenja_bot.slack_io import SlackIO
from daikenja_bot.subject import PAGE, Subject

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

    def __call__(self, config, command_name, subject, *, environ):
        self.calls.append((command_name, subject))
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
        self.assertIn("two commands", client.posted[0]["text"])
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
        command, subject = run.calls[0]
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


def _raise(exc: Exception):
    def fetch(*args, **kwargs):
        raise exc

    return fetch


if __name__ == "__main__":
    unittest.main()
