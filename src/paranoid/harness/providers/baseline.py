"""BaselineAPI, `baseline/<name>` over the baselines layer's POLICIES. See docs/specs/harness/providers.md#baseline."""

import dataclasses
import typing
from typing import Any

from inspect_ai.model import ChatMessage, GenerateConfig

from paranoid.baselines import POLICIES
from paranoid.engine import Bets

from ..store import RunStore
from . import StoreAPI


def cast(value: Any, kind: Any) -> Any:
    """inspect passes -M values as strings, so each is cast to its field's type."""
    if not isinstance(value, str) or kind is str:
        return value
    if kind is bool:
        return value.lower() in ("1", "true", "yes")
    return kind(value)


class BaselineAPI(StoreAPI):
    """`baseline/<name>`. Model args are the policy's parameters."""

    connections = 32  # no I/O, so the cap only bounds concurrency

    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        **model_args: Any,
    ) -> None:
        super().__init__(model_name, base_url, api_key, config)
        if model_name not in POLICIES:
            raise ValueError(f"unknown baseline {model_name!r}, the known ones are {', '.join(POLICIES)}")
        build = POLICIES[model_name]
        hints = typing.get_type_hints(build)
        fields = [f.name for f in dataclasses.fields(build)] if dataclasses.is_dataclass(build) else []
        for name in model_args:
            if name not in fields:
                known = ", ".join(fields) or "none"
                raise ValueError(f"baseline/{model_name} has no parameter {name!r}, its parameters are {known}")
        self.policy = build(**{name: cast(value, hints[name]) for name, value in model_args.items()})

    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets:
        return self.policy(store.game().view(self.policy.peeks))
