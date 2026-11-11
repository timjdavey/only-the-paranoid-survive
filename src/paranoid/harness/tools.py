"""The three tools, each built from the skin. See docs/specs/harness/solver.md#submit, #notes and #compute.

Every word on a tool is the skin's: its name, its text, and its one parameter's name and text.
Built with ToolDef rather than @tool, which would rename each tool after its factory.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from inspect_ai.tool import Tool, ToolDef, ToolParams
from inspect_ai.util import OutputLimitExceededError, sandbox, store_as

from paranoid.engine import BetError
from paranoid.skins import Skin, render_record

from .store import RunStore, StoredRow

NOTES_CAP = 2000  # characters, pilot to confirm
COMPUTE_TIMEOUT = 30  # seconds
COMPUTE_OUTPUT = 4000  # characters returned
RECORD_FILE = "record.csv"


def built(execute: Callable[..., Awaitable[str]], name: str, text: str, param: str, schema: dict[str, Any]) -> Tool:
    """A tool of one required parameter, every word from the skin. The schema carries the parameter's text."""
    parameters = ToolParams(properties={param: schema}, required=[param])
    return ToolDef(execute, name=name, description=text, parameters=parameters).as_tool()


def played_line(skin: Skin, store: RunStore) -> str:
    """The header and the last line of the record: the round just played, in the record's own shape."""
    lines = render_record(skin, store.record()).splitlines(keepends=True)
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
        try:
            result = await sandbox().exec(
                ["python3", "-I", "-c", code], timeout=COMPUTE_TIMEOUT, timeout_retry=False
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
