import unittest

from daikenja_bot.slack_io import SlackError, SlackIO, thread_participants

from .fakes import FakeSlackClient


class FetchThreadTests(unittest.TestCase):
    def test_a_single_page(self):
        client = FakeSlackClient(replies=[{"ts": "1", "user": "U0RIMURU", "text": "hi"}])
        messages = SlackIO(client).fetch_thread("C0HARBOR", "1")
        self.assertEqual(len(messages), 1)
        self.assertEqual(client.replies_calls[0]["channel"], "C0HARBOR")
        self.assertEqual(client.replies_calls[0]["ts"], "1")

    def test_pagination_follows_the_cursor(self):
        client = FakeSlackClient(
            pages=[
                {
                    "ok": True,
                    "messages": [{"ts": "1"}],
                    "has_more": True,
                    "response_metadata": {"next_cursor": "page-2"},
                },
                {"ok": True, "messages": [{"ts": "2"}], "has_more": False},
            ]
        )
        messages = SlackIO(client).fetch_thread("C0HARBOR", "1")
        self.assertEqual([m["ts"] for m in messages], ["1", "2"])
        self.assertEqual(client.replies_calls[1]["cursor"], "page-2")

    def test_has_more_without_a_cursor_stops(self):
        client = FakeSlackClient(
            pages=[{"ok": True, "messages": [{"ts": "1"}], "has_more": True}]
        )
        messages = SlackIO(client).fetch_thread("C0HARBOR", "1")
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(client.replies_calls), 1)

    def test_an_api_error_becomes_a_slack_error(self):
        client = FakeSlackClient(fail={"conversations_replies": "channel_not_found"})
        with self.assertRaises(SlackError) as caught:
            SlackIO(client).fetch_thread("C0HARBOR", "1")
        self.assertIn("channel_not_found", str(caught.exception))

    def test_an_ok_false_response_becomes_a_slack_error(self):
        client = FakeSlackClient(pages=[{"ok": False, "error": "not_in_channel"}])
        with self.assertRaises(SlackError) as caught:
            SlackIO(client).fetch_thread("C0HARBOR", "1")
        self.assertIn("not_in_channel", str(caught.exception))


class ChannelLabelTests(unittest.TestCase):
    def test_the_name_is_prefixed_with_a_hash(self):
        self.assertEqual(
            SlackIO(FakeSlackClient(channel_name="harbor-rollout")).channel_label("C0HARBOR"),
            "#harbor-rollout",
        )

    def test_an_unreadable_channel_falls_back_to_its_id(self):
        client = FakeSlackClient(fail={"conversations_info": "missing_scope"})
        self.assertEqual(SlackIO(client).channel_label("D0DIRECT"), "D0DIRECT")

    def test_the_lookup_is_cached(self):
        client = FakeSlackClient(channel_name="harbor-rollout")
        slack = SlackIO(client)
        slack.channel_label("C0HARBOR")
        slack.channel_label("C0HARBOR")
        self.assertEqual(slack.channel_label("C0HARBOR"), "#harbor-rollout")


class UserNameTests(unittest.TestCase):
    def test_names_are_resolved(self):
        client = FakeSlackClient(users={"U0RIGURD": "rigurd"})
        self.assertEqual(SlackIO(client).user_names(["U0RIGURD"]), {"U0RIGURD": "rigurd"})

    def test_an_unknown_user_maps_to_its_own_id(self):
        client = FakeSlackClient(users={})
        self.assertEqual(SlackIO(client).user_names(["U0DIABLO"]), {"U0DIABLO": "U0DIABLO"})

    def test_a_failing_lookup_does_not_stop_the_batch(self):
        client = FakeSlackClient(fail={"users_info": "ratelimited"})
        names = SlackIO(client).user_names(["U0RIGURD", "U0SHION"])
        self.assertEqual(set(names), {"U0RIGURD", "U0SHION"})


class PostTests(unittest.TestCase):
    def test_a_reply_is_always_threaded_and_never_unfurls(self):
        client = FakeSlackClient()
        SlackIO(client).post("C0HARBOR", "1758067200.000100", "the answer")
        sent = client.posted[0]
        self.assertEqual(sent["channel"], "C0HARBOR")
        self.assertEqual(sent["thread_ts"], "1758067200.000100")
        self.assertEqual(sent["text"], "the answer")
        self.assertFalse(sent["unfurl_links"])

    def test_a_failed_post_raises(self):
        client = FakeSlackClient(fail={"chat_postMessage": "channel_not_found"})
        with self.assertRaises(SlackError):
            SlackIO(client).post("C0HARBOR", "1", "x")


class EphemeralTests(unittest.TestCase):
    def test_it_is_addressed_to_one_person(self):
        client = FakeSlackClient()
        self.assertTrue(
            SlackIO(client).post_ephemeral("C0HARBOR", "U0GOBTA", "not for you")
        )
        sent = client.ephemeral[0]
        self.assertEqual(sent["channel"], "C0HARBOR")
        self.assertEqual(sent["user"], "U0GOBTA")
        self.assertEqual(sent["text"], "not for you")

    def test_no_thread_is_sent_when_there_is_no_thread(self):
        client = FakeSlackClient()
        SlackIO(client).post_ephemeral("C0HARBOR", "U0GOBTA", "x", thread_ts=None)
        self.assertNotIn("thread_ts", client.ephemeral[0])

    def test_a_thread_is_passed_through_when_there_is_one(self):
        client = FakeSlackClient()
        SlackIO(client).post_ephemeral("C0HARBOR", "U0GOBTA", "x", thread_ts="1758067200.000100")
        self.assertEqual(client.ephemeral[0]["thread_ts"], "1758067200.000100")

    def test_a_failure_is_swallowed(self):
        client = FakeSlackClient(fail={"chat_postEphemeral": "user_not_in_channel"})
        self.assertFalse(SlackIO(client).post_ephemeral("C0HARBOR", "U0GOBTA", "x"))


class ReactionTests(unittest.TestCase):
    def test_a_reaction_is_added(self):
        client = FakeSlackClient()
        self.assertTrue(SlackIO(client).add_reaction("C0HARBOR", "1", "eyes"))
        self.assertEqual(client.reactions[0]["name"], "eyes")

    def test_a_missing_scope_is_swallowed(self):
        client = FakeSlackClient(fail={"reactions_add": "missing_scope"})
        self.assertFalse(SlackIO(client).add_reaction("C0HARBOR", "1", "eyes"))

    def test_a_failure_is_logged_as_a_warning(self):
        # Not info: for the reaction trigger this failure disables the
        # re-fire guard, which is a real functional consequence.
        client = FakeSlackClient(fail={"reactions_add": "message_not_found"})
        with self.assertLogs("daikenja_bot.slack_io", level="WARNING"):
            SlackIO(client).add_reaction("C0HARBOR", "1", "eyes")


class FetchMessageTests(unittest.TestCase):
    def test_a_top_level_channel_message_is_returned(self):
        message = {"ts": "1758067200.000100", "user": "U0RIMURU", "text": "hi"}
        client = FakeSlackClient(history=message)
        found = SlackIO(client).fetch_message("C0HARBOR", "1758067200.000100")
        self.assertEqual(found, message)
        self.assertEqual(client.history_calls[0]["channel"], "C0HARBOR")
        self.assertEqual(client.history_calls[0]["latest"], "1758067200.000100")
        self.assertTrue(client.history_calls[0]["inclusive"])

    def test_a_thread_reply_is_found_via_conversations_replies(self):
        parent = {"ts": "1", "thread_ts": "1", "user": "U0RIMURU", "text": "parent"}
        reply = {"ts": "2", "thread_ts": "1", "user": "U0RIMURU", "text": "reply"}
        client = FakeSlackClient(replies=[parent, reply])
        found = SlackIO(client).fetch_message("C0HARBOR", "2")
        self.assertEqual(found, reply)
        self.assertEqual(client.replies_calls[0]["channel"], "C0HARBOR")
        self.assertEqual(client.replies_calls[0]["ts"], "2")
        self.assertEqual(client.history_calls, [])

    def test_a_thread_parent_is_found_via_conversations_replies(self):
        parent = {"ts": "1", "thread_ts": "1", "user": "U0RIMURU", "text": "parent"}
        reply = {"ts": "2", "thread_ts": "1", "user": "U0RIMURU", "text": "reply"}
        client = FakeSlackClient(replies=[parent, reply])
        found = SlackIO(client).fetch_message("C0HARBOR", "1")
        self.assertEqual(found, parent)
        self.assertEqual(client.history_calls, [])

    def test_a_replies_error_falls_back_to_history(self):
        message = {"ts": "1", "user": "U0RIMURU", "text": "hi"}
        client = FakeSlackClient(
            fail={"conversations_replies": "thread_not_found"}, history=message
        )
        found = SlackIO(client).fetch_message("C0HARBOR", "1")
        self.assertEqual(found, message)

    def test_a_history_ts_mismatch_is_treated_as_not_found(self):
        # The exact failure this issue describes: `conversations.history`
        # silently returning the nearest channel-level message instead of
        # the reply that was actually requested.
        wrong_message = {"ts": "999", "user": "U0RIMURU", "text": "wrong"}
        client = FakeSlackClient(history=wrong_message)
        self.assertIsNone(SlackIO(client).fetch_message("C0HARBOR", "1"))

    def test_a_replies_ts_mismatch_falls_back_to_history(self):
        other_thread_message = {"ts": "3", "thread_ts": "3", "user": "U0RIMURU", "text": "other"}
        message = {"ts": "1", "user": "U0RIMURU", "text": "hi"}
        client = FakeSlackClient(replies=[other_thread_message], history=message)
        found = SlackIO(client).fetch_message("C0HARBOR", "1")
        self.assertEqual(found, message)

    def test_nothing_found_is_none(self):
        client = FakeSlackClient(history=None)
        self.assertIsNone(SlackIO(client).fetch_message("C0HARBOR", "1"))

    def test_an_api_error_becomes_a_slack_error(self):
        client = FakeSlackClient(fail={"conversations_history": "channel_not_found"})
        with self.assertRaises(SlackError):
            SlackIO(client).fetch_message("C0HARBOR", "1")


class HasReactionTests(unittest.TestCase):
    def test_the_bots_own_reaction_is_found(self):
        message = {"reactions": [{"name": "eyes", "users": ["U0BOT", "U0RIMURU"]}]}
        self.assertTrue(SlackIO(FakeSlackClient()).has_reaction(message, "eyes"))

    def test_a_different_persons_reaction_does_not_count(self):
        message = {"reactions": [{"name": "eyes", "users": ["U0RIMURU"]}]}
        self.assertFalse(SlackIO(FakeSlackClient()).has_reaction(message, "eyes"))

    def test_a_different_emoji_does_not_count(self):
        message = {"reactions": [{"name": "thumbsup", "users": ["U0BOT"]}]}
        self.assertFalse(SlackIO(FakeSlackClient()).has_reaction(message, "eyes"))

    def test_no_reactions_at_all(self):
        self.assertFalse(SlackIO(FakeSlackClient()).has_reaction({}, "eyes"))


class ParticipantTests(unittest.TestCase):
    def test_only_real_users_are_returned(self):
        messages = [
            {"user": "U0RIMURU"},
            {"user": "U0RIMURU"},
            {"bot_id": "B0X"},
            {"user": "U0SHION"},
        ]
        self.assertEqual(thread_participants(messages), {"U0RIMURU", "U0SHION"})


if __name__ == "__main__":
    unittest.main()
