"""EH1 to EH3, see docs/specs/engine/tests.md#property-tests."""

import math

import numpy as np
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from paranoid.engine import SCENARIOS, Game, make_timeline, split_budget

FAST = settings(max_examples=40, deadline=None)

seeds = st.integers(min_value=0, max_value=2**64 - 1)
scenario_names = st.sampled_from(list(SCENARIOS))


@st.composite
def splits(draw, channels: int = 10, budget: int = 100):
    cuts = sorted(draw(st.lists(st.integers(0, budget), min_size=channels - 1, max_size=channels - 1)))
    edges = [0, *cuts, budget]
    return [b - a for a, b in zip(edges, edges[1:])]


@FAST
@given(seed=seeds, name=scenario_names)
def test_eh1_timeline_invariants(seed, name):
    config = SCENARIOS[name]
    t = make_timeline(config, seed)
    shape = (config.rounds, config.channels)
    for array in (t.levels, t.base, t.weather, t.loadings, t.impulse, t.read_noise_z):
        assert array.shape == shape
    assert t.factor.shape == (config.rounds,)
    total = t.base + t.weather + t.loadings * t.factor[:, None] + t.impulse
    assert np.allclose(t.levels, total, rtol=0, atol=1e-9)
    row = t.base[0]
    others = [c for c in range(config.channels) if c not in (t.leader, t.runner_up)]
    assert row[t.leader] > row[t.runner_up] > max(row[c] for c in others)
    assert row[t.hedge] == row.min()
    assert len(t.field) == config.channels - 2 and t.hedge in t.field


@FAST
@given(split=splits(), seed=st.integers(0, 1000))
def test_eh2_any_valid_split_plays(split, seed):
    row = Game(make_timeline(SCENARIOS["no_change"], seed)).play(split)
    assert row.bets == tuple(split)
    assert [r is None for r in row.readings] == [b == 0 for b in split]


finite_weights = st.floats(min_value=0, max_value=1e300, allow_nan=False, allow_infinity=False)


@FAST
@given(weights=st.lists(finite_weights, min_size=1, max_size=20), budget=st.integers(0, 10_000))
def test_eh3_split_budget(weights, budget):
    assume(any(w > 0 for w in weights))
    split = split_budget(weights, budget)
    assert len(split) == len(weights)
    assert sum(split) == budget
    assert all(isinstance(b, int) and b >= 0 for b in split)


@FAST
@given(weights=st.lists(finite_weights, min_size=1, max_size=5), bad=st.sampled_from([math.inf, -math.inf, math.nan]))
def test_eh3_split_budget_rejects_non_finite(weights, bad):
    try:
        split_budget([*weights, bad], 100)
    except ValueError:
        return
    raise AssertionError("a weight that is not finite must raise ValueError")
