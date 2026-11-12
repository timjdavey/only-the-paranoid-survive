"""A storm: a shock into the shared factor that each channel comes back from at its own speed.

See docs/specs/engine/timeline.md#storm. A shock is a storm that passes. A storm switch is a fall that arrives
in one, so its first rounds match the shock's on the same seed.
"""

import math
from dataclasses import dataclass

import numpy as np

from .draws import sized
from .specs import ShockSpec
from .world import World


@dataclass(frozen=True)
class Storm:
    depth: float
    left: np.ndarray  # (rows from onset, channels). The share of the storm left on each channel, 1 at the trough
    trough: int  # rows from onset to the trough
    pop_rise: float | None  # what the pop adds at the trough, None with no pop
    recovery: tuple[float, ...]  # each channel's half-life multiplier, after any leader_last swap

    def lift(self, channel: int) -> np.ndarray:
        """0 up to the trough, then 1 minus the share left on the channel, so it climbs towards 1 as the storm lifts."""
        lifted = 1.0 - self.left[:, channel]
        lifted[: self.trough + 1] = 0.0
        return lifted


def impulse(profile: str, depth: float, half_life: int, rows: int, recovery: float = 1.0) -> np.ndarray:
    """The impulse from the onset row on, `rows` long. `recovery` multiplies the half-life of the rebound."""
    length = max(rows, half_life + 1)
    series = [0.0] * length
    if profile == "sharp":
        series[0] = -depth
        first_rebound, decay = 1, 2.0 ** (-1.0 / (half_life * recovery))
    else:
        for j in range(half_life + 1):
            series[j] = -depth * ((j + 1) / (half_life + 1))
        first_rebound, decay = half_life + 1, 2.0 ** (-1.0 / (math.ceil(half_life / 2) * recovery))
    for t in range(first_rebound, length):
        series[t] = series[t - 1] * decay
    return np.array(series[:rows])


def capped_depth(world: World, spec: ShockSpec, depth_drawn: float, row: int, leader: int, met: float) -> float:
    """Keep the hedge at least the margin below the leader at the trough, or above it with the knob on.

    `met` is the loading the leader meets the storm with: its own, or its `leader_loading` draw.
    """
    config, hedge = world.config, world.ladder.hedge
    margin = config.hedge_margin_points
    base_gap = float(world.base[row, leader] - world.base[row, hedge])
    slope = float(met - world.loadings[row, hedge])
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


def before_weather(world: World, row: int) -> np.ndarray:
    """Every channel's level from `row` on, before weather: base + loadings × shock impulses + impulse."""
    return world.base[row:] + world.loadings[row:] * world.shock[row:, None] + world.impulse[row:]


def recoveries(draws: dict, leader: int) -> list[float]:
    """Each channel's half-life multiplier. With `leader_last`, the leader swaps with the slowest."""
    recovery = list(draws["recovery"])
    if draws["leader_last"]:
        slowest = int(np.argmax(recovery))
        recovery[leader], recovery[slowest] = recovery[slowest], recovery[leader]
    return recovery


def apply_storm(world: World, spec: ShockSpec, draws: dict, row: int, leader: int) -> Storm:
    """Add the storm from `row` on, in the spec's order: the shared impulse, each channel's part, the pop, the lead."""
    profile, half_life, rows = draws["profile"], draws["half_life"], world.rows - row
    own_loading, met = float(world.loadings[row, leader]), draws["leader_loading"]
    depth = capped_depth(world, spec, draws["depth_drawn"], row, leader, own_loading if met is None else met)
    shared = impulse(profile, depth, half_life, rows)
    world.shock[row:] += shared
    left = np.tile(shared / -depth, (world.config.channels, 1)).T
    recovery_of = recoveries(draws, leader)
    for channel, recovery in enumerate(recovery_of):
        if recovery != 1.0:
            own = impulse(profile, depth, half_life, rows, recovery)
            world.impulse[row:, channel] += world.loadings[row, channel] * (own - shared)
            left[:, channel] = own / -depth
    if met is not None:
        world.impulse[row:, leader] += (met - own_loading) * -depth * left[:, leader]
    trough = half_life if profile == "slide" else 0
    pop_rise = None
    if draws["pop"]:
        pop = draws["pop_channel"]
        at_trough = before_weather(world, row + trough)[0]
        pop_rise = float(at_trough[leader] - world.config.hedge_margin_points - at_trough[pop])
        world.impulse[row:, pop] += pop_rise * left[:, pop]
    if spec.leader_stays_ahead:
        levels = before_weather(world, row)
        over = levels - (levels[:, [leader]] - world.config.hedge_margin_points)
        over[:, leader] = 0.0
        world.impulse[row:] -= np.maximum(over, 0.0)
    return Storm(depth, left, trough, pop_rise, tuple(recovery_of))
