import tempfile
import unittest
from pathlib import Path

import yaml

from daikenja_bot.config import (
    DEFAULT_ALLOWED_TOOLS,
    BotConfig,
    ClaudeConfig,
    ConfigError,
    SlackConfig,
    load_config,
    parse_config,
    resolve_secret,
    secret_env_names,
)

MINIMAL = {"slack": {"owner_user_id": "U0RIMURU"}}


class ParseTests(unittest.TestCase):
    def test_minimal_config_gets_the_defaults(self):
        config = parse_config(MINIMAL)
        self.assertEqual(config.slack.owner_user_id, "U0RIMURU")
        self.assertEqual(config.claude.command, "claude")
        self.assertEqual(config.claude.allowed_tools, DEFAULT_ALLOWED_TOOLS)
        self.assertEqual(config.claude.timeout_seconds, 300)
        self.assertEqual(config.claude.model, "claude-sonnet-5")
        self.assertEqual(config.claude.effort, "medium")
        self.assertIsNone(config.confluence)
        self.assertFalse(config.confluence_configured)

    def test_owner_is_required(self):
        with self.assertRaises(ConfigError) as caught:
            parse_config({"slack": {}})
        self.assertIn("owner_user_id", str(caught.exception))

    def test_empty_file_is_rejected(self):
        with self.assertRaises(ConfigError):
            parse_config(None)

    def test_a_list_at_the_top_level_is_rejected(self):
        with self.assertRaises(ConfigError):
            parse_config(["slack"])

    def test_a_single_string_becomes_a_one_item_list(self):
        config = parse_config(
            {"slack": {"owner_user_id": "U0RIMURU", "allowed_channels": "C0HARBOR"}}
        )
        self.assertEqual(config.slack.allowed_channels, ("C0HARBOR",))

    def test_allowed_tools_can_be_widened(self):
        config = parse_config(
            {**MINIMAL, "claude": {"allowed_tools": ["Read", "Glob", "Grep", "WebFetch"]}}
        )
        self.assertIn("WebFetch", config.claude.allowed_tools)

    def test_empty_allowed_tools_falls_back_to_the_default(self):
        config = parse_config({**MINIMAL, "claude": {"allowed_tools": []}})
        self.assertEqual(config.claude.allowed_tools, DEFAULT_ALLOWED_TOOLS)

    def test_timeout_must_be_a_positive_number(self):
        with self.assertRaises(ConfigError):
            parse_config({**MINIMAL, "claude": {"timeout_seconds": 0}})
        with self.assertRaises(ConfigError):
            parse_config({**MINIMAL, "claude": {"timeout_seconds": "soon"}})

    def test_effort_must_be_a_level_the_cli_accepts(self):
        # The level is not part of the model name; a config that spells it
        # that way should be caught at startup, not at the first mention.
        with self.assertRaises(ConfigError) as caught:
            parse_config({**MINIMAL, "claude": {"effort": "claude-sonnet-5-medium"}})
        self.assertIn("claude.effort", str(caught.exception))

    def test_effort_is_case_insensitive(self):
        config = parse_config({**MINIMAL, "claude": {"effort": "HIGH"}})
        self.assertEqual(config.claude.effort, "high")

    def test_an_empty_model_or_effort_unpins_them(self):
        config = parse_config({**MINIMAL, "claude": {"model": "", "effort": ""}})
        self.assertIsNone(config.claude.model)
        self.assertIsNone(config.claude.effort)

    def test_confluence_needs_both_keys(self):
        with self.assertRaises(ConfigError):
            parse_config(
                {**MINIMAL, "confluence": {"base_url": "https://example.atlassian.net"}}
            )

    def test_confluence_base_url_loses_its_trailing_slash(self):
        config = parse_config(
            {
                **MINIMAL,
                "confluence": {
                    "base_url": "https://example.atlassian.net/",
                    "email": "rimuru@example.com",
                },
            }
        )
        assert config.confluence is not None
        self.assertEqual(config.confluence.base_url, "https://example.atlassian.net")
        self.assertTrue(config.confluence_configured)

    def test_ack_reaction_can_be_switched_off(self):
        config = parse_config({"slack": {"owner_user_id": "U0RIMURU", "ack_reaction": None}})
        self.assertIsNone(config.slack.ack_reaction)

    def test_strangers_are_told_something_by_default(self):
        config = parse_config({"slack": {"owner_user_id": "U0RIMURU"}})
        assert config.slack.unauthorized_message is not None
        self.assertIn("{owner}", config.slack.unauthorized_message)

    def test_an_explicit_null_means_say_nothing(self):
        # Absence and null differ for this key, so it cannot be read with
        # `or` -- a default that survived `null` would be a surprise.
        config = parse_config(
            {"slack": {"owner_user_id": "U0RIMURU", "unauthorized_message": None}}
        )
        self.assertIsNone(config.slack.unauthorized_message)

    def test_a_custom_message_is_kept(self):
        config = parse_config(
            {
                "slack": {
                    "owner_user_id": "U0RIMURU",
                    "unauthorized_message": "  In beta, ask {owner}.  ",
                }
            }
        )
        self.assertEqual(config.slack.unauthorized_message, "In beta, ask {owner}.")

    def test_a_non_string_message_is_rejected(self):
        with self.assertRaises(ConfigError):
            parse_config(
                {"slack": {"owner_user_id": "U0RIMURU", "unauthorized_message": 42}}
            )

    def test_a_channel_allowlist_is_separable_from_the_user_one(self):
        slack = parse_config(
            {"slack": {"owner_user_id": "U0RIMURU", "allowed_channels": ["C0HARBOR"]}}
        ).slack
        self.assertTrue(slack.allows_user("U0RIMURU"))
        self.assertFalse(slack.allows_channel("C0OTHER"))
        self.assertFalse(slack.may_trigger("U0RIMURU", "C0OTHER"))


class LoadTests(unittest.TestCase):
    def test_a_missing_file_says_where_it_looked(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "bot.yaml"
            with self.assertRaises(ConfigError) as caught:
                load_config(missing)
            self.assertIn(str(missing), str(caught.exception))

    def test_broken_yaml_is_reported_as_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bot.yaml"
            path.write_text("slack: [unclosed\n", encoding="utf-8")
            with self.assertRaises(ConfigError) as caught:
                load_config(path)
            self.assertIn("does not parse as YAML", str(caught.exception))

    def test_a_good_file_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bot.yaml"
            path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
            config = load_config(path)
            self.assertEqual(config.source_path, path)

    def test_the_shipped_example_parses(self):
        example = Path(__file__).resolve().parents[1] / "bot.yaml.example"
        config = load_config(example)
        self.assertEqual(config.slack.owner_user_id, "U0EXAMPLEOWNER")
        self.assertEqual(config.claude.allowed_tools, ("Read", "Glob", "Grep"))
        self.assertIsNone(config.confluence)


class AllowlistTests(unittest.TestCase):
    def test_owner_only_by_default(self):
        slack = SlackConfig(owner_user_id="U0RIMURU")
        self.assertTrue(slack.may_trigger("U0RIMURU", "C0HARBOR"))
        self.assertFalse(slack.may_trigger("U0GOBTA", "C0HARBOR"))

    def test_the_owner_is_allowed_even_when_left_off_the_list(self):
        slack = SlackConfig(owner_user_id="U0RIMURU", allowed_users=("U0SHION",))
        self.assertTrue(slack.may_trigger("U0RIMURU", "C0HARBOR"))
        self.assertTrue(slack.may_trigger("U0SHION", "C0HARBOR"))
        self.assertFalse(slack.may_trigger("U0GOBTA", "C0HARBOR"))

    def test_channel_restriction_applies_to_the_owner_too(self):
        slack = SlackConfig(owner_user_id="U0RIMURU", allowed_channels=("C0HARBOR",))
        self.assertTrue(slack.may_trigger("U0RIMURU", "C0HARBOR"))
        self.assertFalse(slack.may_trigger("U0RIMURU", "C0ELSEWHERE"))

    def test_no_channel_list_means_every_channel(self):
        slack = SlackConfig(owner_user_id="U0RIMURU")
        self.assertTrue(slack.may_trigger("U0RIMURU", "C0ANYWHERE"))


class SecretTests(unittest.TestCase):
    def test_environment_comes_first(self):
        value = resolve_secret(
            label="token", env_name="TOKEN_X", inline="inline", environ={"TOKEN_X": " abc "}
        )
        self.assertEqual(value, "abc")

    def test_a_file_is_read_when_the_environment_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token"
            path.write_text("from-file\n", encoding="utf-8")
            value = resolve_secret(
                label="token", env_name="TOKEN_X", file_path=str(path), environ={}
            )
            self.assertEqual(value, "from-file")

    def test_an_empty_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token"
            path.write_text("\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                resolve_secret(label="token", file_path=str(path), environ={})

    def test_a_missing_file_is_an_error(self):
        with self.assertRaises(ConfigError):
            resolve_secret(label="token", file_path="/nowhere/at/all", environ={})

    def test_inline_is_the_last_resort(self):
        self.assertEqual(
            resolve_secret(label="token", env_name="TOKEN_X", inline="xyz", environ={}),
            "xyz",
        )

    def test_nothing_set_names_the_variable_to_export(self):
        with self.assertRaises(ConfigError) as caught:
            resolve_secret(label="the Slack bot token", env_name="TOKEN_X", environ={})
        self.assertIn("TOKEN_X", str(caught.exception))


class SecretEnvNameTests(unittest.TestCase):
    def test_slack_names_only_without_confluence(self):
        config = parse_config(MINIMAL)
        self.assertEqual(
            secret_env_names(config), ("SLACK_BOT_TOKEN", "SLACK_APP_TOKEN")
        )

    def test_confluence_name_is_included_when_configured(self):
        config = BotConfig(
            slack=SlackConfig(owner_user_id="U0RIMURU"),
            claude=ClaudeConfig(),
            confluence=parse_config(
                {
                    **MINIMAL,
                    "confluence": {
                        "base_url": "https://example.atlassian.net",
                        "email": "rimuru@example.com",
                        "token_env": "WIKI_TOKEN",
                    },
                }
            ).confluence,
        )
        self.assertIn("WIKI_TOKEN", secret_env_names(config))


if __name__ == "__main__":
    unittest.main()
