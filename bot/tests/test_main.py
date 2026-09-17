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

from daikenja_bot.__main__ import build_parser, configure_logging, main, read_items
from daikenja_bot.digest import DigestError


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


class DigestArgumentTests(unittest.TestCase):
    def test_the_listener_is_the_default(self):
        args = build_parser().parse_args([])
        self.assertIsNone(args.digest)
        self.assertFalse(args.dry_run)

    def test_a_digest_can_be_asked_for_dry(self):
        args = build_parser().parse_args(["--digest", "items.json", "--dry-run"])
        self.assertEqual(args.digest, "items.json")
        self.assertTrue(args.dry_run)

    def test_a_dry_run_on_its_own_is_refused(self):
        # It would otherwise start the listener and silently ignore the flag,
        # which reads exactly like a digest that produced nothing.
        with _CleanRoot():
            self.assertEqual(main(["--dry-run"]), 2)

    def test_items_are_read_from_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "items.json"
            target.write_text('[{"summary": "x"}]', encoding="utf-8")
            self.assertEqual(read_items(str(target)), '[{"summary": "x"}]')

    def test_a_missing_item_file_says_where_it_looked(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "nothing.json")
            with self.assertRaises(DigestError) as caught:
                read_items(missing)
            self.assertIn(missing, str(caught.exception))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
