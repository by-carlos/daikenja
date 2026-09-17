"""Read and validate ``~/.claude/daikenja/bot.yaml``.

The config file holds identifiers and paths. Tokens are read from the
environment by default, because the bot runs as a long-lived process and an
environment variable is the one place a credential can live without a file
on disk to leak. A ``*_token_file`` is supported for people who prefer a
0600 file, and an inline token is supported but documented as the last
choice.

Nothing here reaches the model. `runner.scrubbed_env` strips every name this
module reads a secret from before the headless session starts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".claude" / "daikenja" / "bot.yaml"

DEFAULT_BOT_TOKEN_ENV = "SLACK_BOT_TOKEN"
DEFAULT_APP_TOKEN_ENV = "SLACK_APP_TOKEN"
DEFAULT_CONFLUENCE_TOKEN_ENV = "CONFLUENCE_API_TOKEN"

# Read-only by construction. The headless session has to reach the user's
# `daikenja.yaml`, the project cards and the ledgers, and nothing else. A
# tool outside this list is denied rather than queued for a prompt nobody is
# there to answer -- see `runner.build_argv`.
DEFAULT_ALLOWED_TOOLS = ("Read", "Glob", "Grep")

DEFAULT_TIMEOUT_SECONDS = 300

# Sent only to the person who mentioned the bot, and only they can see it.
# `{owner}` becomes a mention of `slack.owner_user_id`, which renders as a
# name without notifying anyone -- an ephemeral message never notifies.
DEFAULT_UNAUTHORIZED_MESSAGE = (
    "Sorry -- this is a personal instance of the Daikenja bot. It runs on "
    "{owner}'s own machine, answers from their own project records, and only "
    "they can trigger it. Ask them if you need something from it."
)


class ConfigError(Exception):
    """The config file is missing, unreadable, or does not say enough."""


@dataclass(frozen=True)
class SlackConfig:
    owner_user_id: str
    allowed_users: tuple[str, ...] = ()
    allowed_channels: tuple[str, ...] = ()
    bot_token_env: str = DEFAULT_BOT_TOKEN_ENV
    app_token_env: str = DEFAULT_APP_TOKEN_ENV
    bot_token_file: str | None = None
    app_token_file: str | None = None
    bot_token: str | None = None
    app_token: str | None = None
    ack_reaction: str | None = "eyes"
    # `None` is the silent form. `{owner}` in the text is replaced with a
    # mention of `owner_user_id` by the posting layer -- after the mrkdwn
    # conversion, which would otherwise escape the angle brackets.
    unauthorized_message: str | None = DEFAULT_UNAUTHORIZED_MESSAGE

    def allows_user(self, user_id: str) -> bool:
        """Owner-only unless the config widens it.

        The owner is always allowed: this is a personal instance, and a
        config that listed colleagues but forgot its owner would lock the
        person who runs the process out of their own bot.
        """
        return user_id in set(self.allowed_users) | {self.owner_user_id}

    def allows_channel(self, channel_id: str) -> bool:
        """Empty `allowed_channels` means every channel it was invited to."""
        return not self.allowed_channels or channel_id in self.allowed_channels

    def may_trigger(self, user_id: str, channel_id: str) -> bool:
        return self.allows_user(user_id) and self.allows_channel(channel_id)


@dataclass(frozen=True)
class ClaudeConfig:
    command: str = "claude"
    model: str | None = None
    plugin_dir: str | None = None
    working_dir: str | None = None
    allowed_tools: tuple[str, ...] = DEFAULT_ALLOWED_TOOLS
    extra_args: tuple[str, ...] = ()
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def resolved_working_dir(self) -> Path:
        """Where the headless session runs.

        Defaults to the user's home directory rather than the bot's own
        directory. `judgement` resolves a project by key, then by working
        directory, then by the subject's content; a bot has no meaningful
        working directory, and running it inside a registered project would
        silently attach every thread to that project. Home is almost never
        registered, so content resolution gets to do its job.
        """
        if self.working_dir:
            return Path(self.working_dir).expanduser()
        return Path.home()


@dataclass(frozen=True)
class ConfluenceConfig:
    base_url: str
    email: str
    token_env: str = DEFAULT_CONFLUENCE_TOKEN_ENV
    token_file: str | None = None
    token: str | None = None


@dataclass(frozen=True)
class BotConfig:
    slack: SlackConfig
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    confluence: ConfluenceConfig | None = None
    source_path: Path | None = None

    @property
    def confluence_configured(self) -> bool:
        return self.confluence is not None


def _as_str_tuple(value: Any, key: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            if not isinstance(item, (str, int)):
                raise ConfigError(f"{key}: every entry must be a string, got {item!r}")
            out.append(str(item))
        return tuple(out)
    raise ConfigError(f"{key}: expected a string or a list of strings, got {value!r}")


def _section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{key}: expected a block of keys, got {value!r}")
    return value


def parse_config(data: Any, source_path: Path | None = None) -> BotConfig:
    """Turn parsed YAML into a `BotConfig`, or say exactly what is missing."""
    if data is None:
        raise ConfigError("the config file is empty")
    if not isinstance(data, dict):
        raise ConfigError("the config file must be a block of keys at the top level")

    slack_raw = _section(data, "slack")
    owner = slack_raw.get("owner_user_id")
    if not owner or not isinstance(owner, str):
        raise ConfigError(
            "slack.owner_user_id is required -- the Slack user ID (starts with U) "
            "allowed to trigger this bot. Without it the bot would answer anyone."
        )

    ack_reaction = slack_raw.get("ack_reaction", "eyes")
    if ack_reaction is not None and not isinstance(ack_reaction, str):
        raise ConfigError("slack.ack_reaction: expected an emoji name or null")

    # An explicit `null` is the silent form, so absence and null differ here
    # and the key cannot be read with `or`.
    unauthorized = slack_raw.get("unauthorized_message", DEFAULT_UNAUTHORIZED_MESSAGE)
    if unauthorized is not None and not isinstance(unauthorized, str):
        raise ConfigError(
            "slack.unauthorized_message: expected a line of text, or null to say "
            "nothing at all"
        )

    slack = SlackConfig(
        owner_user_id=owner,
        allowed_users=_as_str_tuple(slack_raw.get("allowed_users"), "slack.allowed_users"),
        allowed_channels=_as_str_tuple(
            slack_raw.get("allowed_channels"), "slack.allowed_channels"
        ),
        bot_token_env=str(slack_raw.get("bot_token_env") or DEFAULT_BOT_TOKEN_ENV),
        app_token_env=str(slack_raw.get("app_token_env") or DEFAULT_APP_TOKEN_ENV),
        bot_token_file=slack_raw.get("bot_token_file"),
        app_token_file=slack_raw.get("app_token_file"),
        bot_token=slack_raw.get("bot_token"),
        app_token=slack_raw.get("app_token"),
        ack_reaction=ack_reaction or None,
        unauthorized_message=unauthorized.strip() if unauthorized else None,
    )

    claude_raw = _section(data, "claude")
    timeout = claude_raw.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        raise ConfigError("claude.timeout_seconds: expected a whole number of seconds")
    if timeout <= 0:
        raise ConfigError("claude.timeout_seconds: must be greater than zero")

    allowed_tools = _as_str_tuple(claude_raw.get("allowed_tools"), "claude.allowed_tools")
    claude = ClaudeConfig(
        command=str(claude_raw.get("command") or "claude"),
        model=claude_raw.get("model") or None,
        plugin_dir=claude_raw.get("plugin_dir"),
        working_dir=claude_raw.get("working_dir"),
        allowed_tools=allowed_tools or DEFAULT_ALLOWED_TOOLS,
        extra_args=_as_str_tuple(claude_raw.get("extra_args"), "claude.extra_args"),
        timeout_seconds=timeout,
    )

    confluence_raw = _section(data, "confluence")
    confluence = None
    if confluence_raw:
        base_url = confluence_raw.get("base_url")
        email = confluence_raw.get("email")
        if not base_url or not email:
            raise ConfigError(
                "confluence: both base_url and email are required when the block "
                "is present. Remove the block to run without Confluence support."
            )
        confluence = ConfluenceConfig(
            base_url=str(base_url).rstrip("/"),
            email=str(email),
            token_env=str(confluence_raw.get("token_env") or DEFAULT_CONFLUENCE_TOKEN_ENV),
            token_file=confluence_raw.get("token_file"),
            token=confluence_raw.get("token"),
        )

    return BotConfig(
        slack=slack, claude=claude, confluence=confluence, source_path=source_path
    )


def load_config(path: Path | str | None = None) -> BotConfig:
    """Read the config file and parse it."""
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG_PATH
    if not config_path.is_file():
        raise ConfigError(
            f"no config file at {config_path}. bot/README.md has a starting point "
            "to copy; it is never committed to this repository."
        )
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{config_path} does not parse as YAML: {exc}") from exc
    return parse_config(raw, source_path=config_path)


def resolve_secret(
    *,
    label: str,
    env_name: str | None = None,
    file_path: str | None = None,
    inline: str | None = None,
    environ: dict[str, str] | None = None,
) -> str:
    """Find one credential, in the documented order, or say where to put it.

    Environment first, then a file, then an inline value. The order is the
    preference order, so a config that sets several gets the safest one.
    """
    env = os.environ if environ is None else environ
    if env_name and env.get(env_name):
        return env[env_name].strip()
    if file_path:
        resolved = Path(file_path).expanduser()
        if not resolved.is_file():
            raise ConfigError(f"{label}: no file at {resolved}")
        content = resolved.read_text(encoding="utf-8").strip()
        if content:
            return content
        raise ConfigError(f"{label}: the file at {resolved} is empty")
    if inline:
        return str(inline).strip()
    raise ConfigError(
        f"{label}: not set. Export {env_name} before starting the bot, or point "
        f"the matching *_token_file key at a file holding it."
    )


def secret_env_names(config: BotConfig) -> tuple[str, ...]:
    """Every environment variable this config reads a credential from.

    `runner.scrubbed_env` removes these before the model process starts, so
    the list has to come from the config rather than from a fixed set.
    """
    names = [config.slack.bot_token_env, config.slack.app_token_env]
    if config.confluence:
        names.append(config.confluence.token_env)
    return tuple(name for name in names if name)
