import os
import shutil
import sys
import unittest
from pathlib import Path

from daikenja_bot.commands import JUDGEMENT, SUMMARY
from daikenja_bot.config import ClaudeConfig, parse_config
from daikenja_bot.prompts import END_SENTINEL, START_SENTINEL, UNAVAILABLE_TOKEN
from daikenja_bot.runner import (
    RunnerError,
    build_argv,
    resolve_command,
    run_command,
    scrubbed_env,
)
from daikenja_bot.subject import THREAD, Subject

from .fakes import FakeRunner, make_config

SUBJECT = Subject(kind=THREAD, label="#harbor-rollout, 4 messages", body="[1] hakurou: hi")


class ScrubbedEnvTests(unittest.TestCase):
    def test_the_configured_token_variables_are_removed(self):
        config = make_config()
        env = scrubbed_env(
            config,
            {"SLACK_BOT_TOKEN": "a", "SLACK_APP_TOKEN": "b", "PATH": "/usr/bin"},
        )
        self.assertNotIn("SLACK_BOT_TOKEN", env)
        self.assertNotIn("SLACK_APP_TOKEN", env)
        self.assertEqual(env["PATH"], "/usr/bin")

    def test_every_slack_variable_goes_not_just_the_configured_ones(self):
        config = make_config()
        env = scrubbed_env(config, {"SLACK_SIGNING_SECRET": "s", "SLACKWARE": "x"})
        self.assertEqual(env, {})

    def test_a_renamed_token_variable_is_still_removed(self):
        config = parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU", "bot_token_env": "MY_TOKEN"},
            }
        )
        env = scrubbed_env(config, {"MY_TOKEN": "a", "HOME": "/home/rimuru"})
        self.assertNotIn("MY_TOKEN", env)
        self.assertIn("HOME", env)

    def test_the_confluence_token_is_removed_when_configured(self):
        config = parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU"},
                "confluence": {
                    "base_url": "https://example.atlassian.net",
                    "email": "rimuru@example.com",
                    "token_env": "WIKI_TOKEN",
                },
            }
        )
        env = scrubbed_env(config, {"WIKI_TOKEN": "a", "LANG": "C"})
        self.assertNotIn("WIKI_TOKEN", env)
        self.assertIn("LANG", env)

    def test_unrelated_variables_are_left_alone(self):
        config = make_config()
        env = scrubbed_env(config, {"ANTHROPIC_API_KEY": "k", "PATH": "/bin"})
        self.assertEqual(env, {"ANTHROPIC_API_KEY": "k", "PATH": "/bin"})


class BuildArgvTests(unittest.TestCase):
    def test_the_default_command_line(self):
        argv = build_argv(make_config())
        self.assertEqual(argv[0], "claude")
        self.assertIn("-p", argv)
        self.assertIn("--permission-prompts", argv)
        self.assertEqual(argv[argv.index("--permission-prompts") + 1], "none")
        self.assertEqual(argv[argv.index("--allowedTools") + 1], "Read,Glob,Grep")

    def test_no_writing_tool_is_allowed_by_default(self):
        tools = build_argv(make_config())[
            build_argv(make_config()).index("--allowedTools") + 1
        ]
        for forbidden in ("Bash", "Write", "Edit", "WebFetch"):
            self.assertNotIn(forbidden, tools)

    def test_no_system_prompt_is_appended(self):
        # Tried and reverted: telling the session it has no reader made it
        # stop invoking the skill and answer in its own voice instead. The
        # block extraction in prompts.py handles the register leak.
        self.assertNotIn("--append-system-prompt", build_argv(make_config()))

    def test_optional_flags_are_only_added_when_set(self):
        argv = build_argv(make_config())
        self.assertNotIn("--model", argv)
        self.assertNotIn("--plugin-dir", argv)

    def test_model_plugin_dir_and_extra_args_are_passed_through(self):
        config = parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU"},
                "claude": {
                    "command": "/opt/claude",
                    "model": "claude-sonnet-5",
                    "plugin_dir": "/repo",
                    "extra_args": ["--verbose"],
                },
            }
        )
        argv = build_argv(config)
        self.assertEqual(argv[0], "/opt/claude")
        self.assertEqual(argv[argv.index("--model") + 1], "claude-sonnet-5")
        self.assertEqual(argv[argv.index("--plugin-dir") + 1], "/repo")
        self.assertEqual(argv[-1], "--verbose")


class ResolveCommandTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which(os.path.basename(sys.executable)),
        "the interpreter's own name is not on PATH here",
    )
    def test_a_bare_name_resolves_to_a_real_file(self):
        # On Windows this is the case that matters: a bare name only finds
        # `claude.CMD` through PATHEXT, which is why the function exists.
        resolved = resolve_command(os.path.basename(sys.executable))
        self.assertTrue(os.path.isfile(resolved))

    def test_a_full_path_comes_back_usable(self):
        self.assertTrue(os.path.isfile(resolve_command(sys.executable)))

    def test_a_missing_command_says_what_to_set(self):
        with self.assertRaises(RunnerError) as caught:
            resolve_command("daikenja-no-such-executable")
        self.assertIn("claude.command", str(caught.exception))


class WorkingDirTests(unittest.TestCase):
    def test_home_is_the_default(self):
        self.assertEqual(ClaudeConfig().resolved_working_dir(), Path.home())

    def test_a_configured_directory_wins(self):
        self.assertEqual(
            ClaudeConfig(working_dir="/srv/harbor").resolved_working_dir(),
            Path("/srv/harbor"),
        )


class RunCommandTests(unittest.TestCase):
    def test_the_answer_comes_back_without_the_sentinels(self):
        runner = FakeRunner(text=f"{START_SENTINEL}\nThread: four messages\n{END_SENTINEL}")
        answer = run_command(
            make_config(), SUMMARY, SUBJECT, environ={"PATH": "/bin"}, runner=runner
        )
        self.assertEqual(answer, "Thread: four messages")

    def test_the_subject_travels_on_stdin_not_in_argv(self):
        runner = FakeRunner(text=f"{START_SENTINEL}\nok\n{END_SENTINEL}")
        run_command(make_config(), JUDGEMENT, SUBJECT, environ={}, runner=runner)
        call = runner.calls[0]
        self.assertIn("[1] hakurou: hi", call["stdin"])
        self.assertNotIn("[1] hakurou: hi", " ".join(call["argv"]))

    def test_the_child_environment_is_scrubbed(self):
        runner = FakeRunner(text=f"{START_SENTINEL}\nok\n{END_SENTINEL}")
        run_command(
            make_config(),
            SUMMARY,
            SUBJECT,
            environ={"SLACK_BOT_TOKEN": "secret", "PATH": "/bin"},
            runner=runner,
        )
        self.assertNotIn("SLACK_BOT_TOKEN", runner.calls[0]["env"])

    def test_an_empty_subject_is_refused_before_the_model_runs(self):
        runner = FakeRunner()
        with self.assertRaises(RunnerError):
            run_command(
                make_config(),
                SUMMARY,
                Subject(kind=THREAD, label="empty", body="   "),
                environ={},
                runner=runner,
            )
        self.assertEqual(runner.calls, [])

    def test_a_failing_session_reports_its_last_stderr_line(self):
        runner = FakeRunner(text="", returncode=1, stderr="one\nnot logged in")
        with self.assertRaises(RunnerError) as caught:
            run_command(make_config(), SUMMARY, SUBJECT, environ={}, runner=runner)
        self.assertIn("not logged in", str(caught.exception))

    def test_a_silent_session_is_an_error_not_an_empty_post(self):
        runner = FakeRunner(text="   ")
        with self.assertRaises(RunnerError):
            run_command(make_config(), SUMMARY, SUBJECT, environ={}, runner=runner)

    def test_an_unloaded_skill_is_an_error_not_an_improvised_answer(self):
        runner = FakeRunner(
            text=f"{START_SENTINEL}\n{UNAVAILABLE_TOKEN}\n{END_SENTINEL}"
        )
        with self.assertRaises(RunnerError) as caught:
            run_command(make_config(), JUDGEMENT, SUBJECT, environ={}, runner=runner)
        message = str(caught.exception)
        self.assertIn("/daikenja:judgement", message)
        self.assertIn("plugin_dir", message)


if __name__ == "__main__":
    unittest.main()
