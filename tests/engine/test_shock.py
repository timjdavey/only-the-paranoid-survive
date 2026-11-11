"""Shocks: ET12 to ET14 and ET23, see docs/specs/engine/tests.md#timeline."""

import dataclasses

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, ShockSpec, make_timeline

SEEDS = range(200)
TOLERANCE = 1e-9


def with_calm(config, seed):
    calm = dataclasses.replace(config, name="calm", events=())
    return make_timeline(config, seed), make_timeline(calm, seed)


def trough_gap(t, shock) -> float:
    """Hedge minus leader at the trough, with base and loadings from the onset row."""
    row, trough = shock.onset - 1, -shock.numbers["depth"]
    leader = int(np.argmax(t.base[row]))
    level = t.base[row] + t.loadings[row] * trough
    return float(level[t.hedge] - level[leader])


def test_et12_shock_moves_the_factor_only():
    profiles = set()
    for seed in range(100):
        t, calm = with_calm(SCENARIOS["one_shock"], seed)
        shock = t.events[0]
        row, half_life = shock.onset - 1, shock.numbers["half_life"]
        assert np.array_equal(t.base, calm.base)
        assert not t.impulse.any()
        assert np.array_equal(t.factor[:row], calm.factor[:row])
        assert np.all(t.factor[row:] != calm.factor[row:])
        s = t.factor - calm.factor
        profiles.add(shock.numbers["profile"])
        if shock.numbers["profile"] == "sharp":
            assert s[row] == pytest.approx(-shock.numbers["depth"], abs=TOLERANCE)
            ratio = s[row + half_life] / s[row]
            assert ratio == pytest.approx(0.5, abs=TOLERANCE)
        else:
            trough = row + half_life
            assert s[trough] == pytest.approx(-shock.numbers["depth"], abs=TOLERANCE)
            assert np.argmin(s) == trough
            assert s[trough + 1] > s[trough]
    assert profiles == {"sharp", "slide"}


def test_et13_hedge_stays_below_the_leader():
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["one_shock"], seed)
        shock = t.events[0]
        assert trough_gap(t, shock) <= -t.config.hedge_margin_points + TOLERANCE
        assert shock.numbers["depth"] <= shock.numbers["depth_drawn"]


def test_et13_hedge_may_overtake():
    deep = (ShockSpec(depth_sigmas=(4.0, 25.0), depth_points=(16.0, 100.0)),)
    config = dataclasses.replace(SCENARIOS["one_shock"], hedge_may_overtake=True, events=deep)
    for seed in SEEDS:
        t = make_timeline(config, seed)
        assert trough_gap(t, t.events[0]) >= config.hedge_margin_points - TOLERANCE


def test_et13_overtake_at_the_defaults_raises_on_some_seed():
    config = dataclasses.replace(SCENARIOS["one_shock"], hedge_may_overtake=True)
    raised = 0
    for seed in range(50):
        try:
            make_timeline(config, seed)
        except ValueError:
            raised += 1
    assert raised > 0


def test_et13_cap_holds_after_a_switch():
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["switch_then_shock"], seed)
        assert trough_gap(t, t.events[1]) <= -t.config.hedge_margin_points + TOLERANCE


def test_et14_one_channel_shock():
    config = dataclasses.replace(SCENARIOS["one_shock"], one_channel_shock=True)
    for seed in range(100):
        t, calm = with_calm(config, seed)
        row = t.events[0].onset - 1
        assert np.array_equal(t.factor, calm.factor)
        assert np.array_equal(t.base, calm.base)
        assert t.events[0].channel == t.leader
        others = [c for c in range(config.channels) if c != t.leader]
        assert not t.impulse[:, others].any()
        assert not t.impulse[:row, t.leader].any()
        assert np.all(t.impulse[row:, t.leader] < 0)
        for round in range(1, config.rounds + 1):
            assert t.climate_leader(round) == calm.climate_leader(round)


def test_et23_nothing_is_clipped():
    config = dataclasses.replace(
        SCENARIOS["one_shock"],
        name="low",
        pin_in_level_points=True,
        leader_base=(14.0, 16.0),
        runner_up_gap_points=(2.0, 3.0),
        field_base=(5.0, 7.0),
        hedge_base=(1.0, 2.0),
        events=(ShockSpec(depth_points=(30.0, 40.0)),),
    )
    t = make_timeline(config, 0)
    assert t.levels.min() < 0
