"""Stand-ins the tests share.

`FakeSlackClient` implements the handful of Web API methods `slack_io` calls
and records what was sent, so a test can assert on the posted text without a
workspace. `FakeRunner` stands in for the headless session.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from daikenja_bot.config import BotConfig, ClaudeConfig, SlackConfig
from daikenja_bot.runner import RunResult

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def make_config(**slack_overrides: Any) -> BotConfig:
    """A minimal config: owner-only, everything else on its defaults."""
    slack_kwargs: dict[str, Any] = {"owner_user_id": "U0RIMURU"}
    slack_kwargs.update(slack_overrides)
    return BotConfig(slack=SlackConfig(**slack_kwargs), claude=ClaudeConfig())


class SlackApiFailure(Exception):
    """What a fake call raises when a test asks for a failure."""

    def __init__(self, error: str) -> None:
        super().__init__(error)
        self.response = {"error": error}


class FakeSlackClient:
    """Records calls, returns whatever the test loaded into it."""

    def __init__(
        self,
        replies: list[dict[str, Any]] | None = None,
        pages: list[dict[str, Any]] | None = None,
        users: dict[str, str] | None = None,
        channel_name: str | None = "harbor-rollout",
        fail: dict[str, str] | None = None,
        bot_user_id: str = "U0BOT",
        history: dict[str, Any] | None = None,
    ) -> None:
        self._bot_user_id = bot_user_id
        self._pages = pages if pages is not None else [
            {"ok": True, "messages": replies or [], "has_more": False}
        ]
        # `pages=` opts into an explicit call-by-call sequence (real
        # pagination, or several deliberately distinct lookups). `replies=`
        # (or nothing) is a single canned answer, returned for every
        # `conversations_replies` call in the test -- `fetch_message` and
        # `fetch_thread` now both call it independently within one test.
        self._repeat_single_page = pages is None
        self._users = users or {}
        self._channel_name = channel_name
        self._fail = fail or {}
        # `conversations_history` stands in for a single-message lookup by
        # timestamp -- a test sets the one message it wants `fetch_message`
        # to return.
        self._history = history
        self.posted: list[dict[str, Any]] = []
        self.ephemeral: list[dict[str, Any]] = []
        self.reactions: list[dict[str, Any]] = []
        self.deleted: list[dict[str, Any]] = []
        self.replies_calls: list[dict[str, Any]] = []
        self.history_calls: list[dict[str, Any]] = []

    def _maybe_fail(self, method: str) -> None:
        if method in self._fail:
            raise SlackApiFailure(self._fail[method])

    def conversations_replies(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("conversations_replies")
        self.replies_calls.append(kwargs)
        index = 0 if self._repeat_single_page else len(self.replies_calls) - 1
        if index < len(self._pages):
            return self._pages[index]
        return {"ok": True, "messages": [], "has_more": False}

    def conversations_history(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("conversations_history")
        self.history_calls.append(kwargs)
        message = self._history
        return {"ok": True, "messages": [message] if message else []}

    def auth_test(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("auth_test")
        return {"ok": True, "user_id": self._bot_user_id}

    def conversations_info(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("conversations_info")
        if self._channel_name is None:
            return {"ok": True, "channel": {}}
        return {"ok": True, "channel": {"name": self._channel_name}}

    def users_info(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("users_info")
        user_id = kwargs["user"]
        if user_id not in self._users:
            return {"ok": False, "error": "user_not_found"}
        return {
            "ok": True,
            "user": {"profile": {"display_name": self._users[user_id]}},
        }

    def chat_postMessage(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("chat_postMessage")
        self.posted.append(kwargs)
        return {"ok": True}

    def chat_postEphemeral(self, **kwargs: Any) -> dict[str, Any]:  # noqa: N802
        self._maybe_fail("chat_postEphemeral")
        self.ephemeral.append(kwargs)
        return {"ok": True}

    def chat_delete(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("chat_delete")
        self.deleted.append(kwargs)
        return {"ok": True}

    def reactions_add(self, **kwargs: Any) -> dict[str, Any]:
        self._maybe_fail("reactions_add")
        self.reactions.append(kwargs)
        return {"ok": True}


class FakeRunner:
    """Stands in for the `claude` subprocess."""

    def __init__(self, text: str = "ok", returncode: int = 0, stderr: str = "") -> None:
        self.result = RunResult(text=text, returncode=returncode, stderr=stderr)
        self.calls: list[dict[str, Any]] = []

    def __call__(self, argv, stdin, *, cwd, env, timeout):  # noqa: ANN001
        self.calls.append(
            {"argv": list(argv), "stdin": stdin, "cwd": cwd, "env": dict(env), "timeout": timeout}
        )
        return self.result
