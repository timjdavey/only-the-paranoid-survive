"""Drift and stringing events: ET18 to ET20, ET26 and ET36.

See docs/specs/engine/tests.md#timeline.
"""

import dataclasses

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, DriftSpec, ShockSpec, make_timeline

SEEDS = range(200)
TOLERANCE = 1e-9


def test_et18_drift():
    config = dataclasses.replace(SCENARIOS["slow_drift"], events=(DriftSpec(length=(10, 15)),))
    profiles = set()
    for seed in SEEDS:
        t = make_timeline(config, seed)
        drift = t.events[0]
        row, length, leader = drift.onset - 1, drift.numbers["length"], t.leader
        done = row + length - 1
        assert done < config.rounds
        second = int(np.argsort(t.base[row - 1])[-2])
        assert t.base[done, leader] == pytest.approx(t.base[row - 1, second] - drift.numbers["size"], abs=TOLERANCE)
        path = t.base[row - 1 : done + 1, leader]
        steps = np.diff(path)
        profiles.add(drift.numbers["profile"])
        if drift.numbers["profile"] == "linear":
            assert np.allclose(steps, -drift.numbers["fall"] / length, rtol=0, atol=TOLERANCE)
        else:
            assert np.all(steps <= 0)
        assert np.all(t.base[done:, leader] == t.base[done, leader])
    assert profiles == {"linear", "logistic"}


def test_et19_events_past_the_last_round():
    config = dataclasses.replace(
        SCENARIOS["slow_drift"], onset=(40, 40), events=(DriftSpec(), ShockSpec())
    )
    t = make_timeline(config, 0)
    drift, shock = t.events
    assert drift.onset == 40
    assert shock.onset > config.rounds
    assert t.levels.shape == (40, config.channels)
    assert t.factor.shape == (40,)
    assert t.base[39, t.leader] < t.base[38, t.leader]
    assert np.array_equal(t.base[:39], np.tile(t.base[0], (39, 1)))


def test_et20_no_two_alike_gives_up():
    fixed = ShockSpec(gap=(8, 8), depth_sigmas=(5.0, 5.0), depth_points=(20.0, 20.0), half_life=(3, 3))
    config = dataclasses.replace(SCENARIOS["one_shock"], events=(fixed, fixed))
    with pytest.raises(ValueError):
        make_timeline(config, 0)


def test_et26_gap():
    gap = SCENARIOS["shock_then_switch"].events[1].gap
    first_gap = SCENARIOS["shock_then_switch"].events[0].gap
    for seed in SEEDS:
        shock, switch = make_timeline(SCENARIOS["shock_then_switch"], seed).events
        assert gap[0] <= switch.onset - shock.onset <= gap[1]
        assert switch.onset - shock.onset == switch.numbers["gap"]
        assert first_gap[0] <= shock.numbers["gap"] <= first_gap[1]


def shock_differences(first, second, spec: ShockSpec, own_scale: float) -> int:
    width = (spec.depth_sigmas[1] - spec.depth_sigmas[0]) * own_scale
    count = first["profile"] != second["profile"]
    count += first["half_life"] != second["half_life"]
    count += abs(first["depth_drawn"] - second["depth_drawn"]) >= 0.1 * width
    return count


def test_et36_no_two_alike_redraws():
    config = dataclasses.replace(SCENARIOS["one_shock"], events=(ShockSpec(), ShockSpec()))
    redrawn = 0
    for seed in SEEDS:
        first, second = make_timeline(config, seed).events
        assert shock_differences(first.numbers, second.numbers, ShockSpec(), config.own_scale) >= 2
        assert first.numbers["tries"] == 1
        redrawn += second.numbers["tries"] > 1
    assert redrawn > 0
