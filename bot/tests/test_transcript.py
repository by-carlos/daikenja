import unittest

from daikenja_bot.transcript import (
    format_timestamp,
    render_thread,
    resolve_mentions,
    speaker_name,
)

from .fakes import load_fixture

USERS = {"U0HAKUROU": "hakurou", "U0RIGURD": "rigurd", "U0SHION": "shion"}


class TimestampTests(unittest.TestCase):
    def test_slack_timestamp_renders_as_utc(self):
        self.assertEqual(format_timestamp("1758067200.000100"), "2025-09-17 00:00 UTC")

    def test_nonsense_timestamp_comes_back_as_given(self):
        self.assertEqual(format_timestamp("not-a-time"), "not-a-time")


class SpeakerTests(unittest.TestCase):
    def test_known_user(self):
        self.assertEqual(speaker_name({"user": "U0RIGURD"}, USERS), "rigurd")

    def test_unknown_user_falls_back_to_the_id(self):
        self.assertEqual(speaker_name({"user": "U0DIABLO"}, USERS), "U0DIABLO")

    def test_bot_uses_its_username(self):
        self.assertEqual(
            speaker_name({"bot_id": "B0X", "username": "releasebot"}, USERS),
            "releasebot",
        )


class MentionTests(unittest.TestCase):
    def test_user_mentions_become_names(self):
        self.assertEqual(resolve_mentions("ping <@U0RIGURD>", USERS), "ping @rigurd")

    def test_channel_mentions_become_names(self):
        self.assertEqual(
            resolve_mentions("in <#C0HARBOR|harbor-rollout>", USERS),
            "in #harbor-rollout",
        )

    def test_labelled_links_keep_both_parts(self):
        self.assertEqual(
            resolve_mentions("<https://example.com/x|the page>", USERS),
            "the page (https://example.com/x)",
        )

    def test_bare_links_stay_bare(self):
        self.assertEqual(
            resolve_mentions("<https://example.com/x>", USERS), "https://example.com/x"
        )


class RenderThreadTests(unittest.TestCase):
    def setUp(self):
        self.messages = load_fixture("sample-thread.json")["messages"]

    def test_join_events_are_dropped_and_numbering_stays_dense(self):
        subject = render_thread(self.messages, USERS, "#harbor-rollout")
        self.assertIn("[1] hakurou", subject.body)
        self.assertIn("[2] rigurd", subject.body)
        self.assertIn("[3] shion", subject.body)
        self.assertIn("[4] releasebot", subject.body)
        self.assertNotIn("has joined the channel", subject.body)

    def test_label_counts_the_messages_that_were_kept(self):
        subject = render_thread(self.messages, USERS, "#harbor-rollout")
        self.assertEqual(subject.label, "#harbor-rollout, 4 messages")

    def test_one_message_is_singular(self):
        subject = render_thread(self.messages[:1], USERS, "#harbor-rollout")
        self.assertEqual(subject.label, "#harbor-rollout, 1 message")

    def test_mentions_inside_the_text_are_resolved(self):
        subject = render_thread(self.messages, USERS, "#harbor-rollout")
        self.assertIn("@rigurd you owned the validation step", subject.body)

    def test_attachments_are_named_and_marked_unread(self):
        subject = render_thread(self.messages, USERS, "#harbor-rollout")
        self.assertIn("[attachment: cutover-timings.csv -- not read]", subject.body)

    def test_source_url_is_carried_through(self):
        subject = render_thread(
            self.messages, USERS, "#harbor-rollout", source_url="https://example.com/t"
        )
        self.assertEqual(subject.source_url, "https://example.com/t")

    def test_an_empty_thread_is_empty(self):
        self.assertTrue(render_thread([], USERS, "#harbor-rollout").is_empty)


if __name__ == "__main__":
    unittest.main()
