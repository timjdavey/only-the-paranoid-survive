"""The three tools, each built from the skin. See docs/specs/harness/solver.md#submit, #notes and #compute.

Every word on a tool is the skin's: its name, its text, and its one parameter's name and text.
Built with ToolDef rather than @tool, which would rename each tool after its factory.

The sandbox reset reaches into inspect's Docker internals, pinned with inspect_ai in pyproject.toml.
HS21 fails loudly if they move.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from inspect_ai.tool import Tool, ToolDef, ToolParams
from inspect_ai.util import OutputLimitExceededError, sandbox, store_as
from inspect_ai.util._sandbox.docker.compose import compose_command
from inspect_ai.util._sandbox.docker.docker import DockerSandboxEnvironment

from paranoid.engine import BetError
from paranoid.skins import Skin, render_record

from .store import RunStore, StoredRow

NOTES_CAP = 2000  # characters, pilot to confirm
COMPUTE_TIMEOUT = 30  # seconds
COMPUTE_OUTPUT = 4000  # characters returned
RECORD_FILE = "record.csv"
COMPUTE_USER = "nobody"  # on Docker, so the code can read record.csv and not change it
RESET_TIMEOUT = 60  # seconds
EMPTY_HERE = ["find", ".", "-mindepth", "1", "-delete"]  # relative paths only, so it never leaves the working directory


def built(execute: Callable[..., Awaitable[str]], name: str, text: str, param: str, schema: dict[str, Any]) -> Tool:
    """A tool of one required parameter, every word from the skin. The schema carries the parameter's text."""
    parameters = ToolParams(properties={param: schema}, required=[param])
    return ToolDef(execute, name=name, description=text, parameters=parameters).as_tool()


def record_blocks(text: str) -> list[str]:
    """The record cut after every \\n and nowhere else: the header, then one piece per row. Nothing added or dropped.

    Not splitlines, which also cuts at \\x0b, U+2028 and other breaks.
    """
    pieces = text.split("\n")
    return [piece + "\n" for piece in pieces[:-1]] + ([pieces[-1]] if pieces[-1] else [])


def played_line(skin: Skin, store: RunStore) -> str:
    """The header and the last line of the record: the round just played, in the record's own shape."""
    lines = record_blocks(render_record(skin, store.record()))
    return lines[0] + lines[-1]


def submit(skin: Skin) -> Tool:
    """The engine's Game.play behind a tool. One parameter, named skin.bets_name, a list of ints."""

    async def execute(**kwargs: Any) -> str:
        store = store_as(RunStore)
        if not store.awaiting_submit:  # a second submit in one reply cannot play two rounds
            store.bad_calls += 1
            return skin.bad_call
        try:
            row = store.game().play(kwargs[skin.bets_name])  # untouched: the engine checks the shape
        except BetError:
            store.bad_calls += 1
            return skin.bad_call
        store.rows = [*store.rows, StoredRow.of(row)]
        store.awaiting_submit = False
        return played_line(skin, store)

    schema = {"type": "array", "items": {"type": "integer"}, "description": skin.bets_text}
    return built(execute, skin.tool_name, skin.tool_text, skin.bets_name, schema)


def notes(skin: Skin, cap: int = NOTES_CAP) -> Tool:
    """Replaces the stored note with the first `cap` characters of its one string, and returns it as stored."""

    async def execute(**kwargs: Any) -> str:
        store = store_as(RunStore)
        store.notes = str(kwargs[skin.notes_param])[:cap]
        return store.notes

    schema = {"type": "string", "description": skin.notes_param_text}
    return built(execute, skin.notes_name, skin.notes_text, skin.notes_param, schema)


def compute(skin: Skin) -> Tool:
    """Runs `python3 -I -c <code>` in the sandbox and returns stdout then stderr, cut to COMPUTE_OUTPUT."""

    async def execute(**kwargs: Any) -> str:
        code = str(kwargs[skin.compute_param])
        user = COMPUTE_USER if docker_sandbox() is not None else None
        try:
            result = await sandbox().exec(
                ["python3", "-I", "-c", code], user=user, timeout=COMPUTE_TIMEOUT, timeout_retry=False
            )
        except TimeoutError:
            return "timeout"
        except OutputLimitExceededError as error:
            return (error.truncated_output or "")[:COMPUTE_OUTPUT]
        return (result.stdout + result.stderr)[:COMPUTE_OUTPUT]

    schema = {"type": "string", "description": skin.compute_param_text}
    return built(execute, skin.compute_name, skin.compute_text, skin.compute_param, schema)


async def write_record(skin: Skin, store: RunStore) -> None:
    """record.csv in the sandbox's working directory, so the code sees the record and nothing else."""
    await sandbox().write_file(RECORD_FILE, render_record(skin, store.record()))


def docker_sandbox() -> DockerSandboxEnvironment | None:
    """The sample's sandbox when it is Docker's, else None. sandbox() returns a proxy, so it is unwrapped by as_type."""
    try:
        return sandbox().as_type(DockerSandboxEnvironment)
    except TypeError:
        return None


async def reset_sandbox() -> None:
    """Clears everything compute left behind, so nothing crosses a round. Raises RuntimeError if it fails.

    Docker restarts the container: the root is read only and every writable mount is tmpfs, so a restart
    clears files, /dev/shm, processes and SysV memory at once. Any other sandbox empties its working directory.
    """
    docker = docker_sandbox()
    if docker is not None:
        command = ["restart", "--timeout", "0", docker._service]
        result = await compose_command(command, project=docker._project, timeout=RESET_TIMEOUT)
    else:
        result = await sandbox().exec(EMPTY_HERE, timeout=RESET_TIMEOUT)
    if not result.success:
        raise RuntimeError(f"the sandbox reset failed with exit code {result.returncode}")
