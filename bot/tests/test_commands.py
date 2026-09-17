import unittest

from daikenja_bot.commands import HELP, JUDGEMENT, SUMMARY, parse_command, strip_mentions

PERMALINK = "https://example.slack.com/archives/C0HARBOR/p1758067200000100"


class StripMentionsTests(unittest.TestCase):
    def test_removes_plain_and_labelled_mentions(self):
        text = "<@U0BOT> summary <@U0RIGURD|rigurd>"
        self.assertEqual(strip_mentions(text), "summary")

    def test_empty_text_is_empty(self):
        self.assertEqual(strip_mentions(""), "")
        self.assertEqual(strip_mentions(None), "")


class ParseCommandTests(unittest.TestCase):
    def test_bare_summary(self):
        command = parse_command("<@U0BOT> summary")
        self.assertEqual(command.name, SUMMARY)
        self.assertIsNone(command.argument)
        self.assertTrue(command.is_known)

    def test_bare_judgement(self):
        self.assertEqual(parse_command("<@U0BOT> judgement").name, JUDGEMENT)

    def test_case_and_punctuation_are_forgiven(self):
        for text in ("<@U0BOT> Judgement", "<@U0BOT> JUDGEMENT:", "<@U0BOT> /judgement"):
            with self.subTest(text=text):
                self.assertEqual(parse_command(text).name, JUDGEMENT)

    def test_link_argument_is_unwrapped(self):
        command = parse_command(
            "<@U0BOT> judgement <https://example.slack.com/archives/C0HARBOR/p1758067200000100>"
        )
        self.assertEqual(command.name, JUDGEMENT)
        self.assertEqual(
            command.argument,
            "https://example.slack.com/archives/C0HARBOR/p1758067200000100",
        )

    def test_labelled_link_argument_keeps_only_the_url(self):
        command = parse_command(
            "<@U0BOT> summary <https://example.com/page|the page>"
        )
        self.assertEqual(command.argument, "https://example.com/page")

    def test_mention_after_the_command_does_not_become_the_argument(self):
        command = parse_command("<@U0BOT> summary <@U0RIGURD>")
        self.assertIsNone(command.argument)

    def test_no_text_is_help(self):
        command = parse_command("<@U0BOT>")
        self.assertEqual(command.name, HELP)
        self.assertIsNone(command.unknown_word)
        self.assertFalse(command.is_known)

    def test_unknown_word_is_help_and_is_reported(self):
        command = parse_command("<@U0BOT> ledger please")
        self.assertEqual(command.name, HELP)
        self.assertEqual(command.unknown_word, "ledger")


class ProjectArgumentTests(unittest.TestCase):
    def test_project_keyword_takes_the_next_token_as_the_key(self):
        command = parse_command("<@U0BOT> judgement project sol-tokenization-service")
        self.assertEqual(command.name, JUDGEMENT)
        self.assertEqual(command.project, "sol-tokenization-service")
        self.assertIsNone(command.argument)

    def test_a_link_may_follow_the_key(self):
        command = parse_command(f"<@U0BOT> judgement project harbor <{PERMALINK}>")
        self.assertEqual(command.project, "harbor")
        self.assertEqual(command.argument, PERMALINK)

    def test_summary_takes_it_too(self):
        command = parse_command("<@U0BOT> summary project harbor")
        self.assertEqual(command.name, SUMMARY)
        self.assertEqual(command.project, "harbor")

    def test_the_keyword_is_matched_whatever_the_case(self):
        command = parse_command("<@U0BOT> judgement Project harbor")
        self.assertEqual(command.project, "harbor")

    def test_the_key_itself_is_kept_as_typed(self):
        command = parse_command("<@U0BOT> judgement project Harbor-Rollout")
        self.assertEqual(command.project, "Harbor-Rollout")

    def test_the_keyword_with_no_key_is_usage(self):
        command = parse_command("<@U0BOT> judgement project")
        self.assertEqual(command.name, HELP)
        self.assertIsNone(command.unknown_word)

    def test_a_link_alone_carries_no_project(self):
        command = parse_command(f"<@U0BOT> judgement <{PERMALINK}>")
        self.assertEqual(command.argument, PERMALINK)
        self.assertIsNone(command.project)


if __name__ == "__main__":
    unittest.main()
