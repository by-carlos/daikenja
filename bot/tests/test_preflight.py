import tempfile
import unittest
from pathlib import Path

from daikenja_bot import preflight
from daikenja_bot.config import parse_config
from daikenja_bot.preflight import SkillReport, parse_skills

from .fakes import make_config

DETAILS_OUTPUT = """\
daikenja 0.9.1
  Description: Skills for reading threads and documents.
  Source: daikenja@carlos-plugins

Component inventory
  Skills (3)  compose, thread, project-log
  Agents (0)
  Hooks (0)
"""

DETAILS_WITH_VERDICT = DETAILS_OUTPUT.replace(
    "Skills (3)  compose, thread, project-log",
    "Skills (4)  compose, thread, verdict, project-log",
)


def responder(returncode: int, output: str, recorder: list | None = None):
    def details(argv, env):
        if recorder is not None:
            recorder.append({"argv": argv, "env": env})
        return returncode, output

    return details


class ParseSkillsTests(unittest.TestCase):
    def test_the_inventory_line_is_read(self):
        self.assertEqual(
            parse_skills(DETAILS_OUTPUT), frozenset({"compose", "thread", "project-log"})
        )

    def test_a_missing_line_is_undetermined_not_empty(self):
        self.assertIsNone(parse_skills("daikenja 0.9.1\n  Description: none\n"))

    def test_empty_output_is_undetermined(self):
        self.assertIsNone(parse_skills(""))


class ReportTests(unittest.TestCase):
    def test_a_complete_install_disables_nothing(self):
        report = SkillReport(
            available=frozenset({"thread", "verdict"}), source="the installed plugin"
        )
        self.assertEqual(report.missing(), {})
        self.assertTrue(report.determined)

    def test_a_missing_verdict_disables_only_verdict(self):
        report = SkillReport(available=frozenset({"thread"}), source="the installed plugin")
        missing = report.missing()
        self.assertEqual(set(missing), {"verdict"})
        self.assertIn("/daikenja:verdict", missing["verdict"])
        self.assertIn("plugin_dir", missing["verdict"])

    def test_an_undetermined_report_disables_nothing(self):
        report = SkillReport(available=None, source="the installed plugin")
        self.assertEqual(report.missing(), {})
        self.assertFalse(report.determined)


class CheckInstalledTests(unittest.TestCase):
    def test_the_installed_plugin_is_queried(self):
        calls: list = []
        report = preflight.check(
            make_config(),
            environ={"SLACK_BOT_TOKEN": "secret", "PATH": "/bin"},
            details=responder(0, DETAILS_WITH_VERDICT, calls),
        )
        self.assertEqual(report.missing(), {})
        self.assertEqual(calls[0]["argv"][1:], ["plugin", "details", "daikenja"])
        self.assertNotIn("SLACK_BOT_TOKEN", calls[0]["env"])

    def test_a_version_without_verdict_disables_that_command(self):
        report = preflight.check(
            make_config(), environ={}, details=responder(0, DETAILS_OUTPUT)
        )
        self.assertEqual(set(report.missing()), {"verdict"})

    def test_a_failing_cli_leaves_both_commands_enabled(self):
        with self.assertLogs("daikenja_bot.preflight", level="WARNING"):
            report = preflight.check(
                make_config(), environ={}, details=responder(1, "no such plugin")
            )
        self.assertFalse(report.determined)
        self.assertEqual(report.missing(), {})

    def test_a_crashing_cli_leaves_both_commands_enabled(self):
        def details(argv, env):
            raise OSError("cannot start")

        with self.assertLogs("daikenja_bot.preflight", level="WARNING"):
            report = preflight.check(make_config(), environ={}, details=details)
        self.assertFalse(report.determined)

    def test_a_missing_cli_leaves_both_commands_enabled(self):
        config = parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU"},
                "claude": {"command": "daikenja-no-such-executable"},
            }
        )
        with self.assertLogs("daikenja_bot.preflight", level="WARNING"):
            report = preflight.check(config, environ={})
        self.assertFalse(report.determined)


class CheckWorkingTreeTests(unittest.TestCase):
    def test_skills_are_read_off_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            for name in ("thread", "verdict"):
                (skills / name).mkdir(parents=True)
                (skills / name / "SKILL.md").write_text("---\n", encoding="utf-8")
            (skills / "not-a-skill").mkdir()
            config = parse_config(
                {
                    "slack": {"owner_user_id": "U0RIMURU"},
                    "claude": {"plugin_dir": tmp},
                }
            )
            report = preflight.check(config, environ={})
            self.assertEqual(report.available, frozenset({"thread", "verdict"}))
            self.assertEqual(report.missing(), {})

    def test_a_directory_with_no_skills_folder_is_undetermined(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = parse_config(
                {
                    "slack": {"owner_user_id": "U0RIMURU"},
                    "claude": {"plugin_dir": tmp},
                }
            )
            self.assertFalse(preflight.check(config, environ={}).determined)

    def test_this_repository_has_both_skills(self):
        repo_root = Path(__file__).resolve().parents[2]
        config = parse_config(
            {
                "slack": {"owner_user_id": "U0RIMURU"},
                "claude": {"plugin_dir": str(repo_root)},
            }
        )
        report = preflight.check(config, environ={})
        self.assertEqual(report.missing(), {})
        assert report.available is not None
        self.assertIn("thread", report.available)
        self.assertIn("verdict", report.available)


if __name__ == "__main__":
    unittest.main()
