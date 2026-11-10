"""A drift: the leader's slow fall to below the second. See docs/specs/engine/timeline.md#drift."""

import math

import numpy as np

from .specs import DriftSpec
from .switch import fall_below_second, require_leader_above_zero
from .world import World


def drift_steps(profile: str, length: int, rows: int) -> np.ndarray:
    """The share of the fall done at each row from the onset on, 1 from row length − 1."""
    if profile == "linear":
        return np.minimum(1.0, (np.arange(rows) + 1) / length)

    def g(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-(8.0 / length) * (x - length / 2.0)))

    start, span = g(0), g(length) - g(0)
    return np.array([1.0 if j + 1 >= length else (g(j + 1) - start) / span for j in range(rows)])


def apply_drift(world: World, spec: DriftSpec, draws: dict, onset: int, earlier) -> tuple:
    row, length = onset - 1, draws["length"]
    leader = world.leader_at(row)
    steps = drift_steps(draws["profile"], length, world.rows - row)
    fall = fall_below_second(world, leader, row, draws["size"], steps)
    require_leader_above_zero(world, leader, row + length - 1)
    return leader, None, {"fall": fall}
