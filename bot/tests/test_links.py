import unittest

from daikenja_bot.links import (
    extract_links,
    forwarded_permalink,
    looks_like_confluence,
    parse_confluence_page_id,
    parse_slack_permalink,
    unwrap_link,
)


class UnwrapLinkTests(unittest.TestCase):
    def test_angle_brackets_are_removed(self):
        self.assertEqual(unwrap_link("<https://example.com>"), "https://example.com")

    def test_label_is_dropped(self):
        self.assertEqual(
            unwrap_link("<https://example.com|the page>"), "https://example.com"
        )

    def test_plain_url_is_untouched(self):
        self.assertEqual(unwrap_link(" https://example.com "), "https://example.com")


class SlackPermalinkTests(unittest.TestCase):
    def test_parent_permalink(self):
        ref = parse_slack_permalink(
            "https://example.slack.com/archives/C0HARBOR/p1758067200000100"
        )
        assert ref is not None
        self.assertEqual(ref.channel_id, "C0HARBOR")
        self.assertEqual(ref.message_ts, "1758067200.000100")
        self.assertEqual(ref.thread_ts, "1758067200.000100")
        self.assertTrue(ref.is_thread_parent)

    def test_reply_permalink_uses_the_thread_timestamp(self):
        ref = parse_slack_permalink(
            "https://example.slack.com/archives/C0HARBOR/p1758067800000300"
            "?thread_ts=1758067200.000100&cid=C0HARBOR"
        )
        assert ref is not None
        self.assertEqual(ref.thread_ts, "1758067200.000100")
        self.assertEqual(ref.message_ts, "1758067800.000300")
        self.assertFalse(ref.is_thread_parent)

    def test_cid_wins_over_the_path_channel(self):
        ref = parse_slack_permalink(
            "https://example.slack.com/archives/C0OTHER/p1758067200000100?cid=C0HARBOR"
        )
        assert ref is not None
        self.assertEqual(ref.channel_id, "C0HARBOR")

    def test_angle_wrapped_permalink(self):
        ref = parse_slack_permalink(
            "<https://example.slack.com/archives/C0HARBOR/p1758067200000100>"
        )
        self.assertIsNotNone(ref)

    def test_non_slack_url_is_not_a_permalink(self):
        self.assertIsNone(parse_slack_permalink("https://example.com/archives/C0/p1"))

    def test_slack_url_that_is_not_a_message(self):
        self.assertIsNone(
            parse_slack_permalink("https://example.slack.com/team/U0RIMURU")
        )


class ConfluenceLinkTests(unittest.TestCase):
    def test_page_id_from_the_long_form(self):
        self.assertEqual(
            parse_confluence_page_id(
                "https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242/Cutover+plan"
            ),
            "424242",
        )

    def test_page_id_from_viewpage_action(self):
        self.assertEqual(
            parse_confluence_page_id(
                "https://example.atlassian.net/wiki/pages/viewpage.action?pageId=424242"
            ),
            "424242",
        )

    def test_short_link_has_no_page_id(self):
        self.assertIsNone(
            parse_confluence_page_id("https://example.atlassian.net/wiki/x/AbCdEf")
        )

    def test_recognised_by_configured_base_url(self):
        self.assertTrue(
            looks_like_confluence(
                "https://wiki.example.com/wiki/spaces/H/pages/1/T",
                base_url="https://wiki.example.com",
            )
        )

    def test_recognised_by_atlassian_host_without_config(self):
        self.assertTrue(
            looks_like_confluence("https://example.atlassian.net/wiki/spaces/H/pages/1/T")
        )

    def test_an_unrelated_url_is_not_confluence(self):
        self.assertFalse(looks_like_confluence("https://example.com/harbor/runbook"))


class ForwardedPermalinkTests(unittest.TestCase):
    ORIGINAL = "https://example.slack.com/archives/C0OTHER/p1758067200000100"

    def test_a_forward_gives_up_the_original(self):
        message = {
            "text": "",
            "attachments": [{"from_url": self.ORIGINAL, "author_id": "U0HAKUROU"}],
        }
        self.assertEqual(forwarded_permalink(message), self.ORIGINAL)

    def test_an_ordinary_message_is_not_a_forward(self):
        self.assertIsNone(forwarded_permalink({"text": "Can we move the cutover?"}))

    def test_an_unfurled_web_link_is_not_a_forward(self):
        message = {
            "text": "the runbook",
            "attachments": [{"from_url": "https://example.com/harbor/runbook"}],
        }
        self.assertIsNone(forwarded_permalink(message))


if __name__ == "__main__":
    unittest.main()


class ExtractLinksTests(unittest.TestCase):
    def test_wrapped_and_bare_links_in_order(self):
        text = "see <https://a.example.com/1|the page> then https://b.example.com/2."
        self.assertEqual(
            extract_links(text), ["https://a.example.com/1", "https://b.example.com/2"]
        )

    def test_a_repeat_is_kept_once(self):
        text = "<https://a.example.com/1> and https://a.example.com/1"
        self.assertEqual(extract_links(text), ["https://a.example.com/1"])

    def test_slack_escaped_ampersands_are_undone(self):
        text = "<https://a.example.com/x?a=1&amp;b=2>"
        self.assertEqual(extract_links(text), ["https://a.example.com/x?a=1&b=2"])

    def test_mentions_and_non_web_links_are_not_links(self):
        self.assertEqual(extract_links("<@U0RIMURU> <mailto:a@example.com> <#C0HARBOR>"), [])
