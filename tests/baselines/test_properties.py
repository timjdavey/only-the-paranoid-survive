"""BH1 to BH3, see docs/specs/baselines/tests.md#property-tests."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from paranoid.baselines import FORECAST_RULES, QUANTILE_LEVELS, bayesian
from paranoid.engine import SCENARIOS, Game, make_timeline

FAST = settings(max_examples=40, deadline=None)

seeds = st.integers(min_value=0, max_value=2**64 - 1)
scenario_names = st.sampled_from(list(SCENARIOS))


@st.composite
def quantile_arrays(draw):
    """(channels, 21) ascending rows, some all NaN, at least one finite."""
    channels = draw(st.integers(1, 12))
    finite = draw(st.lists(st.booleans(), min_size=channels, max_size=channels).filter(any))
    levels = st.floats(-1e6, 1e6, allow_nan=False)
    rows = [
        sorted(draw(st.lists(levels, min_size=len(QUANTILE_LEVELS), max_size=len(QUANTILE_LEVELS))))
        if keep
        else [np.nan] * len(QUANTILE_LEVELS)
        for keep in finite
    ]
    return np.array(rows, dtype=float)


@FAST
@given(q=quantile_arrays(), budget=st.integers(60, 1000))
def test_bh2_every_rule_splits_validly(q, budget):
    for rule in FORECAST_RULES.values():
        split = rule(q, budget)
        assert len(split) == q.shape[0] and sum(split) == budget
        assert all(type(bet) is int and bet >= 0 for bet in split)


@st.composite
def played(draw):
    """A timeline and a record of valid rows on it, from splits drawn at random."""
    t = make_timeline(SCENARIOS[draw(scenario_names)], draw(seeds))
    game = Game(t)
    for _ in range(draw(st.integers(0, t.config.rounds - 1))):
        cuts = sorted(draw(st.lists(st.integers(0, t.config.budget), min_size=9, max_size=9)))
        edges = [0, *cuts, t.config.budget]
        game.play([b - a for a, b in zip(edges, edges[1:])])
    return game.view(False)


@FAST
@given(view=played())
def test_bh3_the_belief_is_well_formed(view):
    belief = bayesian.belief(view)
    q = belief.quantiles
    assert q.shape == (view.channels, len(QUANTILE_LEVELS))
    assert np.isfinite(q).all() and (np.diff(q, axis=1) >= 0).all()
    assert ((belief.changed >= 0) & (belief.changed <= 1)).all()
