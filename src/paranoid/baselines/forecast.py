"""Forecast rules: a forecast's quantiles into a split. See docs/specs/baselines/forecast.md."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Protocol

import numpy as np

from paranoid.engine import Bets, split_budget

QUANTILE_LEVELS: tuple[float, ...] = (
    0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
    0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99,
)  # fmt: skip
MEDIAN_INDEX = 10
ODDS_DRAWS = 1000


class ForecastRule(Protocol):
    def __call__(self, quantiles: np.ndarray, budget: int) -> Bets: ...


@lru_cache(maxsize=32)
def fixed_draws(seed: int, draws: int, channels: int, normals: int) -> tuple[np.ndarray, ...]:
    """One `random((draws, channels))` then `normals` of `standard_normal`, from `default_rng(seed)`. Drawn once, read only."""
    rng, shape = np.random.default_rng(seed), (draws, channels)
    arrays = (rng.random(shape), *(rng.standard_normal(shape) for _ in range(normals)))
    for array in arrays:
        array.setflags(write=False)
    return arrays


def checked(quantiles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The array as floats and which rows are finite, or ValueError for a bad array."""
    q = np.asarray(quantiles, dtype=float)
    if q.ndim != 2 or q.shape[1] != len(QUANTILE_LEVELS):
        raise ValueError(f"quantiles must have shape (channels, {len(QUANTILE_LEVELS)}), got {q.shape}")
    finite = np.isfinite(q).all(axis=1)
    blank = np.isnan(q).all(axis=1)
    if not (finite | blank).all():
        raise ValueError("every quantile row must be all finite or all NaN")
    if not finite.any():
        raise ValueError("every channel is NaN, so there is nothing to forecast from")
    if (np.diff(q[finite], axis=1) < 0).any():
        raise ValueError("every finite quantile row must be ascending")
    return q, finite


def top_of(quantiles: np.ndarray) -> int:
    """The channel with the highest median, NaN rows lowest, lowest index on a tie."""
    q, finite = checked(quantiles)
    return int(np.argmax(np.where(finite, q[:, MEDIAN_INDEX], -np.inf)))


@dataclass(frozen=True)
class TopPick:
    """`budget` on the highest median."""

    def __call__(self, quantiles: np.ndarray, budget: int) -> Bets:
        top = top_of(quantiles)
        return tuple(budget if c == top else 0 for c in range(len(quantiles)))


@dataclass(frozen=True)
class TopPickWithExploreBets:
    """`explore` on every channel but the top pick, the rest on it."""

    explore: int

    def __post_init__(self) -> None:
        if self.explore < 1:
            raise ValueError(f"explore must be at least 1, got {self.explore}")

    def __call__(self, quantiles: np.ndarray, budget: int) -> Bets:
        top, channels = top_of(quantiles), len(quantiles)
        if self.explore * (channels - 1) >= budget:
            raise ValueError(f"explore {self.explore} on {channels - 1} channels leaves nothing of {budget}")
        return tuple(budget - self.explore * (channels - 1) if c == top else self.explore for c in range(channels))


@dataclass(frozen=True)
class Odds:
    """The budget in proportion to each channel's chance of being highest."""

    draws: int = ODDS_DRAWS

    def __post_init__(self) -> None:
        if self.draws < 1:
            raise ValueError(f"draws must be at least 1, got {self.draws}")

    def __call__(self, quantiles: np.ndarray, budget: int) -> Bets:
        q, finite = checked(quantiles)
        channels = len(q)
        (levels,) = fixed_draws(0, self.draws, channels, 0)
        values = np.full((self.draws, channels), -np.inf)
        for c in np.flatnonzero(finite):
            values[:, c] = np.interp(levels[:, c], QUANTILE_LEVELS, q[c])
        wins = np.bincount(np.argmax(values, axis=1), minlength=channels)
        return split_budget([int(w) for w in wins], budget)


top_pick = TopPick()
odds = Odds()
explore_1 = TopPickWithExploreBets(1)
explore_2 = TopPickWithExploreBets(2)
explore_5 = TopPickWithExploreBets(5)

FORECAST_RULES: Mapping[str, ForecastRule] = MappingProxyType(
    {"top-pick": top_pick, "odds": odds, "explore-1": explore_1, "explore-2": explore_2, "explore-5": explore_5}
)
