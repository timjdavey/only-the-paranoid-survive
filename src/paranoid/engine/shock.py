"""A shock: an impulse that decays, into the shared factor or one channel.

See docs/specs/engine/timeline.md#shock.
"""

import math

import numpy as np

from .draws import sized
from .specs import ShockSpec
from .world import World


def impulse(profile: str, depth: float, half_life: int, rows: int) -> np.ndarray:
    """The impulse from the onset row on, `rows` long."""
    length = max(rows, half_life + 1)
    series = [0.0] * length
    if profile == "sharp":
        series[0] = -depth
        first_rebound, decay = 1, 2.0 ** (-1.0 / half_life)
    else:
        for j in range(half_life + 1):
            series[j] = -depth * ((j + 1) / (half_life + 1))
        first_rebound, decay = half_life + 1, 2.0 ** (-1.0 / math.ceil(half_life / 2))
    for t in range(first_rebound, length):
        series[t] = series[t - 1] * decay
    return np.array(series[:rows])


def capped_depth(world: World, spec: ShockSpec, depth_drawn: float, row: int, leader: int) -> float:
    """Keep the hedge at least the margin below the leader at the trough, or above it with the knob on."""
    config, hedge = world.config, world.ladder.hedge
    margin = config.hedge_margin_points
    base_gap = float(world.base[row, leader] - world.base[row, hedge])
    slope = float(world.loadings[row, leader] - world.loadings[row, hedge])
    if leader == hedge or slope <= 0:
        raise ValueError("the hedge must load below the leader for the shock cap to hold")
    if not config.hedge_may_overtake:
        cap = (base_gap - margin) / slope
        if cap <= 0:
            raise ValueError(f"the hedge already sits within {margin} points of the leader")
        return min(depth_drawn, cap)
    needed = (base_gap + margin) / slope
    depth_range, scale = sized(spec.depth_sigmas, spec.depth_points, config.own_scale, config.pin_in_level_points)
    limit = depth_range[1] * scale
    if needed > limit:
        raise ValueError(f"the hedge needs a depth of {needed} to overtake, above the range's high of {limit}")
    return max(depth_drawn, needed)


def apply_shock(world: World, spec: ShockSpec, draws: dict, onset: int, earlier) -> tuple:
    row = onset - 1
    leader = world.leader_at(row)
    one_channel = world.config.one_channel_shock
    depth = draws["depth_drawn"] if one_channel else capped_depth(world, spec, draws["depth_drawn"], row, leader)
    series = impulse(draws["profile"], depth, draws["half_life"], world.rows - row)
    if one_channel:
        world.impulse[row:, leader] += series
        return leader, None, {"depth": depth}
    world.shock[row:] += series
    return None, None, {"depth": depth}
