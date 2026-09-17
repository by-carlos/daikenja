"""Start the bot: ``python -m daikenja_bot``.

``--check`` validates the config and the credentials and exits, which is the
first thing to run after editing ``bot.yaml`` -- it catches a missing token
or a typo in a key without opening a connection to Slack.

``--log-file`` is what makes an unattended run readable: started from a
scheduled task or a service manager there is no console for the log to reach,
and without it a bot that failed to start leaves nothing behind to say why.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import __version__, preflight
from .app import resolve_tokens, run
from .commands import KNOWN_COMMANDS
from .config import DEFAULT_CONFIG_PATH, ConfigError, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="daikenja_bot",
        description="Daikenja's personal-instance Slack bot.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help=f"path to bot.yaml (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the config and the credentials, then exit",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="DEBUG, INFO, WARNING or ERROR (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="append the log to this file instead of the console, rotating it "
        "at 1 MB. Required for an unattended run, which has no console.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def configure_logging(level_name: str, log_file: str | None) -> None:
    """Send the log to the console, or to a rotating file for a service run."""
    handlers: list[logging.Handler] | None = None
    if log_file:
        path = Path(log_file).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers = [
            RotatingFileHandler(
                path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
        ]
    logging.basicConfig(
        level=getattr(logging, level_name.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=handlers,
    )


def _fail(message: str, *, also_log: bool) -> int:
    """Say why it will not start, somewhere the person will actually see it.

    Stderr is the console's copy. An unattended run has no console, so the
    same line goes to the log file -- and only then, or a person watching a
    terminal would read every failure twice.
    """
    print(message, file=sys.stderr)
    if also_log:
        logging.getLogger("daikenja_bot").error("%s", message)
    return 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level, args.log_file)
    logged = bool(args.log_file)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        return _fail(f"config: {exc}", also_log=logged)

    if args.check:
        try:
            resolve_tokens(config, os.environ)
        except ConfigError as exc:
            return _fail(f"credentials: {exc}", also_log=logged)
        print(f"config OK: {config.source_path}")
        print(f"  owner:      {config.slack.owner_user_id}")
        print(
            "  channels:   "
            + (
                ", ".join(config.slack.allowed_channels)
                if config.slack.allowed_channels
                else "every channel the bot is invited to"
            )
        )
        print(
            "  strangers:  "
            + (
                "told privately why, in an ephemeral reply"
                if config.slack.unauthorized_message
                else "ignored in silence"
            )
        )
        print(f"  claude:     {config.claude.command}")
        model = config.claude.model or "your account's default"
        effort = config.claude.effort or "your account's default"
        print(f"  model:      {model} at {effort} effort")
        print(f"  tools:      {', '.join(config.claude.allowed_tools)}")
        print(f"  working in: {config.claude.resolved_working_dir()}")
        print(
            "  confluence: "
            + (config.confluence.base_url if config.confluence else "not configured")
        )

        report = preflight.check(config, environ=dict(os.environ))
        unavailable = report.missing()
        if not report.determined:
            print(f"  commands:   unknown -- could not read {report.source}")
        else:
            for command in sorted(KNOWN_COMMANDS):
                state = "unavailable" if command in unavailable else "ready"
                print(f"  {command + ':':12}{state}")
        for command in sorted(unavailable):
            print(f"\n{unavailable[command]}", file=sys.stderr)
        return 0

    try:
        run(config)
    except ConfigError as exc:
        return _fail(f"credentials: {exc}", also_log=logged)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
