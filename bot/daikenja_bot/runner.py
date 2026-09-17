"""Run the model, headless, with no way to reach Slack.

This is the whole of the model layer. It starts `claude -p`, pipes the
subject in, and returns text. It is given no Slack client, no token and no
send capability, and `scrubbed_env` takes the credentials out of the
environment the child process inherits -- otherwise "the model cannot post"
would be true only until it read `os.environ` and called the API itself.

The tool allowlist is the second half of the same idea. A session that can
only read files can still find a ledger; it cannot run a command, write a
file or fetch a URL on the say-so of something it read in a thread.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass
from typing import Mapping, Sequence

from .config import BotConfig, secret_env_names
from .prompts import (
    build_input,
    build_instruction,
    extract_output,
    is_unavailable,
    skill_name,
)
from .subject import Subject

log = logging.getLogger(__name__)

# Anything matching these is stripped from the child's environment. The
# configured token variables are removed by name as well; this catches the
# rest of a Slack app's environment (signing secret, client secret) whatever
# the user called them.
SCRUBBED_PREFIXES = ("SLACK_", "SLACK")


class RunnerError(Exception):
    """The headless session could not be run, or produced nothing usable."""


@dataclass(frozen=True)
class RunResult:
    text: str
    returncode: int
    stderr: str


def scrubbed_env(
    config: BotConfig, environ: Mapping[str, str]
) -> dict[str, str]:
    """The environment the model process gets: this one, minus the secrets."""
    drop = {name.upper() for name in secret_env_names(config)}
    out: dict[str, str] = {}
    for key, value in environ.items():
        upper = key.upper()
        if upper in drop:
            continue
        if any(upper.startswith(prefix) for prefix in SCRUBBED_PREFIXES):
            continue
        out[key] = value
    return out


def build_argv(config: BotConfig) -> list[str]:
    """The `claude` command line, without the prompt.

    `--permission-prompts none` matters: in a headless run there is nobody
    to answer a permission prompt, so without it a tool outside the
    allowlist stalls the session instead of being refused.
    """
    claude = config.claude
    argv = [
        claude.command,
        "-p",
        "--output-format",
        "text",
        "--permission-prompts",
        "none",
        "--allowedTools",
        ",".join(claude.allowed_tools),
    ]
    if claude.model:
        argv += ["--model", claude.model]
    if claude.plugin_dir:
        argv += ["--plugin-dir", claude.plugin_dir]
    argv += list(claude.extra_args)
    return argv


def run_command(
    config: BotConfig,
    command_name: str,
    subject: Subject,
    *,
    environ: Mapping[str, str],
    runner: "CommandRunner | None" = None,
) -> str:
    """Produce the text for one command. Returns the answer, never posts it."""
    if subject.is_empty:
        raise RunnerError("there was nothing to read in that subject")

    instruction = build_instruction(command_name, subject)
    argv = build_argv(config) + [instruction]
    stdin = build_input(subject)

    invoke = runner or _subprocess_runner
    result = invoke(
        argv,
        stdin,
        cwd=str(config.claude.resolved_working_dir()),
        env=scrubbed_env(config, environ),
        timeout=config.claude.timeout_seconds,
    )

    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        tail = detail[-1] if detail else f"exit code {result.returncode}"
        raise RunnerError(f"the headless session failed: {tail}")

    answer = extract_output(result.text, command_name)
    if not answer:
        raise RunnerError("the headless session returned nothing")
    if is_unavailable(answer):
        raise RunnerError(
            f"{skill_name(command_name)} is not loaded in my headless session. "
            "Check that the Daikenja plugin is installed for the account the "
            "bot runs as, and that its version ships that skill -- or point "
            "claude.plugin_dir at a working tree that does."
        )
    return answer


class CommandRunner:
    """The call shape `run_command` needs, so tests can supply their own."""

    def __call__(
        self,
        argv: Sequence[str],
        stdin: str,
        *,
        cwd: str,
        env: Mapping[str, str],
        timeout: int,
    ) -> RunResult:  # pragma: no cover - interface only
        raise NotImplementedError


def resolve_command(command: str) -> str:
    """Find the executable, honouring Windows' PATHEXT.

    On Windows the Claude Code CLI installs as `claude.CMD`, and Python's
    subprocess does not apply PATHEXT to a bare name -- it hands the name
    straight to CreateProcess, which fails with a plain "file not found".
    `shutil.which` does apply it, and the resolved path launches fine. On
    POSIX this is an ordinary PATH lookup.
    """
    resolved = shutil.which(command)
    if resolved:
        return resolved
    raise RunnerError(
        f"{command} was not found. Install the Claude Code CLI, or set "
        "claude.command in bot.yaml to the full path of the executable."
    )


def _subprocess_runner(
    argv: Sequence[str],
    stdin: str,
    *,
    cwd: str,
    env: Mapping[str, str],
    timeout: int,
) -> RunResult:
    argv = [resolve_command(argv[0]), *argv[1:]]
    log.info("running %s in %s", argv[0], cwd)
    try:
        completed = subprocess.run(
            list(argv),
            input=stdin,
            cwd=cwd,
            env=dict(env),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except OSError as exc:
        raise RunnerError(f"{argv[0]} could not be started: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RunnerError(
            f"the headless session did not finish within {timeout}s"
        ) from exc

    return RunResult(
        text=completed.stdout or "",
        returncode=completed.returncode,
        stderr=completed.stderr or "",
    )
