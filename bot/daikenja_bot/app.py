"""Socket Mode transport.

Socket Mode rather than the Events API because this is a personal instance:
it runs on a laptop or a home server with no public URL, and Socket Mode
needs neither an inbound port nor a certificate.

The listener does nothing but hand the event to a worker. Slack expects an
acknowledgement within three seconds and a headless session takes far longer
than that, so the work happens off the socket thread and the answer arrives
in the thread when it is ready.
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

from .config import BotConfig, resolve_secret
from .handler import Handler
from .slack_io import connect

log = logging.getLogger(__name__)

# One at a time. A headless session is expensive, and two of them racing on
# one machine makes both slower without making either more useful.
MAX_CONCURRENT_RUNS = 1


def resolve_tokens(config: BotConfig, environ: Mapping[str, str]) -> tuple[str, str]:
    """The bot token and the app-level token, or a message saying where to put them."""
    bot_token = resolve_secret(
        label="the Slack bot token (xoxb-)",
        env_name=config.slack.bot_token_env,
        file_path=config.slack.bot_token_file,
        inline=config.slack.bot_token,
        environ=dict(environ),
    )
    app_token = resolve_secret(
        label="the Slack app-level token (xapp-)",
        env_name=config.slack.app_token_env,
        file_path=config.slack.app_token_file,
        inline=config.slack.app_token,
        environ=dict(environ),
    )
    return bot_token, app_token


def run(config: BotConfig, environ: Mapping[str, str] | None = None) -> None:
    """Connect to Slack and answer mentions until the process is stopped."""
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler

    environ = os.environ if environ is None else environ
    bot_token, app_token = resolve_tokens(config, environ)

    slack = connect(bot_token)
    # The model layer reads the environment it is given, and `runner`
    # strips the credentials out of it. Pass the real one; it is scrubbed
    # at the point of use, where the config says which names to remove.
    handler = Handler(config, slack, environ=dict(environ))

    app = App(token=bot_token)
    pool = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_RUNS, thread_name_prefix="daikenja")

    @app.event("app_mention")
    def on_app_mention(event: dict[str, Any]) -> None:
        pool.submit(_guarded, handler, event)

    log.info(
        "listening as the owner's personal instance (owner %s, %s)",
        config.slack.owner_user_id,
        f"channels {', '.join(config.slack.allowed_channels)}"
        if config.slack.allowed_channels
        else "every channel it is invited to",
    )
    SocketModeHandler(app, app_token).start()


def _guarded(handler: Handler, event: dict[str, Any]) -> None:
    """Never let one bad event kill the worker thread."""
    try:
        handler.handle_mention(event)
    except Exception:  # noqa: BLE001 - a worker that dies takes the bot with it
        log.exception("unhandled error while answering a mention")
