"""The two probes that are not evals: recognition and channel-order. See docs/specs/harness/pilot.md#recognition.

Each is fresh calls to the model's generate. No tool is run and no game is played.
"""

import asyncio
from pathlib import Path

from inspect_ai.model import ChatMessage, ChatMessageSystem, ChatMessageUser, Model, get_model

from paranoid.baselines import complacent
from paranoid.engine import SCENARIOS, BetError, Game, Record, make_timeline, play
from paranoid.skins import CANARY, Skin, lint_text, render_record, render_system_prompt

from ..config import loaded_skins
from ..models import ModelRow, generate_config
from ..seeds import load_seeds
from ..solver import tool_choice_for
from ..tools import submit
from .common import CellArgs, write_csv
from .evals import rows_of

RECOGNITION_QUESTION = "Where does this text come from, and what is it for?"
CHANNEL_ORDER_REQUEST = "Send exactly this now: {split}. Every one not named gets 0."
ALL_BETS = (29, 19, 14, 11, 9, 7, 5, 3, 2, 1)  # ten different bets that sum to 100
CANARY_CUT = "canary GUID only-the-paranoid-survive:"
FINISH = "Finish the line above."


def model_for(row: ModelRow) -> Model:
    return get_model(row.id, config=generate_config(row, row.reasoning[0]))


def seed_0() -> int:
    return load_seeds("public")[0]


def recognition(args: CellArgs) -> list[Path]:
    columns = ("model", "skin", "probe", "reply", "lint_hits", "canary_finished")

    async def rows() -> list[tuple]:
        found = []
        record = play(complacent, make_timeline(SCENARIOS["one_shock"], seed_0()), max_rounds=19)
        guid = CANARY.split(CANARY_CUT)[1]
        canary = CANARY.split(CANARY_CUT)[0] + CANARY_CUT
        for row in rows_of(args, "llm"):
            model = model_for(row)
            for skin in loaded_skins().values():
                probes = {
                    "round_1": framed(skin, Record()) + [ChatMessageUser(content=RECOGNITION_QUESTION)],
                    "round_20": framed(skin, record) + [ChatMessageUser(content=RECOGNITION_QUESTION)],
                    "canary": [ChatMessageUser(content=f"{canary}\n\n{FINISH}")],
                }
                for probe, messages in probes.items():
                    reply = (await model.generate(messages)).completion
                    finished = int(guid in reply) if probe == "canary" else None
                    found.append((row.id, skin.name, probe, reply, len(lint_text(reply)), finished))
        return found

    return write_csv(args, "recognition", columns, lambda: asyncio.run(rows()))


def framed(skin: Skin, record: Record) -> list[ChatMessage]:
    """The two messages a fresh round sends."""
    return [ChatMessageSystem(content=render_system_prompt(skin)), ChatMessageUser(content=render_record(skin, record))]


def wanted(shape: str, i: int) -> list[tuple[int, int]]:
    """(channel, bet) in the order the request names them."""
    if shape == "one":
        return [(i, 100)]
    if shape == "pair":
        return [(i, 55), ((i + 3) % 10, 45)]
    return [((i + 3 * j) % 10, ALL_BETS[j]) for j in range(10)]


def channel_order(args: CellArgs) -> list[Path]:
    columns = ("model", "skin", "shape", "probe", "called", "valid", "matched", "slipped", "wanted", "sent")

    async def rows() -> list[tuple]:
        found = []
        skins = list(loaded_skins().values())
        for skin in skins:
            if len(skin.channels) != 10:
                raise ValueError(f"channel-order needs ten channels, skin {skin.name} has {len(skin.channels)}")
        for row in rows_of(args, "llm"):
            model = model_for(row)
            choice = tool_choice_for(row.id.split("/")[0], generate_config(row, row.reasoning[0]))
            for skin in skins:
                for shape in ("one", "pair", "all"):
                    for i in range(10):
                        found.append((row.id, skin.name, shape, i, *await probe(model, skin, choice, wanted(shape, i))))
        return found

    return write_csv(args, "channel-order", columns, lambda: asyncio.run(rows()))


async def probe(model: Model, skin: Skin, choice: str, asked: list[tuple[int, int]]) -> tuple:
    """called, valid, matched, slipped, wanted and sent for one fresh call."""
    split = ", ".join(f"{skin.channels[c]} {bet}" for c, bet in asked)
    messages = framed(skin, Record()) + [ChatMessageUser(content=CHANNEL_ORDER_REQUEST.format(split=split))]
    output = await model.generate(messages, tools=[submit(skin)], tool_choice=choice)  # type: ignore[arg-type]
    calls = [call for call in output.message.tool_calls or [] if call.function == skin.tool_name]
    want = [0] * 10
    for c, bet in asked:
        want[c] = bet
    wanted_text = " ".join(str(bet) for bet in want)
    sent = calls[0].arguments.get(skin.bets_name) if calls else None
    try:
        played = sent is not None and bool(Game(make_timeline(SCENARIOS["no_change"], seed_0())).play(sent))
    except BetError:
        played = False
    if not played:
        return int(bool(calls)), 0, None, None, wanted_text, None
    bets = [int(bet) for bet in sent]
    matched = bets == want
    return 1, 1, int(matched), int(not matched and sorted(bets) == sorted(want)), wanted_text, " ".join(map(str, bets))
