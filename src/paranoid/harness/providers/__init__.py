"""StoreAPI and the provider registrations. See docs/specs/harness/providers.md.

A provider plays a model that cannot call a tool: it ignores the messages, reads the store, and answers
with one call to the skin's tool. Each @modelapi imports its class only when inspect asks for it.
"""

from typing import Any

from inspect_ai.model import (
    ChatCompletionChoice,
    ChatMessage,
    ChatMessageAssistant,
    GenerateConfig,
    ModelAPI,
    ModelOutput,
    ModelUsage,
    modelapi,
)
from inspect_ai.tool import ToolCall, ToolChoice, ToolInfo
from inspect_ai.util import store_as

from paranoid.engine import BetError, Bets

from ..store import RunStore


class StoreAPI(ModelAPI):
    """The shared base. Subclasses implement `bets`, or `answer` to log more beside the bets."""

    connections = 1

    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        **model_args: Any,
    ) -> None:
        super().__init__(model_name, base_url, api_key, [], config)

    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets:
        raise NotImplementedError

    async def answer(self, store: RunStore, input: list[ChatMessage]) -> tuple[Bets, dict[str, Any] | None]:
        """The bets, and what to log on the message beside them."""
        return await self.bets(store, input), None

    async def generate(
        self, input: list[ChatMessage], tools: list[ToolInfo], tool_choice: ToolChoice, config: GenerateConfig
    ) -> ModelOutput:
        if not tools:
            raise RuntimeError(f"{self.model_name} was offered no tool, so it cannot place bets")
        store = store_as(RunStore)
        bets, metadata = await self.answer(store, input)
        try:
            checked = store.game().check(bets)  # a bad split is a bug in the provider, never a model's bad call
        except BetError as error:
            raise RuntimeError(f"{self.model_name} placed bets the engine rejects in round {store.round()}: {error}") from None
        name = next(iter(tools[0].parameters.properties))  # the skin's bets_name
        call = ToolCall(id=f"{self.model_name}-{store.round()}", function=tools[0].name, arguments={name: list(checked)})
        message = ChatMessageAssistant(content="", tool_calls=[call], model=self.model_name, metadata=metadata)
        choice = ChatCompletionChoice(message=message, stop_reason="tool_calls")
        return ModelOutput(model=self.model_name, choices=[choice], usage=ModelUsage())

    def max_connections(self) -> int:
        return self.connections


@modelapi(name="baseline")
def baseline() -> type[ModelAPI]:
    from .baseline import BaselineAPI

    return BaselineAPI


@modelapi(name="jev")
def jev() -> type[ModelAPI]:
    from .jev import JevAPI

    return JevAPI


@modelapi(name="timestral")
def timestral() -> type[ModelAPI]:
    from .timestral import TimestralAPI

    return TimestralAPI
