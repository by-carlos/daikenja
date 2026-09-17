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


class ReactionTests(unittest.TestCase):
    def test_a_reaction_is_added(self):
        client = FakeSlackClient()
        self.assertTrue(SlackIO(client).add_reaction("C0HARBOR", "1", "eyes"))
        self.assertEqual(client.reactions[0]["name"], "eyes")

    def test_a_missing_scope_is_swallowed(self):
        client = FakeSlackClient(fail={"reactions_add": "missing_scope"})
        self.assertFalse(SlackIO(client).add_reaction("C0HARBOR", "1", "eyes"))


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
