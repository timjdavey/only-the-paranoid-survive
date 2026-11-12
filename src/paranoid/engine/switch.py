"""A switch: a fall, a rise, both, or an undo. See docs/specs/engine/timeline.md#switch."""

import numpy as np

from .shock import storm_numbers
from .specs import SwitchSpec
from .storm import apply_storm
from .world import World

STORM_KEYS = ("profile", "depth_drawn", "half_life", "recovery", "leader_last", "pop", "pop_channel")


def ramp_steps(ramp: int, rows: int) -> np.ndarray:
    """f(t) = min(1, (t − onset + 1) / ramp), from the onset row on."""
    return np.minimum(1.0, (np.arange(rows) + 1) / ramp)


def move_to(world: World, channel: int, row: int, end: float, ramp: int) -> None:
    """A straight line from the channel's base at the onset row to `end`, then `end` exactly."""
    start = float(world.base[row, channel])
    steps = ramp_steps(ramp, ramp - 1)
    world.base[row : row + ramp - 1, channel] = start + (end - start) * steps
    world.base[row + ramp - 1 :, channel] = end


def fall_below_second(world: World, leader: int, row: int, size: float, steps: np.ndarray) -> float:
    """Move the leader's base to `size` below the second channel's at the onset row. Returns the fall."""
    second = world.highest_at(row, {leader})
    fall = float(world.base[row, leader] - world.base[row, second] + size)
    world.base[row:, leader] -= fall * steps
    return fall


def require_leader_above_zero(world: World, leader: int, end_row: int) -> None:
    if world.base[end_row, leader] <= 0:
        raise ValueError("the event would leave the leader's base at or below 0, so the config is wrong")


def undo(world: World, draws: dict, row: int, earlier) -> tuple:
    switches = [event for event in earlier if event.shape == "switch"]
    sleeper = switches[-1].sleeper
    start, end = float(world.base[row, sleeper]), float(world.base[0, sleeper])
    move_to(world, sleeper, row, end, draws["ramp"])
    world.loadings[row:, sleeper] = world.loadings[0, sleeper]
    return sleeper, None, {"fall": start - end, "target": end}


def storm_switch(world: World, spec: SwitchSpec, draws: dict, row: int) -> tuple:
    """A fall that arrives in a storm. The leader's base falls, and any sleeper's rises, as the storm lifts off each."""
    leader = world.leader_at(row)
    storm_draws = {key: draws[f"storm_{key}"] for key in STORM_KEYS}
    storm = apply_storm(world, spec.storm, storm_draws, row, leader)
    derived = {f"storm_{key}": value for key, value in storm_numbers(storm).items()}
    second = world.highest_at(row, {leader})
    ends = world.base[row].copy()
    fall = float(ends[leader] - ends[second] + draws["size"])
    world.base[row:, leader] -= fall * storm.lift(leader)
    ends[leader] -= fall
    if ends[leader] <= 0:
        raise ValueError("the event would leave the leader's base at or below 0, so the config is wrong")
    sleeper = target = None
    if draws["kind"] == "fall_and_rise":
        sleeper = draws["storm_pop_channel"] if draws["storm_pop"] else draws["sleeper"]
        target = float(np.delete(ends, sleeper).max() + draws["rise"])
        world.base[row:, sleeper] += (target - ends[sleeper]) * storm.lift(sleeper)
    return leader, sleeper, {"fall": fall, "target": target, **derived}


def apply_switch(world: World, spec: SwitchSpec, draws: dict, onset: int, earlier) -> tuple:
    row = onset - 1
    if spec.storm is not None:
        return storm_switch(world, spec, draws, row)
    channel, sleeper, derived = quiet_switch(world, draws, row, earlier)
    return channel, sleeper, {**derived, "storm_depth": None, "storm_pop_rise": None}


def quiet_switch(world: World, draws: dict, row: int, earlier) -> tuple:
    """A switch with no storm: a straight ramp, or an undo."""
    kind, ramp = draws["kind"], draws["ramp"]
    if kind == "undo":
        return undo(world, draws, row, earlier)
    end_row = row + ramp - 1
    leader = world.leader_at(row)
    channel = sleeper = fall = target = None
    if kind in ("fall", "fall_and_rise"):
        fall = fall_below_second(world, leader, row, draws["size"], ramp_steps(ramp, world.rows - row))
        require_leader_above_zero(world, leader, end_row)
        channel = leader
    if kind in ("rise", "fall_and_rise"):
        sleeper = draws["sleeper"]
        ends = world.base[end_row]
        if draws["short"]:
            below = world.highest_at(end_row, {leader, sleeper})
            target = float(ends[below] + draws["short_level"] * (ends[leader] - ends[below]))
        else:
            target = float(np.delete(ends, sleeper).max() + draws["rise"])
        move_to(world, sleeper, row, target, ramp)
        world.loadings[row:, sleeper] = draws["sleeper_loading"]
    return channel, sleeper, {"fall": fall, "target": target}
