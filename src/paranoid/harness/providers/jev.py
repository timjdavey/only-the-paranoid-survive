"""JevAPI, `jev/<model>` or `jev/<endpoint>/<model>`, and the client seam a test fakes.

See docs/specs/harness/providers.md#jev. typesafe-sdk is a default dependency, imported inside
TypesafeClient only, so nothing but a Jev run loads it. Any API that takes Jev's request shape is an
endpoint, so one provider plays them all.
"""

import math
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class Endpoint:
    """A Jev-compatible API."""

    base_url: str | None  # None: the SDK's own default, TypeSafe
    key_env: str | None  # None: the SDK reads TYPESAFE_API_KEY itself
    headers: Mapping[str, str] = field(default_factory=dict)  # sent on every call


TYPESAFE = Endpoint(None, None)
ENDPOINTS = {
    # S1-Region: eu keeps every call in the EU tier: off the peer-to-peer network, unlogged, never trained on.
    "decisionmodels": Endpoint("https://api.decisionmodels.io", "DECISIONMODELS_API_KEY", {"S1-Region": "eu"}),
}


def endpoint_of(model_name: str) -> tuple[Endpoint, str]:
    """`decisionmodels/s1-pro-5` is Decision Models' `s1-pro-5`. A name with no slash is TypeSafe's."""
    prefix, slash, model = model_name.partition("/")
    if not slash:
        return TYPESAFE, model_name
    if prefix not in ENDPOINTS:
        raise ValueError(f"jev/{model_name}: no endpoint {prefix!r}, the known ones are {', '.join(ENDPOINTS)}")
    return ENDPOINTS[prefix], model


class TypesafeClient:
    """A thin wrapper over typesafe-sdk, pointed at one endpoint."""

    def __init__(self, model: str, endpoint: Endpoint = TYPESAFE) -> None:
        self.model = model
        self.endpoint = endpoint
        self.client: Any = None

    def sdk(self) -> Any:
        """The SDK client, built once. A key is never borrowed from another endpoint."""
        if self.client is None:
            from typesafe_sdk import AsyncTypeSafeClient

            key = None
            if self.endpoint.key_env is not None:
                key = os.environ.get(self.endpoint.key_env, "").strip()
                if not key:
                    raise ValueError(f"Set {self.endpoint.key_env} to play {self.model}, see docs/harness/models.md#keys")
            self.client = AsyncTypeSafeClient(
                model=self.model, base_url=self.endpoint.base_url, api_key=key, headers=dict(self.endpoint.headers)
            )
        return self.client

    async def ask(self, state: str, question: str, options: Sequence[str]) -> JevAnswer:
        from typesafe_sdk import Choice

        client = self.sdk()
        criteria: dict[str, Any] = {option: None for option in options}
        questions = {QUESTION_NAME: Choice(instructions=question, criteria=criteria)}
        response = await client.system_one(state=state, questions=questions)
        answer = response.choices[QUESTION_NAME]
        missing = [i for i, option in enumerate(options) if option not in answer.probabilities]
        if missing:
            raise ValueError(f"{self.model}'s reply has no probability for the options at {missing}")
        probabilities = tuple(float(answer.probabilities[option]) for option in options)
        return JevAnswer(probabilities, answer.confidence, response.model_dump())


def text_of(input: list[ChatMessage], kind: type) -> str:
    """The text of the last message of that kind."""
    return next(message.text for message in reversed(input) if isinstance(message, kind))


def check(probabilities: Sequence[float], channels: int, model: str) -> None:
    if len(probabilities) != channels:
        raise ValueError(f"{model} gave {len(probabilities)} probabilities for {channels} channels")
    if any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError(f"{model} gave a probability that is negative or not finite")
    if sum(probabilities) == 0:
        raise ValueError(f"{model} gave every channel a probability of 0")


class JevAPI(StoreAPI):
    """`jev/<model>` or `jev/<endpoint>/<model>`. One ask a round with the state as given, nothing kept between rounds."""

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
        endpoint, model = endpoint_of(model_name)
        self.client: JevClient = client if client is not None else TypesafeClient(model, endpoint)

    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets:
        return (await self.answer(store, input))[0]

    async def answer(self, store: RunStore, input: list[ChatMessage]) -> tuple[Bets, dict[str, Any]]:
        skin = skin_named(store.skin)
        state = text_of(input, ChatMessageSystem) + "\n\n" + text_of(input, ChatMessageUser)
        answer = await self.client.ask(state, skin.question, skin.channels)
        check(answer.probabilities, len(skin.channels), self.model_name)
        bets = split_budget(answer.probabilities, store.config().budget)
        logged = {
            "probabilities": list(answer.probabilities),
            "confidence": answer.confidence,
            "raw": dict(answer.raw),
            "rounded_out": sum(1 for p, bet in zip(answer.probabilities, bets) if p > 0 and bet == 0),
        }
        return bets, logged
