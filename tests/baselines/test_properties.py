"""BH1 to BH3, see docs/specs/baselines/tests.md#property-tests."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from paranoid.baselines import FORECAST_RULES, QUANTILE_LEVELS

FAST = settings(max_examples=40, deadline=None)


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
