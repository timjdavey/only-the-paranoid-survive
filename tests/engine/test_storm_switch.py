"""A switch that arrives in a storm: ET45 to ET52. See docs/specs/engine/tests.md#timeline and timeline.md#storm."""

import dataclasses
import math

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, ScenarioConfig, ShockSpec, make_timeline

SEEDS = range(200)
TOLERANCE = 1e-9


def trough_row(n, onset: int, prefix: str = "storm_") -> int:
    return onset - 1 + (n[f"{prefix}half_life"] if n[f"{prefix}profile"] == "slide" else 0)


def lift(n, channel: int, rows: int) -> np.ndarray:
    """0 to the trough, then 1 minus the share of the storm left on the channel, from the spec's formula."""
    half_life, recovery, j = n["storm_half_life"], n["storm_recovery"][channel], np.arange(rows)
    if n["storm_profile"] == "sharp":
        left = 2.0 ** (-j / (half_life * recovery))
        trough = 0
    else:
        left = 2.0 ** (-(j - half_life) / (math.ceil(half_life / 2) * recovery))
        trough = half_life
    return np.where(j <= trough, 0.0, 1.0 - left)


def test_et45_storm_twins_match_through_the_trough(stormy):
    shock, switch = stormy(SCENARIOS["one_shock"]), stormy(SCENARIOS["down_switch"])
    for seed in SEEDS:
        a, b = make_timeline(shock, seed), make_timeline(switch, seed)
        row = trough_row(b.events[0].numbers, b.events[0].onset) + 1
        assert np.array_equal(a.levels[:row], b.levels[:row])
        assert not np.array_equal(a.levels[row:], b.levels[row:])
    both, after = stormy(SCENARIOS["shock_then_switch"]), stormy(SCENARIOS["switch_then_shock"])
    for seed in range(100):
        for config, twin in ((both, shock), (after, switch)):
            t = make_timeline(config, seed)
            row = t.events[1].onset - 1
            assert np.array_equal(t.levels[:row], make_timeline(twin, seed).levels[:row])


def test_et46_storm_fall(stormy):
    config = stormy(SCENARIOS["down_switch"])
    calm = dataclasses.replace(config, name="calm", events=())
    for seed in SEEDS:
        t, quiet = make_timeline(config, seed), make_timeline(calm, seed)
        switch, leader = t.events[0], t.leader
        row, n = switch.onset - 1, switch.numbers
        second = int(np.argsort(t.base[row - 1])[-2])
        assert n["fall"] == pytest.approx(t.base[row - 1, leader] - t.base[row - 1, second] + n["size"], abs=TOLERANCE)
        expected = t.base[row - 1, leader] - n["fall"] * lift(n, leader, config.rounds - row)
        assert np.allclose(t.base[row:, leader], expected, atol=TOLERANCE)
        others = [c for c in range(config.channels) if c not in (leader, t.sleeper)]
        assert np.array_equal(t.base[:, others], quiet.base[:, others])
        assert np.array_equal(t.loadings, quiet.loadings)


def test_et47_storm_rise(stormy):
    config, rises, pops = stormy(SCENARIOS["down_switch"]), 0, 0
    for seed in SEEDS:
        t = make_timeline(config, seed)
        switch = t.events[0]
        row, n = switch.onset - 1, switch.numbers
        if n["kind"] != "fall_and_rise":
            assert t.sleeper is None and n["target"] is None
            continue
        rises += 1
        pops += n["storm_pop"]
        assert t.sleeper == (n["storm_pop_channel"] if n["storm_pop"] else n["sleeper"])
        ends = t.base[row - 1].copy()
        ends[t.leader] -= n["fall"]
        assert n["target"] == pytest.approx(np.delete(ends, t.sleeper).max() + n["rise"], abs=TOLERANCE)
        start = t.base[row - 1, t.sleeper]
        expected = start + (n["target"] - start) * lift(n, t.sleeper, config.rounds - row)
        assert np.allclose(t.base[row:, t.sleeper], expected, atol=TOLERANCE)
    assert rises > 50 and 0 < pops < rises


def test_et48_storm_numbers_equal_the_twin_shock(stormy):
    shock, switch = stormy(SCENARIOS["one_shock"]), stormy(SCENARIOS["down_switch"])
    for seed in SEEDS:
        a, b = make_timeline(shock, seed).events[0], make_timeline(switch, seed).events[0]
        for key, value in a.numbers.items():
            if key != "tries":
                assert b.numbers[f"storm_{key}"] == value, key
        assert b.channel == make_timeline(switch, seed).leader


def test_et49_no_two_alike_still_bites(stormy):
    fixed = ShockSpec(depth_sigmas=(6.0, 6.0), depth_points=(24.0, 24.0), half_life=(3, 3), profile="sharp")
    config = stormy(ScenarioConfig(name="twice", events=(fixed, fixed)))
    with pytest.raises(ValueError):
        make_timeline(config, 0)
    shocks, redrawn = stormy(ScenarioConfig(name="shocks", events=(ShockSpec(), ShockSpec()))), 0
    for seed in SEEDS:
        _, second = make_timeline(shocks, seed).events
        redrawn += second.numbers["tries"] > 1
    assert redrawn > 0


@pytest.mark.parametrize("name", ["shock_then_switch", "switch_then_shock"])
def test_et50_two_event_scenarios_build(stormy, name):
    config = stormy(SCENARIOS[name])
    for seed in SEEDS:
        t = make_timeline(config, seed)
        assert len(t.events) == 2
        assert t.sleeper != t.hedge
        assert np.allclose(t.levels, t.base + t.weather + t.loadings * t.factor[:, None] + t.impulse, atol=TOLERANCE)


@pytest.mark.parametrize("name", SCENARIOS)
def test_et51_pinning_holds(stormy, name):
    pinned = dataclasses.replace(stormy(SCENARIOS[name]), pin_in_level_points=True)
    wide = dataclasses.replace(pinned, own_scale=8.0)
    for seed in range(50):
        a, b = make_timeline(pinned, seed), make_timeline(wide, seed)
        for field in ("base", "loadings", "impulse"):
            assert np.array_equal(getattr(a, field), getattr(b, field)), field
        assert a.events == b.events
        assert [dict(e.numbers) for e in a.events] == [dict(e.numbers) for e in b.events]


def test_et52_an_onset_on_the_last_round_builds(stormy):
    rounds = SCENARIOS["down_switch"].rounds
    for name in ("one_shock", "down_switch", "switch_then_shock"):
        config = dataclasses.replace(stormy(SCENARIOS[name]), onset=(rounds, rounds))
        t = make_timeline(config, 0)
        assert t.events[0].onset == rounds
        assert t.levels.shape == (rounds, config.channels)
