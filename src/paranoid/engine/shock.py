"""A shock: a storm that passes, or with the hard-variant knob an impulse into one channel.

See docs/specs/engine/timeline.md#shock.
"""

from .specs import ShockSpec
from .storm import apply_storm, impulse
from .world import World


def storm_numbers(storm) -> dict:
    """The derived keys a storm adds to `Event.numbers`."""
    return {"depth": storm.depth, "pop_rise": storm.pop_rise, "recovery": storm.recovery}


def apply_shock(world: World, spec: ShockSpec, draws: dict, onset: int, earlier) -> tuple:
    row = onset - 1
    leader = world.leader_at(row)
    if world.config.one_channel_shock:
        depth = draws["depth_drawn"]
        world.impulse[row:, leader] += impulse(draws["profile"], depth, draws["half_life"], world.rows - row)
        return leader, None, {"depth": depth, "pop_rise": None}
    return None, None, storm_numbers(apply_storm(world, spec, draws, row, leader))
