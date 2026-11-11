"""The four fixed baselines with no parameters. See docs/specs/baselines/policies.md."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from paranoid.engine import Bets, View, split_budget


def all_on(channel: int, view: View) -> Bets:
    """`budget` on one channel, 0 elsewhere."""
    return tuple(view.budget if c == channel else 0 for c in range(view.channels))


@dataclass(frozen=True)
class Uniform:
    """The floor: the budget split evenly, whatever the view."""

    peeks: ClassVar[bool] = False

    def __call__(self, view: View) -> Bets:
        return split_budget([1] * view.channels, view.budget)


@dataclass(frozen=True)
class Discerning:
    """The yardstick: `budget` on the highest base level this round."""

    peeks: ClassVar[bool] = True

    def __call__(self, view: View) -> Bets:
        return all_on(view.timeline.climate_leader(view.round), view)


@dataclass(frozen=True)
class Complacent:
    """`budget` on the round 1 leader, every round."""

    peeks: ClassVar[bool] = False

    def __call__(self, view: View) -> Bets:
        return all_on(view.start.leader, view)


@dataclass(frozen=True)
class Perfect:
    """`budget` on the highest level this round, weather and all."""

    peeks: ClassVar[bool] = True

    def __call__(self, view: View) -> Bets:
        return all_on(int(np.argmax(view.timeline.levels[view.round - 1])), view)


uniform = Uniform()
discerning = Discerning()
complacent = Complacent()
perfect = Perfect()
