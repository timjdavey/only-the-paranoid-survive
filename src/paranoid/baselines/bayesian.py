"""The Bayesian baseline: a belief in the engine's family, through a forecast rule.

See docs/specs/baselines/bayesian.md. It reads its own record, the start and the dials,
never the timeline. Its state is the record replayed, which filter.py caches by the record's rows.
"""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from paranoid.engine import Bets, View

from .filter import Family, Runs, replay, sample
from .forecast import FORECAST_RULES, ODDS_DRAWS, QUANTILE_LEVELS, fixed_draws
from .lookahead import best_split

HAZARDS = (0.005, 0.01, 0.025, 0.05, 0.1)
BAYESIAN_RULES = (*FORECAST_RULES, "lookahead")
LOOKAHEAD_DRAWS = 100


def read_only(array: np.ndarray) -> np.ndarray:
    array = np.ascontiguousarray(array, dtype=float).copy()
    array.setflags(write=False)
    return array


@dataclass(frozen=True, eq=False)
class Belief:
    """The predictive for view.round, one entry per channel."""

    mean: np.ndarray
    sd: np.ndarray
    changed: np.ndarray  # chance the base has jumped since round 1
    quantiles: np.ndarray  # (channels, len(QUANTILE_LEVELS)), ascending along the last axis


@dataclass(frozen=True)
class Bayesian:
    """A run-length filter per channel over its own readings, through one of BAYESIAN_RULES."""

    peeks: ClassVar[bool] = False
    hazard: float = 0.025
    rule: str = "odds"
    draws: int = ODDS_DRAWS
    lookahead_draws: int = LOOKAHEAD_DRAWS

    def __post_init__(self) -> None:
        if not 0 < self.hazard < 1:
            raise ValueError(f"hazard must lie strictly inside (0, 1), got {self.hazard}")
        if self.rule not in BAYESIAN_RULES:
            raise ValueError(f"rule must be one of {BAYESIAN_RULES}, got {self.rule!r}")
        if self.draws < 1 or self.lookahead_draws < 1:
            raise ValueError("draws and lookahead_draws must be at least 1")

    def __call__(self, view: View) -> Bets:
        if view.round == 1:
            return tuple(view.budget if c == view.start.leader else 0 for c in range(view.channels))
        family = Family.of(view, self.hazard)
        runs = replay(view.record, family)
        belief = self.belief_of(runs)
        if self.rule != "lookahead":
            return FORECAST_RULES[self.rule](belief.quantiles, view.budget)
        candidates = list(dict.fromkeys(rule(belief.quantiles, view.budget) for rule in FORECAST_RULES.values()))
        return best_split(view, runs, family, belief.mean, candidates, self.lookahead_draws)

    def belief(self, view: View) -> Belief:
        return self.belief_of(replay(view.record, Family.of(view, self.hazard)))

    def belief_of(self, runs: Runs) -> Belief:
        mean, var = runs.mixture()
        picks, normals = fixed_draws(0, self.draws, len(mean), 1)  # picks drawn first, as bayesian.md#the-belief pins
        samples = sample(runs, picks, normals)
        quantiles = np.quantile(samples, QUANTILE_LEVELS, axis=0).T
        changed = np.clip(1 - runs.weight[:, 0], 0.0, 1.0)
        return Belief(
            mean=read_only(mean),
            sd=read_only(np.sqrt(var)),
            changed=read_only(changed),
            quantiles=read_only(quantiles),
        )


bayesian = Bayesian()
