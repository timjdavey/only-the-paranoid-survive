"""BF1 to BF4, see docs/specs/baselines/tests.md#forecast."""

import numpy as np
import pytest

from paranoid.baselines import (
    FORECAST_RULES,
    MEDIAN_INDEX,
    ODDS_DRAWS,
    QUANTILE_LEVELS,
    Odds,
    TopPickWithExploreBets,
    explore_1,
    explore_2,
    explore_5,
    odds,
    top_pick,
)

RULES = list(FORECAST_RULES.values())
SPREAD = np.linspace(-10.0, 10.0, len(QUANTILE_LEVELS))  # strictly ascending, centred on 0


def forecast(*centres: float) -> np.ndarray:
    """One strictly ascending row per channel, its median at the centre given."""
    return np.array([centre + SPREAD for centre in centres])


def test_bf1_top_pick_and_explore():
    q = forecast(40, 55, 50, 30)
    assert top_pick(q, 100) == (0, 100, 0, 0)
    assert explore_2(q, 100) == (2, 94, 2, 2)
    ten = forecast(*range(40, 50))
    assert explore_2(ten, 100) == (2,) * 9 + (82,)
    assert explore_1(ten, 100)[-1] == 91 and explore_5(ten, 100)[-1] == 55


def test_bf1_odds_on_equal_rows_is_even():
    first, second = odds(forecast(50, 50), 100)
    assert abs(first - 50) <= 5 and first + second == 100


def test_bf1_odds_follows_the_gap():
    split = odds(forecast(60, 50, 20), 100)
    assert split[0] > split[1] > split[2] == 0


def test_bf1_a_nan_channel():
    q = forecast(40, 50, 45)
    q[1] = np.nan
    assert top_pick(q, 100) == (0, 0, 100)
    assert odds(q, 100)[1] == 0
    assert explore_2(q, 100) == (2, 2, 96)


def test_bf2_the_grid_and_the_ids():
    assert len(QUANTILE_LEVELS) == 21
    assert list(QUANTILE_LEVELS) == sorted(set(QUANTILE_LEVELS))
    assert QUANTILE_LEVELS[0] == 0.01 and QUANTILE_LEVELS[-1] == 0.99
    assert {0.05, 0.10, 0.95} <= set(QUANTILE_LEVELS)
    assert MEDIAN_INDEX == 10 and QUANTILE_LEVELS[MEDIAN_INDEX] == 0.5
    assert np.allclose(np.diff(QUANTILE_LEVELS[1:-1]), 0.05)
    assert dict(FORECAST_RULES) == {
        "top-pick": top_pick,
        "odds": odds,
        "explore-1": explore_1,
        "explore-2": explore_2,
        "explore-5": explore_5,
    }
    assert explore_5 == TopPickWithExploreBets(5) and odds == Odds() and odds.draws == ODDS_DRAWS == 1000
    with pytest.raises(TypeError):
        FORECAST_RULES["odds"] = top_pick


def test_bf3_odds_is_pure():
    q = forecast(50, 52, 49, 51)
    q[2] = np.nan
    before = q.copy()
    assert odds(q, 100) == odds(q, 100)
    assert np.array_equal(q, before, equal_nan=True)


def bad_arrays() -> dict[str, np.ndarray]:
    partly_nan, infinite, falling = forecast(50, 40), forecast(50, 40), forecast(50, 40)
    partly_nan[0, 3] = np.nan
    infinite[1, -1] = np.inf
    falling[0] = falling[0][::-1]
    return {
        "all nan": np.full((3, 21), np.nan),
        "one dimension": SPREAD,
        "20 columns": forecast(50, 40)[:, :20],
        "partly nan": partly_nan,
        "infinite": infinite,
        "falling": falling,
    }


@pytest.mark.parametrize("name", list(bad_arrays()))
@pytest.mark.parametrize("rule", RULES, ids=list(FORECAST_RULES))
def test_bf4_a_bad_array_raises(rule, name):
    with pytest.raises(ValueError):
        rule(bad_arrays()[name], 100)


@pytest.mark.parametrize("rule", RULES, ids=list(FORECAST_RULES))
def test_bf4_equal_neighbours_pass(rule):
    q = forecast(50, 40)
    q[0, 5:9] = q[0, 5]
    assert sum(rule(q, 100)) == 100


def test_bf4_explore_too_big_for_the_channels():
    with pytest.raises(ValueError):
        TopPickWithExploreBets(12)(forecast(*range(10)), 100)
    assert sum(TopPickWithExploreBets(11)(forecast(*range(10)), 100)) == 100


def test_bf4_construction_checks():
    with pytest.raises(ValueError):
        TopPickWithExploreBets(0)
    with pytest.raises(ValueError):
        Odds(draws=0)
