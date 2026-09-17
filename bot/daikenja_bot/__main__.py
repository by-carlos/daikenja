"""Start the bot: ``python -m daikenja_bot``.

``--check`` validates the config and the credentials and exits, which is the
first thing to run after editing ``bot.yaml`` -- it catches a missing token
or a typo in a key without opening a connection to Slack.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from . import __version__
from .app import resolve_tokens, run
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
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"config: {exc}", file=sys.stderr)
        return 2

    if args.check:
        try:
            resolve_tokens(config, os.environ)
        except ConfigError as exc:
            print(f"credentials: {exc}", file=sys.stderr)
            return 2
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
        print(f"  claude:     {config.claude.command}")
        print(f"  tools:      {', '.join(config.claude.allowed_tools)}")
        print(f"  working in: {config.claude.resolved_working_dir()}")
        print(
            "  confluence: "
            + (config.confluence.base_url if config.confluence else "not configured")
        )
        return 0

    try:
        run(config)
    except ConfigError as exc:
        print(f"credentials: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
