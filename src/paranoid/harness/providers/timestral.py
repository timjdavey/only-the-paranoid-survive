"""TimestralAPI, `timestral/<policy>` over the forecasters layer's TIMESTRAL_POLICIES.

See docs/specs/harness/providers.md#timestral. The model, its pin and its cache are that layer's.
"""

from dataclasses import replace
from typing import Any

import numpy as np
from inspect_ai.model import ChatMessage, GenerateConfig

from paranoid.engine import Bets
from paranoid.forecasters import TIMESTRAL_POLICIES, Forecaster, require_timestral

from ..store import RunStore
from . import StoreAPI


class TimestralAPI(StoreAPI):
    """`timestral/<policy>`. Pass a `forecaster` to play a fake, as the tests do."""

    connections = 1  # a forecast is CPU bound, so two at once would stall the loop for no gain

    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        forecaster: Forecaster | None = None,
        **model_args: Any,
    ) -> None:
        super().__init__(model_name, base_url, api_key, config)
        if model_name not in TIMESTRAL_POLICIES:
            raise ValueError(f"unknown Timestral policy {model_name!r}, the known ones are {', '.join(TIMESTRAL_POLICIES)}")
        policy = TIMESTRAL_POLICIES[model_name]
        if forecaster is None:
            require_timestral()
        else:
            policy = replace(policy, forecaster=forecaster)
        self.policy = policy

    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets:
        return (await self.answer(store, input))[0]

    async def answer(self, store: RunStore, input: list[ChatMessage]) -> tuple[Bets, dict[str, Any]]:
        view = store.game().view(False)
        forecast = self.policy.forecast(view)  # read back from the cache by the two calls below
        quantiles = None
        if forecast is not None:
            quantiles = [row.tolist() if np.isfinite(row).all() else None for row in forecast.quantiles]
        logged = {
            "quantiles": quantiles,
            "cache_key": None if forecast is None else forecast.cache_key,
            "rounded_out": self.policy.rounded_out(view),
        }
        return self.policy(view), logged
