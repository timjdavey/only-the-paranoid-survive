"""Stub policies and helpers for the engine suite, see docs/specs/engine/tests.md#stub-policies.

The engine suite may not import the baselines layer, so these are as plain as a policy can be.
"""

import dataclasses
from typing import ClassVar

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, Bets, Timeline, View, make_timeline, split_budget


@dataclasses.dataclass(frozen=True)
class OnFirst:
    """The whole budget on channel 0."""

    peeks: ClassVar[bool] = False

    def __call__(self, view: View) -> Bets:
        return (view.budget,) + (0,) * (view.channels - 1)


@dataclasses.dataclass(frozen=True)
class Even:
    """split_budget([1] × channels, budget)."""

    peeks: ClassVar[bool] = False

    def __call__(self, view: View) -> Bets:
        return split_budget([1] * view.channels, view.budget)


@pytest.fixture(scope="session")
def on_first() -> OnFirst:
    return OnFirst()


@pytest.fixture(scope="session")
def even() -> Even:
    return Even()


@pytest.fixture
def timeline() -> Timeline:
    return make_timeline(SCENARIOS["no_change"], 0)


@pytest.fixture(scope="session")
def hand_built():
    """Replace arrays on a timeline, kept read only like the real ones."""

    def build(timeline: Timeline, **arrays: np.ndarray) -> Timeline:
        frozen = {}
        for name, array in arrays.items():
            array = np.array(array, dtype=float)
            array.setflags(write=False)
            frozen[name] = array
        return dataclasses.replace(timeline, **frozen)

    return build
