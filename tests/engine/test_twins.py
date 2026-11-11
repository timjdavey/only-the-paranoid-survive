"""Twin timelines and pinning: ET9 to ET11, ET21 and ET33 to ET35.

See docs/specs/engine/tests.md#timeline and timeline.md#twin-timelines.
"""

import dataclasses

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, make_timeline

SEEDS = range(100)


def pair(first: str, second: str, seed: int):
    return make_timeline(SCENARIOS[first], seed), make_timeline(SCENARIOS[second], seed)


def test_et9_one_shock_and_down_switch():
    for seed in SEEDS:
        shock, switch = pair("one_shock", "down_switch", seed)
        row = shock.events[0].onset - 1
        assert np.array_equal(shock.levels[:row], switch.levels[:row])
        assert not np.array_equal(shock.levels[row:], switch.levels[row:])


def test_et10_shock_then_switch_and_one_shock():
    for seed in SEEDS:
        both, shock = pair("shock_then_switch", "one_shock", seed)
        row = both.events[1].onset - 1
        assert np.array_equal(both.levels[:row], shock.levels[:row])


def test_et11_up_switch_and_no_change():
    for seed in SEEDS:
        up, calm = pair("up_switch", "no_change", seed)
        sleeper, row = up.sleeper, up.events[0].onset - 1
        others = [c for c in range(up.config.channels) if c != sleeper]
        assert np.array_equal(up.levels[:, others], calm.levels[:, others])
        assert np.array_equal(up.levels[:row, sleeper], calm.levels[:row, sleeper])
        assert np.all(up.levels[row:, sleeper] != calm.levels[row:, sleeper])


@pytest.mark.parametrize("name", SCENARIOS)
def test_et21_pinning(name):
    pinned = [
        dataclasses.replace(SCENARIOS[name], own_scale=scale, pin_in_level_points=True)
        for scale in (4.0, 8.0)
    ]
    for seed in range(50):
        a, b = (make_timeline(config, seed) for config in pinned)
        for array in ("base", "loadings", "impulse"):
            assert np.array_equal(getattr(a, array), getattr(b, array)), array
        assert a.events == b.events
        assert not np.array_equal(a.weather, b.weather)


def test_et33_switch_then_shock_and_down_switch():
    for seed in SEEDS:
        both, switch = pair("switch_then_shock", "down_switch", seed)
        row = both.events[1].onset - 1
        assert np.array_equal(both.levels[:row], switch.levels[:row])
        assert not np.array_equal(both.levels[row:], switch.levels[row:])


def test_et34_up_switch_then_down_switch_and_up_switch():
    shorts = 0
    for seed in SEEDS:
        both, up = pair("up_switch_then_down_switch", "up_switch", seed)
        sleeper = both.events[0].sleeper
        assert sleeper == up.events[0].sleeper
        if up.events[0].numbers["short"] == 0:
            row = both.events[1].onset - 1
            assert np.array_equal(both.levels[:row], up.levels[:row])
        else:
            shorts += 1
            others = [c for c in range(up.config.channels) if c != sleeper]
            assert np.array_equal(both.levels[:, others], up.levels[:, others])
            assert not np.array_equal(both.levels[:, sleeper], up.levels[:, sleeper])
    assert shorts > 0


def test_et35_up_switch_then_down_switch_and_no_change():
    for seed in SEEDS:
        both, calm = pair("up_switch_then_down_switch", "no_change", seed)
        undo = both.events[1]
        done = undo.onset - 1 + undo.numbers["ramp"] - 1
        assert np.array_equal(both.levels[done:], calm.levels[done:])
        assert np.array_equal(both.base[done:], calm.base[done:])
        assert np.array_equal(both.loadings[done:], calm.loadings[done:])
