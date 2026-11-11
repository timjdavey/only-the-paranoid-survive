"""BB5 and BB8, whole runs on a scripted timeline and on named seeds, see docs/specs/baselines/tests.md#bayesian.

Each seed was picked on the real code. If one stops holding, read tests.md#three-sizes first.
"""

import numpy as np
import pytest

from paranoid.baselines import Bayesian, bayesian, complacent
from paranoid.engine import SCENARIOS, make_timeline, play

NEAR_ZERO = Bayesian(hazard=1e-9, rule="top-pick")


def test_bb5_holds_on_a_timeline_with_no_weather(no_change, scripted):
    t = scripted(no_change, no_change.base)
    assert play(NEAR_ZERO, t) == play(complacent, t)


@pytest.mark.parametrize("seed", [0, 1])
def test_bb5_holds_on_named_no_change_seeds(seed):
    t = make_timeline(SCENARIOS["no_change"], seed)
    assert play(NEAR_ZERO, t) == play(complacent, t)


def test_bb5_weather_can_move_it():
    """Seed 33: the leader's bad spell forecasts below the unread runner-up, see bayesian.md#rules."""
    t = make_timeline(SCENARIOS["no_change"], 33)
    assert play(NEAR_ZERO, t) != play(complacent, t)


@pytest.mark.parametrize("seed", [0, 2])
def test_bb8_beats_complacent_on_a_down_switch(seed):
    t = make_timeline(SCENARIOS["down_switch"], seed)
    output = [sum(r.output for r in play(policy, t).rows) for policy in (bayesian, complacent)]
    assert output[0] > output[1]


@pytest.mark.parametrize("seed", [0, 1])
def test_bb8_holds_through_one_shock(seed, picks):
    t = make_timeline(SCENARIOS["one_shock"], seed)
    assert picks(play(bayesian, t))[-1] == t.leader


def test_bayesian_never_reads_the_timeline(view_of):
    t = make_timeline(SCENARIOS["switch_then_shock"], 2)
    record = play(bayesian, t, max_rounds=20)
    for k in (1, 8, 20):
        hidden, shown = view_of(t, record.rows[:k]), view_of(t, record.rows[:k], peeks=True)
        assert bayesian(hidden) == bayesian(shown)
        assert np.array_equal(bayesian.belief(hidden).quantiles, bayesian.belief(shown).quantiles)
