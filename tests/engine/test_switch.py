"""Switches: ET15, ET16, ET24, ET27, ET29, ET31 and ET32.

See docs/specs/engine/tests.md#timeline.
"""

import dataclasses

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, DriftSpec, ScenarioConfig, SwitchSpec, make_timeline

SEEDS = range(200)
TOLERANCE = 1e-9

SHOCK_KEYS = {
    "gap", "profile", "depth_drawn", "half_life", "recovery", "leader_last", "pop", "pop_channel", "depth", "pop_rise",
}
NUMBER_KEYS = {
    "shock": SHOCK_KEYS | {"tries"},
    "switch": {
        "gap", "kind", "size", "rise", "ramp", "sleeper", "sleeper_loading",
        "short", "short_level", "fall", "target", "tries",
    } | {f"storm_{key}" for key in SHOCK_KEYS},
    "drift": {"gap", "profile", "size", "length", "fall", "tries"},
}


def ends(t, event) -> tuple[int, int]:
    """The onset row and the row the ramp completes on."""
    row = event.onset - 1
    return row, row + event.numbers["ramp"] - 1


def test_et15_fall():
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["down_switch"], seed)
        switch = t.events[0]
        row, done = ends(t, switch)
        leader, ramp = t.leader, switch.numbers["ramp"]
        second = int(np.argsort(t.base[row - 1])[-2])
        assert switch.channel == leader
        assert switch.numbers["sleeper"] != t.hedge
        assert t.base[done, leader] == pytest.approx(t.base[row - 1, second] - switch.numbers["size"], abs=TOLERANCE)
        moved = t.base[row - 1, leader] - t.base[done, leader]
        assert switch.numbers["fall"] == pytest.approx(moved, abs=TOLERANCE)
        for j in range(ramp):
            step = t.base[row - 1, leader] - switch.numbers["fall"] * (j + 1) / ramp
            assert t.base[row + j, leader] == pytest.approx(step, abs=TOLERANCE)
        unmoved = [c for c in range(t.config.channels) if c not in (leader, switch.sleeper)]
        assert np.array_equal(t.base[:, unmoved], np.tile(t.base[0, unmoved], (t.config.rounds, 1)))


def rises():
    for name in ("down_switch", "up_switch"):
        for seed in SEEDS:
            t = make_timeline(SCENARIOS[name], seed)
            if t.sleeper is not None and t.events[0].numbers["short"] == 0:
                yield t


def test_et16_rise():
    count = 0
    for t in rises():
        count += 1
        switch, sleeper = t.events[0], t.sleeper
        row, done = ends(t, switch)
        highest_other = np.delete(t.base[done], sleeper).max()
        assert t.base[done, sleeper] - highest_other == pytest.approx(switch.numbers["rise"], abs=TOLERANCE)
        assert np.all(t.loadings[row:, sleeper] == switch.numbers["sleeper_loading"])
        assert switch.numbers["sleeper_loading"] > 0
        others = [c for c in range(t.config.channels) if c != sleeper]
        assert np.array_equal(t.loadings[:, others], np.tile(t.loadings[0, others], (t.config.rounds, 1)))
        assert np.all(t.loadings[:row, sleeper] == t.loadings[0, sleeper])
    assert count > 100


def low_ladder(**fields) -> ScenarioConfig:
    return ScenarioConfig(
        name="low",
        pin_in_level_points=True,
        leader_base=(12.0, 12.0),
        runner_up_gap_points=(2.0, 2.0),
        field_base=(5.0, 6.0),
        hedge_base=(1.0, 2.0),
        **fields,
    )


def test_et24_leader_at_or_below_zero_raises():
    with pytest.raises(ValueError):
        make_timeline(low_ladder(events=(SwitchSpec(kind="fall", size_points=(20.0, 20.0)),)), 0)
    with pytest.raises(ValueError):
        make_timeline(low_ladder(events=(DriftSpec(size_points=(20.0, 20.0)),)), 0)
    make_timeline(low_ladder(events=(SwitchSpec(kind="fall", size_points=(5.0, 5.0)),)), 0)


def test_et27_empty_sleeper_set_raises():
    both = (SwitchSpec(kind="fall_and_rise"), SwitchSpec(kind="fall_and_rise"))
    config = ScenarioConfig(name="four", channels=4, events=both)
    with pytest.raises(ValueError):
        make_timeline(config, 0)


@pytest.mark.parametrize("name", SCENARIOS)
def test_et29_numbers_keys(name):
    for seed in range(50):
        for event in make_timeline(SCENARIOS[name], seed).events:
            assert set(event.numbers) == NUMBER_KEYS[event.shape]
            assert event.numbers["tries"] >= 1
            if event.shape == "switch":
                assert all(event.numbers[f"storm_{key}"] is None for key in SHOCK_KEYS)
            if event.shape == "shock":
                assert event.numbers["depth"] <= event.numbers["depth_drawn"]


def test_et29_depth_on_every_one_shock_seed():
    for seed in SEEDS:
        shock = make_timeline(SCENARIOS["one_shock"], seed).events[0]
        assert shock.numbers["depth"] <= shock.numbers["depth_drawn"]


def test_et31_short():
    count = 0
    for seed in range(400):
        t = make_timeline(SCENARIOS["up_switch"], seed)
        switch = t.events[0]
        if switch.numbers["short"] == 0:
            continue
        count += 1
        row, done = ends(t, switch)
        leader, sleeper = t.leader, t.sleeper
        below = t.base[done, t.runner_up]
        top = t.base[done, leader]
        expected = below + switch.numbers["short_level"] * (top - below)
        assert t.base[done, sleeper] == pytest.approx(expected, abs=TOLERANCE)
        assert below < t.base[done, sleeper] < top
        for round in range(1, t.config.rounds + 1):
            assert t.climate_leader(round) == leader
    assert count > 50


def test_et32_undo():
    calm_config = SCENARIOS["no_change"]
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["up_switch_then_down_switch"], seed)
        calm = make_timeline(calm_config, seed)
        rise, undo = t.events
        assert undo.channel == rise.sleeper
        assert undo.sleeper is None
        assert undo.numbers["kind"] == "undo"
        row, done = ends(t, undo)
        assert np.allclose(t.base[done:], calm.base[done:], rtol=0, atol=TOLERANCE)
        assert np.allclose(t.loadings[done:], calm.loadings[done:], rtol=0, atol=TOLERANCE)
        sleeper, ramp = undo.channel, undo.numbers["ramp"]
        start, end = t.base[row - 1, sleeper], t.base[0, sleeper]
        for j in range(ramp):
            step = start + (end - start) * (j + 1) / ramp
            assert t.base[row + j, sleeper] == pytest.approx(step, abs=TOLERANCE)
        assert undo.numbers["fall"] == pytest.approx(start - t.base[done, sleeper], abs=TOLERANCE)
