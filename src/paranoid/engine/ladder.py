"""The order, the ladder and the loadings, row 0 of base and loadings.

See docs/specs/engine/timeline.md#the-ladder and #loadings.
"""

from dataclasses import dataclass

import numpy as np

from .config import ScenarioConfig
from .draws import sized, uniform


@dataclass(frozen=True)
class Ladder:
    leader: int
    runner_up: int
    hedge: int
    field: tuple[int, ...]  # the other channels in drawn order, the hedge last
    base: np.ndarray  # (channels,), row 0 of base


def draw_ladder(rng: np.random.Generator, config: ScenarioConfig) -> Ladder:
    order = [int(c) for c in rng.permutation(config.channels)]
    leader, runner_up, hedge, field = order[0], order[1], order[-1], tuple(order[2:])
    gap_range, scale = sized(
        config.runner_up_gap_sigmas,
        config.runner_up_gap_points,
        config.own_scale,
        config.pin_in_level_points,
    )
    base = np.zeros(config.channels)
    leader_base = uniform(rng, config.leader_base)
    runner_up_base = leader_base - uniform(rng, gap_range, scale)
    base[leader], base[runner_up] = leader_base, runner_up_base
    low, high = config.field_base
    top = min(high, runner_up_base - config.field_headroom)
    if top < low:
        raise ValueError(f"no room for the field below the runner-up: {top} is below {low}")
    for channel in field[:-1]:
        base[channel] = uniform(rng, (low, top))
    base[hedge] = uniform(rng, config.hedge_base)
    return Ladder(leader, runner_up, hedge, field, base)


def draw_loadings(rng: np.random.Generator, config: ScenarioConfig, hedge: int) -> np.ndarray:
    """One loading per channel in index order, then the hedge's overwritten."""
    loadings = np.array([uniform(rng, config.loading) for _ in range(config.channels)])
    loadings[hedge] = uniform(rng, config.hedge_loading)
    return loadings
