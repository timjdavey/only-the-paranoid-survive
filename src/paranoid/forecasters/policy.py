"""A forecaster through a forecast rule, as an engine policy. See docs/specs/forecasters/policy.md."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar, Protocol

import numpy as np

from paranoid.baselines import FORECAST_RULES, QUANTILE_LEVELS, ForecastRule, Odds, uniform
from paranoid.engine import Bets, View

from . import cache
from .timestral import Timestral, timestral


class Forecaster(Protocol):
    @property
    def key(self) -> str: ...

    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray: ...


@dataclass(frozen=True, eq=False)
class Forecast:
    """Next round's quantiles, one row per channel, and the key they are cached under."""

    quantiles: np.ndarray  # (channels, len(QUANTILE_LEVELS)), read only. A NaN row for a channel never read
    cache_key: str


def ask(forecaster: Forecaster, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray:
    """The forecaster's reply for the channels with a reading, checked, sorted and put back in channel order."""
    read = np.isfinite(readings).any(axis=0)
    reply = np.asarray(forecaster(readings[:, read], None if bets is None else bets[:, read]), dtype=float)
    expected = (int(read.sum()), len(QUANTILE_LEVELS))
    if reply.shape != expected:
        raise ValueError(f"the forecaster must return shape {expected}, got {reply.shape}")
    if not np.isfinite(reply).all():
        raise ValueError("the forecaster returned a quantile that is not finite")
    quantiles = np.full((readings.shape[1], len(QUANTILE_LEVELS)), np.nan)
    quantiles[read] = np.sort(reply, axis=1)
    return quantiles


@dataclass(frozen=True)
class ForecastPolicy:
    """The record to a forecaster, its forecast to a rule. Keeps no state: the cache only saves time."""

    peeks: ClassVar[bool] = False
    rule: ForecastRule
    with_bets: bool = False
    forecaster: Forecaster = timestral

    def forecast(self, view: View) -> Forecast | None:
        """This round's forecast, from the cache when it is there. None on an empty record."""
        rows = view.record.rows
        if not rows:
            return None
        readings = np.array([[np.nan if r is None else r for r in row.readings] for row in rows], dtype=float)
        bets = np.array([row.bets for row in rows], dtype=float) if self.with_bets else None
        key = cache.cache_key(self.forecaster.key, readings, bets)
        quantiles = cache.load(key)
        if quantiles is None:
            quantiles = ask(self.forecaster, readings, bets)
            cache.save(key, quantiles)
        quantiles.setflags(write=False)
        return Forecast(quantiles, key)

    def rounded_out(self, view: View) -> bool:
        """Whether Odds rounds a channel the forecaster had not written off down to a bet of 0."""
        forecast = self.forecast(view)
        if forecast is None or not isinstance(self.rule, Odds):
            return False
        finite = np.isfinite(forecast.quantiles).all(axis=1)
        return any(bet == 0 and ok for bet, ok in zip(self.rule(forecast.quantiles, view.budget), finite))

    def __call__(self, view: View) -> Bets:
        forecast = self.forecast(view)
        return uniform(view) if forecast is None else self.rule(forecast.quantiles, view.budget)


TIMESTRAL_POLICIES: Mapping[str, ForecastPolicy] = MappingProxyType(
    {
        **{name: ForecastPolicy(rule) for name, rule in FORECAST_RULES.items()},
        # Each channel alone, as a joint forecast cannot tie a row of bets to its channel.
        "odds-bet-aware": ForecastPolicy(FORECAST_RULES["odds"], with_bets=True, forecaster=Timestral(joint=False)),
    }
)
