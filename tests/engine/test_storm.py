"""Storms on a shock: ET39 to ET44, ET53 and ET54. See docs/specs/engine/tests.md#timeline and timeline.md#storm."""

import dataclasses
import hashlib
import math

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, ShockSpec, make_timeline

SEEDS = range(200)
TOLERANCE = 1e-9

# Pinned before the shape knobs existed. Changing it is a reviewed change, see ET39.
LEVELS_HASH = "aa7ad96e2061b38a"


def levels_hash() -> str:
    """SHA-256 of `levels` on seeds 0 to 9 of every scenario, rounded to 9 places so a last-bit wobble passes."""
    digest = hashlib.sha256()
    for config in SCENARIOS.values():
        for seed in range(10):
            digest.update(np.round(make_timeline(config, seed).levels, 9).tobytes())
    return digest.hexdigest()[:16]


def one_shock(**knobs):
    return dataclasses.replace(SCENARIOS["one_shock"], events=(ShockSpec(**knobs),))


def with_calm(config, seed):
    calm = dataclasses.replace(config, name="calm", events=())
    return make_timeline(config, seed), make_timeline(calm, seed)


def before_weather(t, calm) -> np.ndarray:
    """base + loadings × the shock impulses + impulse: every level with the weather and the factor's own walk out."""
    return t.base + t.loadings * (t.factor - calm.factor)[:, None] + t.impulse


def trough_row(event) -> int:
    n = event.numbers
    return event.onset - 1 + (n["half_life"] if n["profile"] == "slide" else 0)


def formula(numbers, recovery: float, rows: int) -> np.ndarray:
    """The impulse a channel meets from onset, written from the spec rather than the recursion."""
    depth, half_life, j = numbers["depth"], numbers["half_life"], np.arange(rows)
    if numbers["profile"] == "sharp":
        return -depth * 2.0 ** (-j / (half_life * recovery))
    rebound = math.ceil(half_life / 2) * recovery
    return np.where(j <= half_life, -depth * (j + 1) / (half_life + 1), -depth * 2.0 ** (-(j - half_life) / rebound))


def test_et39_off_draws_today():
    assert levels_hash() == LEVELS_HASH


@pytest.mark.parametrize("name", SCENARIOS)
def test_et40_off_is_off(name):
    for spec in SCENARIOS[name].events:
        assert getattr(spec, "storm", None) is None
        assert not getattr(spec, "knobs_on", False)
    for seed in range(50):
        t = make_timeline(SCENARIOS[name], seed)
        assert not t.impulse.any()
        for event in t.events:
            if event.shape == "shock":
                n = event.numbers
                assert n["recovery"] == (1.0,) * t.config.channels
                assert (n["leader_last"], n["pop"], n["pop_channel"], n["pop_rise"]) == (0, 0, None, None)
                assert n["leader_loading"] is None


def test_et41_uneven_recovery_follows_its_formula():
    config = one_shock(recovery=(0.5, 2.0))
    for seed in range(100):
        t, calm = with_calm(config, seed)
        shock = t.events[0]
        row, recovery = shock.onset - 1, shock.numbers["recovery"]
        assert all(0.5 <= m <= 2.0 for m in recovery)
        assert len(set(recovery)) == config.channels
        moved = t.levels - calm.levels
        for channel, m in enumerate(recovery):
            expected = t.loadings[row, channel] * formula(shock.numbers, m, config.rounds - row)
            assert np.allclose(moved[row:, channel], expected, atol=TOLERANCE)
        assert np.allclose(t.factor[row:] - calm.factor[row:], formula(shock.numbers, 1.0, config.rounds - row))


def test_et42_leader_last():
    never, always, half = one_shock(recovery=(0.5, 2.0)), one_shock(recovery=(0.5, 2.0), leader_last_share=1.0), []
    for seed in SEEDS:
        a, b = make_timeline(never, seed), make_timeline(always, seed)
        drawn, swapped = a.events[0].numbers["recovery"], b.events[0].numbers["recovery"]
        assert sorted(drawn) == sorted(swapped)
        assert swapped[b.leader] == max(swapped)
        half.append(make_timeline(one_shock(leader_last_share=0.5), seed).events[0].numbers["leader_last"])
    assert np.mean(half) == pytest.approx(0.5, abs=0.08)


def test_et43_the_pop():
    config, shares = one_shock(recovery=(0.5, 2.0), pop_share=1.0, leader_loading=(0.8, 1.2)), []
    for seed in SEEDS:
        t, calm = with_calm(config, seed)
        shock = t.events[0]
        pop, row = shock.numbers["pop_channel"], trough_row(shock)
        assert pop in t.field and pop not in (t.hedge, t.leader)
        assert shock.sleeper is None and t.sleeper is None
        levels = before_weather(t, calm)[row]
        assert levels[t.leader] - levels[pop] == pytest.approx(config.hedge_margin_points, abs=TOLERANCE)
        shares.append(make_timeline(one_shock(pop_share=0.5), seed).events[0].numbers["pop"])
    assert np.mean(shares) == pytest.approx(0.5, abs=0.08)


def test_et44_the_leader_stays_ahead(stormy):
    config = stormy(SCENARIOS["one_shock"])
    margin = config.hedge_margin_points
    for seed in SEEDS:
        t, calm = with_calm(config, seed)
        levels = before_weather(t, calm)[t.events[0].onset - 1 :]
        others = np.delete(levels, t.leader, axis=1)
        assert np.all(levels[:, [t.leader]] - others >= margin - TOLERANCE)
    overtaken = 0
    for seed in SEEDS:
        t, calm = with_calm(SCENARIOS["one_shock"], seed)
        levels = before_weather(t, calm)
        overtaken += int(np.any(np.argmax(levels, axis=1) != t.leader))
    assert overtaken > 0


def test_et53_invariants_with_every_knob_on(stormy):
    config = stormy(SCENARIOS["one_shock"])
    for seed in range(100):
        t, calm = with_calm(config, seed)
        row = t.events[0].onset - 1
        assert np.allclose(t.levels, t.base + t.weather + t.loadings * t.factor[:, None] + t.impulse, atol=TOLERANCE)
        assert np.array_equal(t.base, calm.base)
        assert not t.impulse[:row].any()
        assert np.allclose(t.factor[row:] - calm.factor[row:], formula(t.events[0].numbers, 1.0, config.rounds - row))


def test_et54_leader_loading():
    config = one_shock(recovery=(0.5, 2.0), leader_loading=(0.8, 1.2))
    full, margin = one_shock(leader_loading=(1.0, 1.0)), config.hedge_margin_points
    assert ShockSpec(leader_loading=(1.0, 1.0)).knobs_on
    for seed in SEEDS:
        t, calm = with_calm(config, seed)
        shock = t.events[0]
        row, n = shock.onset - 1, shock.numbers
        assert 0.8 <= n["leader_loading"] <= 1.2
        assert np.array_equal(t.loadings, calm.loadings)
        moved = t.levels - calm.levels
        for channel, m in enumerate(n["recovery"]):
            met = n["leader_loading"] if channel == t.leader else t.loadings[row, channel]
            assert np.allclose(moved[row:, channel], met * formula(n, m, config.rounds - row), atol=TOLERANCE)
        at_trough = before_weather(t, calm)[trough_row(shock)]
        assert at_trough[t.leader] - at_trough[t.hedge] >= margin - TOLERANCE
        whole = make_timeline(full, seed)
        fall = make_timeline(SCENARIOS["no_change"], seed).levels - whole.levels
        depth = whole.events[0].numbers["depth"]
        assert fall[trough_row(whole.events[0]), whole.leader] == pytest.approx(depth, abs=TOLERANCE)
