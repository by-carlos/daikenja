"""The entry point's own behaviour: argument parsing and where the log goes.

`--log-file` is the one piece here worth a test. It exists for a run with no
console, so a mistake in it produces exactly no evidence -- which is the
failure it was added to prevent.
"""

from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from daikenja_bot.__main__ import build_parser, configure_logging, project_data_line


class _CleanRoot:
    """basicConfig does nothing when the root logger already has handlers."""

    def __enter__(self) -> None:
        root = logging.getLogger()
        self._saved = list(root.handlers)
        self._level = root.level
        root.handlers.clear()

    def __exit__(self, *exc: object) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers[:] = self._saved
        root.setLevel(self._level)


class ParserTests(unittest.TestCase):
    def test_the_log_goes_to_the_console_by_default(self):
        self.assertIsNone(build_parser().parse_args([]).log_file)

    def test_check_and_a_config_path_can_be_combined(self):
        args = build_parser().parse_args(["--check", "--config", "x.yaml"])
        self.assertTrue(args.check)
        self.assertEqual(args.config, "x.yaml")


class LogFileTests(unittest.TestCase):
    def test_a_log_file_is_written_and_its_directory_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "logs" / "bot.log"
            with _CleanRoot():
                configure_logging("INFO", str(target))
                logging.getLogger("daikenja_bot").info("listening")
            self.assertIn("listening", target.read_text(encoding="utf-8"))

    def test_an_unknown_level_falls_back_to_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "bot.log"
            with _CleanRoot():
                configure_logging("LOUD", str(target))
                self.assertEqual(logging.getLogger().level, logging.INFO)

    def test_debug_is_honoured(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "bot.log"
            with _CleanRoot():
                configure_logging("debug", str(target))
                self.assertEqual(logging.getLogger().level, logging.DEBUG)


class ProjectDataLineTests(unittest.TestCase):
    """`--check` names the projects a mention would get the fixed line for.

    Read from the files as they are, never from git: invented projects in a
    temporary directory stand in for the user's repositories.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _repo(self, name: str, files: dict[str, str]) -> str:
        repo = self.root / name
        for relative, text in files.items():
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        repo.mkdir(exist_ok=True)
        return repo.as_posix()

    def _config(self, body: str) -> Path:
        path = self.root / "daikenja.yaml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_projects_on_the_current_format_are_all_readable(self):
        harbor = self._repo(
            "harbor",
            {
                "DECISIONS.md": "<!-- decisions-format: 1 -->\n# Decisions\n",
                ".daikenja/open.md": "<!-- daikenja-open-format: 1 -->\n",
            },
        )
        config = self._config(f"projects:\n  harbor:\n    path: {harbor}\n")
        self.assertEqual(project_data_line(config), "1, all readable")

    def test_each_unreadable_state_is_named(self):
        ember = self._repo("ember", {".daikenja/ledger.md": "# old ledger\n"})
        beacon = self._repo(
            "beacon", {"DECISIONS.md": "<!-- decisions-format: 2 -->\n"}
        )
        harbor = self._repo("harbor", {})
        config = self._config(
            "projects:\n"
            f"  ember:\n    path: {ember}\n"
            f"  beacon:\n    paths:\n      - {harbor}\n      - {beacon}\n"
            "  atlas:\n    paths: []\n"
            f"  harbor:\n    path: {harbor}\n"
        )
        line = project_data_line(config)
        self.assertIn("ember (needs-migration)", line)
        self.assertIn("beacon (newer-format)", line)
        self.assertIn("atlas (needs-migration)", line)
        self.assertNotIn("harbor", line)

    def test_a_missing_daikenja_yaml_is_reported_not_raised(self):
        line = project_data_line(self.root / "absent.yaml")
        self.assertTrue(line.startswith("unknown -- no daikenja.yaml"))

    def test_no_projects_is_said_plainly(self):
        self.assertEqual(project_data_line(self._config("projects: {}\n")), "none registered")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
