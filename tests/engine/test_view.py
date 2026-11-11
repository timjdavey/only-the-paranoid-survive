"""EV1 to EV3, see docs/specs/engine/tests.md#view."""

import dataclasses
import math
from typing import ClassVar

import pytest

from paranoid.engine import SCENARIOS, Dials, View, make_timeline, play, split_budget

DIAL_NAMES = {
    "rounds", "own_scale", "persistence", "factor_scale", "read_noise_k",
    "leader_base", "runner_up_gap_points", "field_base", "hedge_base",
}


def test_ev1_split_budget():
    assert split_budget([1] * 10, 100) == (10,) * 10
    assert split_budget([1, 1, 1], 100) == (34, 33, 33)
    assert split_budget([0, 2, 0], 7) == (0, 7, 0)
    for bad in ([0, 0, 0], [1, -1, 1], [1, math.inf], [math.nan, 1]):
        with pytest.raises(ValueError):
            split_budget(bad, 100)


def test_ev2_policy_cannot_write_the_timeline(timeline):
    @dataclasses.dataclass(frozen=True)
    class Vandal:
        peeks: ClassVar[bool] = True

        def __call__(self, view: View):
            view.timeline.levels[0, 0] = 0.0
            return (view.budget,) + (0,) * (view.channels - 1)

    with pytest.raises(ValueError):
        play(Vandal(), timeline)


def test_ev3_dials():
    assert {f.name for f in dataclasses.fields(Dials)} == DIAL_NAMES

    @dataclasses.dataclass(frozen=True)
    class Checking:
        peeks: ClassVar[bool] = False

        def __call__(self, view: View):
            config = SCENARIOS[name]
            for dial in DIAL_NAMES:
                assert getattr(view.dials, dial) == getattr(config, dial)
            return split_budget([1] * view.channels, view.budget)

    for name in SCENARIOS:
        for seed in range(20):
            play(Checking(), make_timeline(SCENARIOS[name], seed))
