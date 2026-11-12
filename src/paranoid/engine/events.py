"""Event, each shape's draws, onsets and no two alike.

See docs/specs/engine/timeline.md#events, #draw-order and #no-two-alike.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal

import numpy as np

from .config import ScenarioConfig
from .draws import chance, either, pick, pick_with, sized, uniform, whole
from .drift import apply_drift
from .shock import apply_shock
from .specs import SHAPES, DriftSpec, EventSpec, ShockSpec, SwitchSpec
from .switch import apply_switch
from .world import World

MAX_TRIES = 100

Numbers = Mapping[str, float | int | str | tuple[float, ...] | None]


@dataclass(frozen=True)
class Event:
    shape: Literal["shock", "switch", "drift"]
    onset: int  # first round it edits, from 1
    channel: int | None  # the channel that moved down, else None
    sleeper: int | None  # the channel that rose, if one did
    numbers: Numbers = field(hash=False)  # every per-seed draw by name


@dataclass(frozen=True)
class Draws:
    values: dict[str, float | int | str]  # the draws no two alike compares
    widths: dict[str, float]  # the range width in level points of each float draw
    extras: dict[str, object] = field(default_factory=dict)  # draws no two alike leaves out, see storm


STORM_DRAWS = ("gap", "profile", "depth_drawn", "half_life")
STORM_DRAWS += ("recovery", "leader_last", "pop", "pop_channel", "leader_loading")
STORM_DERIVED = ("depth", "pop_rise")


def draw_storm(rng: np.random.Generator, spec: ShockSpec, config: ScenarioConfig) -> tuple[Draws, float]:
    """A shock's draws, then the shape knobs' draws. Returns the uniform that picks the pop once the onset is known."""
    depth_range, scale = sized(spec.depth_sigmas, spec.depth_points, config.own_scale, config.pin_in_level_points)
    values = {
        "gap": whole(rng, spec.gap),
        "profile": either(rng, spec.profile, "sharp", "slide"),
        "depth_drawn": uniform(rng, depth_range, scale),
        "half_life": whole(rng, spec.half_life),
    }
    extras = {
        "recovery": tuple(uniform(rng, spec.recovery) for _ in range(config.channels)),
        "leader_last": 1 if chance(rng, spec.leader_last_share) else 0,
        "pop": 1 if chance(rng, spec.pop_share) else 0,
    }
    pop_u = rng.random()
    met = uniform(rng, spec.leader_loading or (0.0, 0.0))  # drawn even when off, as every draw is
    extras["leader_loading"] = None if spec.leader_loading is None else met
    return Draws(values, {"depth_drawn": width(depth_range, scale)}, extras), pop_u


def pop_channel(draws: Draws, u: float, sleepers: set[int]) -> int | None:
    """The channel that pops, from the same set a sleeper is drawn from, or None with no pop."""
    return pick_with(u, sleepers) if draws.extras["pop"] else None


def draw_shock(rng: np.random.Generator, spec: ShockSpec, config: ScenarioConfig, sleepers) -> Draws:
    draws, u = draw_storm(rng, spec, config)
    draws.extras["pop_channel"] = pop_channel(draws, u, sleepers(draws.values["gap"]))
    return draws


def draw_switch(rng: np.random.Generator, spec: SwitchSpec, config: ScenarioConfig, sleepers) -> Draws:
    storm = draw_storm(rng, spec.storm, config) if spec.storm is not None else None
    scale_args = (config.own_scale, config.pin_in_level_points)
    size_range, size_scale = sized(spec.size_sigmas, spec.size_points, *scale_args)
    rise_range, rise_scale = sized(spec.rise_sigmas, spec.rise_points, *scale_args)
    gap = whole(rng, spec.gap)
    u = rng.random()
    if spec.kind == "draw":
        kind = "fall_and_rise" if u < spec.riser_share else "fall"
    else:
        kind = spec.kind
    values = {
        "gap": gap,
        "kind": kind,
        "size": uniform(rng, size_range, size_scale),
        "rise": uniform(rng, rise_range, rise_scale),
        "ramp": whole(rng, spec.ramp),
        "sleeper": pick(rng, sleepers(gap)),
        "sleeper_loading": uniform(rng, config.loading),
        "short": 1 if chance(rng, spec.short_share) else 0,
        "short_level": uniform(rng, spec.short_level),
    }
    widths = {
        "size": width(size_range, size_scale),
        "rise": width(rise_range, rise_scale),
        "sleeper_loading": width(config.loading),
        "short_level": width(spec.short_level),
    }
    extras: dict[str, object] = {f"storm_{key}": None for key in STORM_DRAWS}
    if storm is not None:
        storm_draws, pop_u = storm
        storm_draws.extras["pop_channel"] = pop_channel(storm_draws, pop_u, sleepers(gap))
        extras = {f"storm_{key}": value for key, value in {**storm_draws.values, **storm_draws.extras}.items()}
    return Draws(values, widths, extras)


def draw_drift(rng: np.random.Generator, spec: DriftSpec, config: ScenarioConfig, _sleepers) -> Draws:
    size_range, scale = sized(spec.size_sigmas, spec.size_points, config.own_scale, config.pin_in_level_points)
    values = {
        "gap": whole(rng, spec.gap),
        "profile": either(rng, spec.profile, "linear", "logistic"),
        "size": uniform(rng, size_range, scale),
        "length": whole(rng, spec.length),
    }
    return Draws(values, {"size": width(size_range, scale)})


DRAWS = {"shock": draw_shock, "switch": draw_switch, "drift": draw_drift}
APPLY = {"shock": apply_shock, "switch": apply_switch, "drift": apply_drift}


def width(bounds: tuple[float, float], scale: float = 1.0) -> float:
    return (bounds[1] - bounds[0]) * scale


def differences(previous: Numbers, draws: Draws) -> int:
    """How many draws differ from the previous event of the shape, gap excluded."""
    count = 0
    for key, value in draws.values.items():
        if key == "gap":
            continue
        if key in draws.widths:
            spread = draws.widths[key]
            count += spread > 0 and abs(value - previous[key]) >= 0.1 * spread
        else:
            count += value != previous[key]
    return count


def draw_until_different(
    rng: np.random.Generator,
    spec: EventSpec,
    config: ScenarioConfig,
    previous: Numbers | None,
    sleepers: Callable[[int], set[int]],
) -> tuple[Draws, int]:
    draw = DRAWS[SHAPES[type(spec)]]
    for tries in range(1, MAX_TRIES + 1):
        draws = draw(rng, spec, config, sleepers)
        if previous is None or differences(previous, draws) >= 2:
            return draws, tries
    raise ValueError(f"no two alike: event still matched the one before after {MAX_TRIES} tries")


def apply_events(world: World, rngs: Sequence[np.random.Generator], first_onset: int) -> tuple[Event, ...]:
    """Draw and apply each event in order, each from its own stream."""
    config, events = world.config, []
    for index, (spec, rng) in enumerate(zip(config.events, rngs, strict=True)):
        shape = SHAPES[type(spec)]

        def onset_after(gap: int, index: int = index) -> int:
            return first_onset if index == 0 else events[-1].onset + gap

        def sleepers(gap: int) -> set[int]:
            onset = onset_after(gap)
            moved = {c for e in events for c in (e.channel, e.sleeper) if c is not None}
            ruled_out = moved | {world.ladder.hedge, world.leader_at(onset - 1)}
            return set(world.ladder.field) - ruled_out

        previous = next((e.numbers for e in reversed(events) if e.shape == shape), None)
        draws, tries = draw_until_different(rng, spec, config, previous, sleepers)
        onset = onset_after(draws.values["gap"])
        channel, sleeper, derived = APPLY[shape](world, spec, {**draws.values, **draws.extras}, onset, events)
        numbers = MappingProxyType({**draws.values, **draws.extras, **derived, "tries": tries})
        events.append(Event(shape, onset, channel, sleeper, numbers))
    return tuple(events)
