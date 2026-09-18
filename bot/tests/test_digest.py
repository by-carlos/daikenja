"""The digest layer: reading a feeder's list, and posting one message.

The grouping itself is not tested here and cannot be -- it happens inside the
headless session, against the user's own project cards and ledgers. What is
testable is everything around it: that a feeder's list is read the way the
contract says, that a broken list is refused instead of half-digested, that
the block handed to the session carries every field, and that what comes back
reaches the owner's DM as Slack's dialect rather than as markdown.
"""

from __future__ import annotations

import json
import unittest

from daikenja_bot.digest import (
    DigestError,
    ItemList,
    build_digest,
    build_subject,
    parse_items,
    post_digest,
    render_items,
)
from daikenja_bot.prompts import END_SENTINEL, START_SENTINEL
from daikenja_bot.slack_io import SlackIO
from daikenja_bot.subject import ITEMS

from .fakes import POSTED_TS, FakeRunner, FakeSlackClient, make_config

ONE_ITEM = [
    {
        "ts": "2026-09-18T08:14:00Z",
        "channel": "#harbor-rollout",
        "sender": "@diablo",
        "bucket": "fyi",
        "topic": "harbor-rollout",
        "permalink": "https://example.com/archives/C0HARBOR/p1",
        "summary": "The 30-day replica window may not survive the cutover move.",
    }
]


def answered(text: str) -> FakeRunner:
    """A session that produced `text` between the sentinels."""
    return FakeRunner(text=f"thinking out loud\n{START_SENTINEL}\n{text}\n{END_SENTINEL}\n")


class ParseTests(unittest.TestCase):
    def test_a_plain_array_is_read(self):
        parsed = parse_items(json.dumps(ONE_ITEM))
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed.items[0]["channel"], "#harbor-rollout")

    def test_an_items_key_is_read_too(self):
        parsed = parse_items(json.dumps({"items": ONE_ITEM, "generated_at": "x"}))
        self.assertEqual(len(parsed), 1)

    def test_a_feeders_own_fields_are_dropped_not_refused(self):
        entry = dict(ONE_ITEM[0], score=0.91, message_id="abc", rubric="p2")
        parsed = parse_items(json.dumps([entry]))
        self.assertNotIn("score", parsed.items[0])
        self.assertEqual(parsed.items[0]["summary"], ONE_ITEM[0]["summary"])

    def test_the_block_field_names_are_accepted_as_aliases(self):
        entry = {
            "when": "2026-09-18T08:14:00Z",
            "from": "@diablo",
            "link": "https://example.com/p1",
            "project": "harbor-rollout",
            "summary": "Something happened.",
        }
        item = parse_items(json.dumps([entry])).items[0]
        self.assertEqual(item["ts"], "2026-09-18T08:14:00Z")
        self.assertEqual(item["sender"], "@diablo")
        self.assertEqual(item["permalink"], "https://example.com/p1")
        self.assertEqual(item["topic"], "harbor-rollout")

    def test_a_numeric_timestamp_survives_as_text(self):
        item = parse_items(json.dumps([{"ts": 1726647240, "summary": "x"}])).items[0]
        self.assertEqual(item["ts"], "1726647240")

    def test_an_item_with_no_summary_is_skipped_not_fatal(self):
        parsed = parse_items(json.dumps([{"channel": "#x"}, ONE_ITEM[0]]))
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed.skipped, ("Item 1 has no summary. Skipped.",))

    def test_empty_input_is_refused(self):
        with self.assertRaises(DigestError):
            parse_items("   ")

    def test_an_empty_list_is_refused(self):
        with self.assertRaises(DigestError):
            parse_items("[]")

    def test_broken_json_names_where_it_broke(self):
        with self.assertRaises(DigestError) as caught:
            parse_items('[{"summary": "x",}]')
        self.assertIn("line", str(caught.exception))

    def test_a_list_of_strings_is_refused(self):
        with self.assertRaises(DigestError) as caught:
            parse_items('["just a line"]')
        self.assertIn("item 1", str(caught.exception))

    def test_a_field_that_is_not_text_is_refused(self):
        with self.assertRaises(DigestError) as caught:
            parse_items(json.dumps([{"summary": "x", "channel": ["#a", "#b"]}]))
        self.assertIn("channel", str(caught.exception))


class RenderTests(unittest.TestCase):
    def test_every_field_reaches_the_block_under_its_label(self):
        block = render_items(parse_items(json.dumps(ONE_ITEM)))
        self.assertIn("--- ITEM 1 ---", block)
        self.assertIn("when: 2026-09-18T08:14:00Z", block)
        self.assertIn("channel: #harbor-rollout", block)
        self.assertIn("from: @diablo", block)
        self.assertIn("bucket: fyi", block)
        self.assertIn("topic: harbor-rollout", block)
        self.assertIn("link: https://example.com/archives/C0HARBOR/p1", block)
        self.assertIn("summary: The 30-day replica window", block)

    def test_an_absent_field_leaves_no_empty_label(self):
        block = render_items(parse_items(json.dumps([{"summary": "Just this."}])))
        self.assertNotIn("channel:", block)
        self.assertNotIn("bucket:", block)

    def test_the_subject_says_how_many_items_it_holds(self):
        subject = build_subject(parse_items(json.dumps(ONE_ITEM * 3)))
        self.assertEqual(subject.kind, ITEMS)
        self.assertIn("3 items", subject.label)
        self.assertFalse(subject.is_empty)

    def test_one_item_is_not_called_items(self):
        self.assertIn("1 item ", build_subject(parse_items(json.dumps(ONE_ITEM))).label)


class BuildTests(unittest.TestCase):
    def test_the_session_is_asked_for_the_digest_skill(self):
        runner = answered("**Digest** -- 1 item")
        build_digest(
            make_config(),
            parse_items(json.dumps(ONE_ITEM)),
            environ={},
            runner=runner,
        )
        instruction = runner.calls[0]["argv"][-1]
        self.assertIn("/daikenja:digest", instruction)
        self.assertIn("direct message", instruction)

    def test_the_shape_names_the_configured_groups_between_projects_and_unmatched(self):
        # The skill reads `digest.groups` from daikenja.yaml itself; the bot
        # only has to ask for the shape that includes them, in that order.
        runner = answered("**Digest** -- 1 item")
        build_digest(
            make_config(),
            parse_items(json.dumps(ONE_ITEM)),
            environ={},
            runner=runner,
        )
        instruction = runner.calls[0]["argv"][-1]
        projects = instruction.index("group per project")
        groups = instruction.index("configured digest group")
        unmatched = instruction.index("Unmatched")
        self.assertLess(projects, groups)
        self.assertLess(groups, unmatched)

    def test_the_items_travel_on_standard_input(self):
        runner = answered("**Digest** -- 1 item")
        build_digest(
            make_config(),
            parse_items(json.dumps(ONE_ITEM)),
            environ={},
            runner=runner,
        )
        self.assertIn("--- ITEM 1 ---", runner.calls[0]["stdin"])

    def test_the_credentials_never_reach_the_session(self):
        runner = answered("**Digest** -- 1 item")
        build_digest(
            make_config(),
            parse_items(json.dumps(ONE_ITEM)),
            environ={"SLACK_BOT_TOKEN": "xoxb-secret", "PATH": "/usr/bin"},
            runner=runner,
        )
        self.assertNotIn("SLACK_BOT_TOKEN", runner.calls[0]["env"])
        self.assertEqual(runner.calls[0]["env"]["PATH"], "/usr/bin")

    def test_only_the_deliverable_comes_back(self):
        runner = answered("**Digest** -- 1 item, 1 project")
        text = build_digest(
            make_config(),
            parse_items(json.dumps(ONE_ITEM)),
            environ={},
            runner=runner,
        )
        self.assertEqual(text, "**Digest** -- 1 item, 1 project")


class PostTests(unittest.TestCase):
    def _post(self, text: str) -> dict:
        client = FakeSlackClient()
        timestamp = post_digest(SlackIO(client), make_config(), text)
        self.assertEqual(timestamp, POSTED_TS)
        return client.posted[0]

    def test_it_goes_to_the_owners_dm_with_no_thread(self):
        sent = self._post("**Digest** -- 1 item")
        self.assertEqual(sent["channel"], "U0RIMURU")
        self.assertNotIn("thread_ts", sent)

    def test_markdown_is_converted_to_slacks_dialect(self):
        sent = self._post(
            "**Digest** -- 1 item\n\n- #harbor-rollout -- "
            "[The replica window may move](https://example.com/p1)"
        )
        self.assertIn("*Digest*", sent["text"])
        self.assertNotIn("**Digest**", sent["text"])
        self.assertIn("<https://example.com/p1|The replica window may move>", sent["text"])
        self.assertIn("• #harbor-rollout", sent["text"])

    def test_a_long_digest_is_cut_rather_than_refused(self):
        sent = self._post("word " * 20_000)
        self.assertLess(len(sent["text"]), 40_000)
        self.assertIn("cut here", sent["text"])

    def test_nothing_is_unfurled(self):
        sent = self._post("[a link](https://example.com/p1)")
        self.assertFalse(sent["unfurl_links"])
        self.assertFalse(sent["unfurl_media"])


class ItemListTests(unittest.TestCase):
    def test_an_item_list_reports_its_own_length(self):
        self.assertEqual(len(ItemList(items=({"summary": "a"}, {"summary": "b"}))), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
