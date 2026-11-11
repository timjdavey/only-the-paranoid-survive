"""Timestral, the default forecaster. See docs/specs/forecasters/timestral.md.

The Timestral package is imported inside `load` and brings torch with it, so importing this module imports neither.
"""

from dataclasses import dataclass
from functools import cache
from importlib.util import find_spec
from typing import Any

import numpy as np

from paranoid.baselines import QUANTILE_LEVELS

TIMESTRAL_MODEL = "mistralai/Timestral-209M"
TIMESTRAL_REVISION = "9874d252ab0aae16f7f7c999f98f98d6ad7d8365"


def require_timestral() -> None:
    """ImportError naming the extra when torch or Timestral is missing. Imports neither."""
    missing = [name for name in ("torch", "timestral") if find_spec(name) is None]
    if missing:
        raise ImportError(f"{' and '.join(missing)} not installed, run `uv sync --extra timestral`")


@cache
def load(model: str, revision: str) -> Any:
    """The model on CPU, one per process for each model and revision."""
    require_timestral()
    from timestral import TimestralForecaster

    forecaster = TimestralForecaster.from_pretrained(model, device="cpu", revision=revision)
    if tuple(forecaster.quantile_levels) != QUANTILE_LEVELS:
        raise ValueError(f"{model} reports quantile levels {forecaster.quantile_levels}, not QUANTILE_LEVELS")
    return forecaster


@dataclass(frozen=True)
class Timestral:
    """Next round's quantiles per channel, forecast jointly or each channel alone."""

    joint: bool = True
    model: str = TIMESTRAL_MODEL
    revision: str = TIMESTRAL_REVISION

    @property
    def key(self) -> str:
        return f"{self.model}@{self.revision}/{'joint' if self.joint else 'separate'}"

    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray:
        if self.joint and bets is not None:
            raise ValueError("a joint forecast cannot tie a row of bets to its channel, use Timestral(joint=False)")
        require_timestral()
        forecaster = load(self.model, self.revision)
        context = np.ascontiguousarray(np.asarray(readings, dtype=np.float32).T)  # (read, rounds)
        if self.joint:
            reply = forecaster.forecast(context[None], prediction_length=1)
        else:
            past = None if bets is None else np.ascontiguousarray(np.asarray(bets, dtype=np.float32).T)[:, None, :]
            reply = forecaster.forecast(context[:, None, :], prediction_length=1, past_covariates=past)
        # (series, variates, 1, levels): drop the horizon, one row per channel.
        return reply.quantiles[..., 0, :].reshape(len(context), -1).numpy().astype(float)


timestral = Timestral()
