"""Check, before answering anything, that the skills this bot needs exist.

A real run against an install one version behind produced this as the
`judgement`: *"The /daikenja:judgement command isn't available in this session,
but I can analyse the thread"*, followed by a confident answer from no
source at all. Asking the session to report an unloaded skill helps and is
kept, but it is a request, and a small model ignores it. This check is not a
request.

It costs no tokens: `claude plugin details` reads what is installed on disk,
and a configured `plugin_dir` is read directly. When neither can be
determined the bot still starts -- the check says so and gets out of the
way, because refusing to run over a CLI output format that may have moved
would be worse than the problem.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .commands import JUDGEMENT, SUMMARY
from .config import BotConfig
from .prompts import skill_name
from .runner import NO_WINDOW, RunnerError, resolve_command, scrubbed_env

log = logging.getLogger(__name__)

PLUGIN_NAME = "daikenja"
DETAILS_TIMEOUT = 60

# Which skill each command cannot run without.
REQUIRED_SKILL = {SUMMARY: "thread", JUDGEMENT: "judgement"}

SKILLS_LINE_RE = re.compile(r"^\s*Skills\s*\(\d+\)\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class SkillReport:
    """What the check found."""

    available: frozenset[str] | None
    source: str

    @property
    def determined(self) -> bool:
        return self.available is not None

    def missing(self) -> dict[str, str]:
        """Command name -> the line to post when someone asks for it."""
        if self.available is None:
            return {}
        out: dict[str, str] = {}
        for command, skill in REQUIRED_SKILL.items():
            if skill not in self.available:
                out[command] = (
                    f"I cannot run `{command}`: the {skill_name(command)} skill "
                    f"is not in {self.source}. Update the Daikenja plugin to a "
                    "version that ships it, or point `claude.plugin_dir` at a "
                    "working tree that does."
                )
        return out


def _from_plugin_dir(plugin_dir: str) -> SkillReport:
    root = Path(plugin_dir).expanduser() / "skills"
    if not root.is_dir():
        return SkillReport(available=None, source=f"the working tree at {plugin_dir}")
    names = {
        child.name for child in root.iterdir() if (child / "SKILL.md").is_file()
    }
    return SkillReport(
        available=frozenset(names), source=f"the working tree at {plugin_dir}"
    )


def _default_details(argv: list[str], env: dict[str, str]) -> tuple[int, str]:
    # `env` is the scrubbed environment, and passing it is the point: this is
    # the second place the bot starts the CLI, and "the model never holds a
    # Slack token" has to hold in both. The check itself runs one fixed
    # command over a file on disk before any thread has been read, so nothing
    # here was reachable -- but the rule was written in `runner.py` and not
    # honoured here, which is how it stops being true later.
    completed = subprocess.run(
        argv,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=DETAILS_TIMEOUT,
        check=False,
        creationflags=NO_WINDOW,
    )
    return completed.returncode, (completed.stdout or "")


def check(
    config: BotConfig,
    *,
    environ: dict[str, str] | None = None,
    details: Callable[[list[str], dict[str, str]], tuple[int, str]] = _default_details,
) -> SkillReport:
    """Work out which Daikenja skills the headless session will find."""
    if config.claude.plugin_dir:
        return _from_plugin_dir(config.claude.plugin_dir)

    source = f"the installed {PLUGIN_NAME} plugin"
    try:
        command = resolve_command(config.claude.command)
    except RunnerError as exc:
        log.warning("skill check skipped: %s", exc)
        return SkillReport(available=None, source=source)

    argv = [command, "plugin", "details", PLUGIN_NAME]
    try:
        returncode, output = details(argv, scrubbed_env(config, environ or {}))
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("skill check skipped: %s", exc)
        return SkillReport(available=None, source=source)

    if returncode != 0:
        log.warning(
            "skill check skipped: `%s plugin details %s` exited %s",
            config.claude.command,
            PLUGIN_NAME,
            returncode,
        )
        return SkillReport(available=None, source=source)

    return SkillReport(available=parse_skills(output), source=source)


def parse_skills(output: str) -> frozenset[str] | None:
    """Read the ``Skills (18)  compose, doc-review, ...`` inventory line.

    None means the line was not there, which is how a changed output format
    reaches the caller as "could not determine" rather than as "no skills".
    """
    match = SKILLS_LINE_RE.search(output or "")
    if not match:
        return None
    names = {part.strip() for part in match.group(1).split(",")}
    return frozenset(name for name in names if name)
