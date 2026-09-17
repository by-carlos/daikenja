import unittest

from daikenja_bot.mrkdwn import (
    MAX_MESSAGE_CHARS,
    TRUNCATION_NOTE,
    escape_entities,
    to_mrkdwn,
    truncate,
)


class EscapeTests(unittest.TestCase):
    def test_ampersand_is_escaped_once(self):
        self.assertEqual(escape_entities("a & <b>"), "a &amp; &lt;b&gt;")


class ConversionTests(unittest.TestCase):
    def test_double_asterisk_bold_becomes_single(self):
        self.assertEqual(to_mrkdwn("**Ledger:** nothing"), "*Ledger:* nothing")

    def test_underscore_bold_becomes_single_asterisk(self):
        self.assertEqual(to_mrkdwn("__certain__"), "*certain*")

    def test_single_asterisk_italic_becomes_underscore(self):
        self.assertEqual(to_mrkdwn("an *emphasised* word"), "an _emphasised_ word")

    def test_headings_become_bold_lines(self):
        self.assertEqual(to_mrkdwn("## AI review summary"), "*AI review summary*")

    def test_bullets_become_dots_and_keep_their_indent(self):
        converted = to_mrkdwn("- one\n  - nested")
        self.assertEqual(converted, "• one\n  • nested")

    def test_numbered_lists_are_left_alone(self):
        self.assertEqual(to_mrkdwn("1. first\n2. second"), "1. first\n2. second")

    def test_markdown_link_becomes_slack_link(self):
        self.assertEqual(
            to_mrkdwn("see [the runbook](https://example.com/runbook)"),
            "see <https://example.com/runbook|the runbook>",
        )

    def test_link_url_is_not_escaped(self):
        converted = to_mrkdwn("[q](https://example.com/a?b=1&c=2)")
        self.assertIn("https://example.com/a?b=1&c=2", converted)
        self.assertNotIn("&amp;", converted)

    def test_bare_angle_url_keeps_working(self):
        self.assertEqual(
            to_mrkdwn("<https://example.com/x>"), "<https://example.com/x>"
        )

    def test_prose_angle_brackets_are_escaped(self):
        self.assertEqual(to_mrkdwn("a < b > c"), "a &lt; b &gt; c")

    def test_inline_code_survives_and_is_escaped(self):
        self.assertEqual(to_mrkdwn("run `a < b`"), "run `a &lt; b`")

    def test_asterisks_inside_inline_code_are_not_converted(self):
        self.assertEqual(to_mrkdwn("`**not bold**`"), "`**not bold**`")

    def test_fenced_block_content_is_preserved(self):
        converted = to_mrkdwn("```\nD-003 -> frozen\n**kept**\n```")
        self.assertEqual(converted, "```\nD-003 -&gt; frozen\n**kept**\n```")

    def test_unbalanced_fence_is_closed(self):
        self.assertTrue(to_mrkdwn("```\nunclosed").endswith("```"))

    def test_horizontal_rule_is_dropped(self):
        self.assertEqual(to_mrkdwn("a\n\n---\n\nb"), "a\n\n\nb")

    def test_blockquote_marker_survives_escaping(self):
        self.assertEqual(to_mrkdwn("> quoted"), "> quoted")

    def test_empty_input(self):
        self.assertEqual(to_mrkdwn(""), "")

    def test_a_whole_judgement_message(self):
        source = (
            "⚖️ **Verdict**\n"
            "The proposed Friday cutover contradicts the Monday cutover "
            "decision.\n"
            "\n"
            "\U0001F4D2 **Ledger -- harbor**\n"
            "- **Monday cutover** (D-001) -- the thread proposes Friday "
            "instead. _certain · ledger_\n"
            "\n"
            "\U0001F50D **Basis**\n"
            "- **Step 4 at volume** -- never run at volume. Source: "
            "[the harbor runbook](https://example.com/harbor/runbook). "
            "_likely · general knowledge_\n"
            "\n"
            "\U0001F6A7 **Not checked**\n"
            "- The linked runbook itself.\n"
        )
        converted = to_mrkdwn(source)
        self.assertIn("*Verdict*", converted)
        self.assertIn("*Ledger -- harbor*", converted)
        self.assertIn("*Basis*", converted)
        self.assertIn("*Not checked*", converted)
        self.assertIn("• ", converted)
        self.assertIn("<https://example.com/harbor/runbook|the harbor runbook>", converted)
        self.assertIn("_certain · ledger_", converted)
        self.assertIn("_likely · general knowledge_", converted)
        self.assertIn("⚖️", converted)
        self.assertIn("\U0001F4D2", converted)
        self.assertNotIn("**", converted)


class TruncateTests(unittest.TestCase):
    def test_short_text_is_untouched(self):
        self.assertEqual(truncate("short"), "short")

    def test_long_text_is_cut_and_says_so(self):
        cut = truncate("x" * (MAX_MESSAGE_CHARS + 500))
        self.assertLessEqual(len(cut), MAX_MESSAGE_CHARS)
        self.assertTrue(cut.endswith(TRUNCATION_NOTE))

    def test_cut_prefers_a_line_break(self):
        body = ("line\n" * 20_000)[: MAX_MESSAGE_CHARS + 200]
        cut = truncate(body)
        self.assertTrue(cut.replace(TRUNCATION_NOTE, "").endswith("line"))


if __name__ == "__main__":
    unittest.main()
