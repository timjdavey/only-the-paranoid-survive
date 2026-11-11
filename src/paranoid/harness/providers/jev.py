"""JevAPI, `jev/<model>`, and the client seam a test fakes. See docs/specs/harness/providers.md#jev.

typesafe-sdk is a default dependency, imported inside TypesafeClient only, so nothing but a Jev run loads it.
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from inspect_ai.model import ChatMessage, ChatMessageSystem, ChatMessageUser, GenerateConfig

from paranoid.engine import Bets, split_budget

from ..config import skin_named
from ..store import RunStore
from . import StoreAPI

QUESTION_NAME = "channel"


@dataclass(frozen=True)
class JevAnswer:
    probabilities: tuple[float, ...]  # one per option, in option order
    confidence: float | None
    raw: Mapping[str, Any]  # the SDK's reply as returned


class JevClient(Protocol):
    async def ask(self, state: str, question: str, options: Sequence[str]) -> JevAnswer: ...


class TypesafeClient:
    """A thin wrapper over typesafe-sdk. The SDK reads TYPESAFE_API_KEY itself."""

    def __init__(self, model: str) -> None:
        self.model = model
        self.client: Any = None

    async def ask(self, state: str, question: str, options: Sequence[str]) -> JevAnswer:
        from typesafe_sdk import AsyncTypeSafeClient, Choice

        if self.client is None:
            self.client = AsyncTypeSafeClient(model=self.model)
        criteria: dict[str, Any] = {option: None for option in options}
        questions = {QUESTION_NAME: Choice(instructions=question, criteria=criteria)}
        response = await self.client.system_one(state=state, questions=questions)
        answer = response.choices[QUESTION_NAME]
        missing = [i for i, option in enumerate(options) if option not in answer.probabilities]
        if missing:
            raise ValueError(f"Jev's reply has no probability for the options at {missing}")
        probabilities = tuple(float(answer.probabilities[option]) for option in options)
        return JevAnswer(probabilities, answer.confidence, response.model_dump())


def text_of(input: list[ChatMessage], kind: type) -> str:
    """The text of the last message of that kind."""
    return next(message.text for message in reversed(input) if isinstance(message, kind))


def check(probabilities: Sequence[float], channels: int) -> None:
    if len(probabilities) != channels:
        raise ValueError(f"Jev gave {len(probabilities)} probabilities for {channels} channels")
    if any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError("Jev gave a probability that is negative or not finite")
    if sum(probabilities) == 0:
        raise ValueError("Jev gave every channel a probability of 0")


class JevAPI(StoreAPI):
    """`jev/<model>`. One ask a round with the state as given, nothing kept between rounds."""

    connections = 4

    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        client: JevClient | None = None,
        **model_args: Any,
    ) -> None:
        super().__init__(model_name, base_url, api_key, config)
        self.client: JevClient = client if client is not None else TypesafeClient(model_name)

    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets:
        return (await self.answer(store, input))[0]

    async def answer(self, store: RunStore, input: list[ChatMessage]) -> tuple[Bets, dict[str, Any]]:
        skin = skin_named(store.skin)
        state = text_of(input, ChatMessageSystem) + "\n\n" + text_of(input, ChatMessageUser)
        answer = await self.client.ask(state, skin.question, skin.channels)
        check(answer.probabilities, len(skin.channels))
        bets = split_budget(answer.probabilities, store.config().budget)
        logged = {
            "probabilities": list(answer.probabilities),
            "confidence": answer.confidence,
            "raw": dict(answer.raw),
            "rounded_out": sum(1 for p, bet in zip(answer.probabilities, bets) if p > 0 and bet == 0),
        }
        return bets, logged
