"""round_loop, the tool choice rule and the record's content blocks. See docs/specs/harness/solver.md.

Each round: a fresh system prompt and record, the tools, then tries until a valid call to the skin's
tool or max_tries. The model reads the skin's words and nobody else's.
"""

from typing import Any, Literal

from inspect_ai.model import (
    ChatMessage,
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageTool,
    ChatMessageUser,
    ContentText,
    GenerateConfig,
    ModelName,
    get_model,
)
from inspect_ai.solver import Generate, Solver, TaskState, solver

from paranoid.baselines import POLICIES
from paranoid.engine import play
from paranoid.skins import Skin, render_record, render_system_prompt

from .config import check_tool_choice, parse_tools
from .store import RunStore, StoredRow, timeline_for, uncapped
from .tools import NOTES_CAP, compute, notes, reset_sandbox, submit, write_record

# apis whose prompt cache matches by content block. Empty until the two Anthropic checks pass,
# see docs/specs/harness/solver.md#verify-before-code. Then ("anthropic",).
BLOCK_CACHE_APIS: tuple[str, ...] = ()
STORE_KEYS = ("scenario", "seed_set", "seed_index", "skin", "rounds", "inertia", "own_scale")


def tool_choice_for(api: str, config: GenerateConfig) -> Literal["any", "auto"]:
    """`auto` when the api is anthropic and the config asks for thinking, else `any`."""
    thinking = config.reasoning_effort not in (None, "none") or config.reasoning_tokens is not None
    return "auto" if api == "anthropic" and thinking else "any"


def record_blocks(text: str) -> list[str]:
    """The record cut after every line end: the header, then one piece per row. Nothing added or dropped."""
    return text.splitlines(keepends=True)


def api_name() -> str:
    """The active model's provider name. Model.api is the provider object, so the name comes from ModelName."""
    return ModelName(get_model()).api


def user_message(skin: Skin, store: RunStore, with_notes: bool) -> ChatMessageUser:
    """The record, as one block or cut by record_blocks, then the saved note as one more block."""
    text = render_record(skin, store.record())
    pieces = record_blocks(text) if api_name() in BLOCK_CACHE_APIS else [text]
    content: list[Any] = [ContentText(text=piece) for piece in pieces]
    if with_notes and store.notes:
        content.append(ContentText(text=store.notes))
    return ChatMessageUser(content=content)


def fill(store: RunStore, metadata: dict[str, Any]) -> None:
    """Copy the sample's metadata in, then play the warm up with the inertia cap cleared."""
    for key in STORE_KEYS:
        setattr(store, key, metadata[key])
    if metadata.get("warm_up"):
        name, _, count = metadata["warm_up"].partition(":")
        timeline = timeline_for(uncapped(store.config()), store.seed())
        record = play(POLICIES[name](), timeline, max_rounds=int(count))
        store.rows = [StoredRow.of(row) for row in record.rows]
        store.warm_up_rounds = len(record)


def settle(skin: Skin, store: RunStore, messages: list[ChatMessage]) -> set[str]:
    """Put the skin's words on every refused call of this try, and return the tools that ran."""
    ran: set[str] = set()
    for message in messages:
        if not isinstance(message, ChatMessageTool):
            continue
        if message.error is not None and message.error.type == "parsing":
            if message.function == skin.tool_name:
                store.bad_calls += 1
                message.content = skin.bad_call
            else:
                message.content = skin.no_call
            message.error = None
        elif message.function:
            ran.add(message.function)
    return ran


@solver
def round_loop(
    skin: Skin,
    tools: str = "notes,compute",
    tool_choice: str | None = None,
    max_tries: int = 10,
    notes_cap: int = NOTES_CAP,
    rolling: bool = False,
) -> Solver:
    """Plays one run, one fresh call a round. See docs/specs/harness/solver.md#each-round."""
    pilot_tools = parse_tools(tools)
    check_tool_choice(tool_choice)

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        store = state.store_as(RunStore)
        if store.scenario == "":
            fill(store, state.metadata)
        if not store.tool_choice:
            model = get_model()
            store.tool_choice = tool_choice or tool_choice_for(ModelName(model).api, model.config)
        state.metadata["tool_choice"] = store.tool_choice
        offered = [submit(skin)]
        offered += [notes(skin, notes_cap)] if "notes" in pilot_tools else []
        offered += [compute(skin)] if "compute" in pilot_tools else []
        rounds = store.config().rounds
        computed = store.compute_rounds  # what the sandbox has seen since it was last clean
        while not store.gave_up and store.round() <= rounds:
            message = user_message(skin, store, "notes" in pilot_tools)
            if rolling and state.messages and store.round() > store.warm_up_rounds + 1:
                state.messages.append(message)
            else:
                state.messages = [ChatMessageSystem(content=render_system_prompt(skin)), message]
            state.tools = list(offered)
            state.tool_choice = store.tool_choice  # type: ignore[assignment]
            if "compute" in pilot_tools:
                if store.compute_rounds > computed:  # the round before ran compute, see solver.md#compute
                    await reset_sandbox()
                    computed = store.compute_rounds
                await write_record(skin, store)
            state = await play_round(state, generate, skin, store, max_tries)
        return state

    return solve


async def play_round(state: TaskState, generate: Generate, skin: Skin, store: RunStore, max_tries: int) -> TaskState:
    """Tries until a valid call to the skin's tool, or gives up after max_tries."""
    ran: set[str] = set()
    for tries in range(1, max_tries + 1):
        store.awaiting_submit = True
        before = len(state.messages)
        state = await generate(state, tool_calls="single")
        new = state.messages[before:]
        ran |= settle(skin, store, new)
        if not store.awaiting_submit:
            store.tries = [*store.tries, tries]
            break
        reply = next((m for m in new if isinstance(m, ChatMessageAssistant)), None)
        calls = reply.tool_calls if reply is not None and reply.tool_calls else []
        if not any(call.function == skin.tool_name for call in calls):
            store.no_calls += 1
            if state.output.stop_reason == "max_tokens":
                store.cut_offs += 1
            state.messages.append(ChatMessageUser(content=skin.no_call))
    else:
        store.tries = [*store.tries, max_tries]
        store.gave_up = True
        store.awaiting_submit = False
    store.notes_rounds += skin.notes_name in ran
    store.compute_rounds += skin.compute_name in ran
    return state
