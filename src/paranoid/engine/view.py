"""What a policy sees, what it is handed, what it is, and split_budget.

See docs/specs/engine/view.md. Never imports game.py, which imports this.
"""

import math
import numbers
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol

from .record import Bets, Record
from .specs import Range
from .timeline import Timeline


@dataclass(frozen=True)
class Start:
    """The ladder on round 1. Handed to the baselines, never to a model."""

    leader: int
    runner_up: int
    hedge: int
    field: tuple[int, ...]


@dataclass(frozen=True)
class Dials:
    """The release constants, copied from the config. Handed to the baselines, never to a model."""

    rounds: int
    own_scale: float
    persistence: float
    factor_scale: float
    read_noise_k: float
    leader_base: Range
    runner_up_gap_points: Range
    field_base: Range
    hedge_base: Range


@dataclass(frozen=True)
class View:
    round: int  # the round about to be played, from 1
    channels: int
    budget: int
    start: Start
    dials: Dials
    record: Record  # every round before this one
    timeline: Timeline | None  # the timeline for peeking policies, else None


class Policy(Protocol):
    peeks: bool  # True if it may read the timeline

    def __call__(self, view: View) -> Bets: ...


def as_fraction(weight: float) -> Fraction:
    if isinstance(weight, numbers.Integral):
        return Fraction(int(weight))
    value = float(weight)
    if not math.isfinite(value):
        raise ValueError(f"every weight must be finite, got {weight!r}")
    return Fraction(value)


def split_budget(weights: Sequence[float], budget: int) -> Bets:
    """Largest remainder: floors first, then one point each to the largest remainders, lowest index on a tie."""
    exact = [as_fraction(w) for w in weights]
    if any(w < 0 for w in exact):
        raise ValueError("no weight may be negative")
    total = sum(exact, Fraction(0))
    if total == 0:
        raise ValueError("the weights must have a positive sum")
    shares = [w / total * budget for w in exact]
    floors = [math.floor(share) for share in shares]
    leftover = budget - sum(floors)
    by_remainder = sorted(range(len(shares)), key=lambda c: (-(shares[c] - floors[c]), c))
    for channel in by_remainder[:leftover]:
        floors[channel] += 1
    return tuple(floors)
