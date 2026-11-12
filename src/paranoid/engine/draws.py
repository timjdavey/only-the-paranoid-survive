"""The seed streams and the five draws every event and the ladder use.

See docs/specs/engine/timeline.md#seed-streams and #draws.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from .specs import IntRange, Range, is_whole

MAX_SEED = 2**64 - 1


@dataclass(frozen=True)
class Streams:
    """One generator per child of SeedSequence(seed), in the spec's order."""

    ladder: np.random.Generator
    loadings: np.random.Generator
    weather: np.random.Generator
    factor: np.random.Generator
    onset: np.random.Generator
    read_noise: np.random.Generator
    events: tuple[np.random.Generator, ...]


def make_streams(seed: int, event_count: int) -> Streams:
    """Spawn the seven streams, then one child of the events stream per event.

    A spawned child depends on its index and not on how many siblings exist, so
    event 0 draws the same numbers whatever events follow it.
    """
    if not is_whole(seed):
        raise TypeError(f"seed must be a whole number, got {seed!r}")
    if not 0 <= seed <= MAX_SEED:
        raise ValueError(f"seed must lie in [0, 2**64 - 1], got {seed}")
    children = np.random.SeedSequence(int(seed)).spawn(7)
    first_six = [np.random.default_rng(child) for child in children[:6]]
    events = tuple(np.random.default_rng(child) for child in children[6].spawn(event_count))
    return Streams(*first_six, events=events)


def sized(sigmas: Range, points: Range, own_scale: float, pinned: bool) -> tuple[Range, float]:
    """The range the engine reads for a size, and what to multiply a draw by."""
    return (points, 1.0) if pinned else (sigmas, own_scale)


def uniform(rng: np.random.Generator, bounds: Range, scale: float = 1.0) -> float:
    """Uniform from a Range: low + u × (high − low), then times scale."""
    low, high = bounds
    u = rng.random()
    return (low + u * (high - low)) * scale


def whole(rng: np.random.Generator, bounds: IntRange) -> int:
    """Uniform from an IntRange: low + floor(u × (high − low + 1))."""
    low, high = bounds
    count = high - low + 1
    return low + min(math.floor(rng.random() * count), count - 1)


def chance(rng: np.random.Generator, share: float) -> bool:
    """True when u < share."""
    return rng.random() < share


def either(rng: np.random.Generator, value: str, first: str, second: str) -> str:
    """A fixed word, or even odds between two when it is "draw". Always one draw."""
    u = rng.random()
    if value != "draw":
        return value
    return first if u < 0.5 else second


def pick(rng: np.random.Generator, channels: Iterable[int]) -> int:
    """Uniform over a set of channels, taken in index order."""
    return pick_with(rng.random(), channels)


def pick_with(u: float, channels: Iterable[int]) -> int:
    """The channel at floor(u × n) of a set taken in index order, for a draw made before the set was known."""
    ordered = sorted(channels)
    if not ordered:
        raise ValueError("the set of channels to pick from is empty, so the config is wrong")
    return ordered[min(math.floor(u * len(ordered)), len(ordered) - 1)]
