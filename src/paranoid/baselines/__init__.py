"""Every fixed baseline as a pure policy. See docs/specs/baselines/README.md."""

from .forecast import (
    FORECAST_RULES,
    MEDIAN_INDEX,
    ODDS_DRAWS,
    QUANTILE_LEVELS,
    ForecastRule,
    Odds,
    TopPick,
    TopPickWithExploreBets,
    explore_1,
    explore_2,
    explore_5,
    odds,
    top_pick,
)
from .policies import complacent, discerning, perfect, uniform

__all__ = [
    "uniform",
    "discerning",
    "complacent",
    "perfect",
    "ForecastRule",
    "QUANTILE_LEVELS",
    "MEDIAN_INDEX",
    "ODDS_DRAWS",
    "TopPick",
    "Odds",
    "TopPickWithExploreBets",
    "top_pick",
    "odds",
    "explore_1",
    "explore_2",
    "explore_5",
    "FORECAST_RULES",
]
