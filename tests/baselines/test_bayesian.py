"""BB1 to BB4, BB6, BB7 and BB9, see docs/specs/baselines/tests.md#bayesian.

The rows about whole runs, BB5 and BB8, are in test_bayesian_runs.py.
"""

import dataclasses

import numpy as np
import pytest

from paranoid.baselines import (
    BAYESIAN_RULES,
    FORECAST_RULES,
    HAZARDS,
    LOOKAHEAD_DRAWS,
    ODDS_DRAWS,
    QUANTILE_LEVELS,
    Bayesian,
    bayesian,
    complacent,
)
from paranoid.engine import SCENARIOS, make_timeline, play

WOBBLE = [0.3, -0.6, 0.8, -0.2, 0.5, -0.9, 0.1, 0.6, -0.4, 0.0]  # every reading within 1 of the level


def on_leader(row, t, levels):
    """Rows with `budget` on the leader, reading the levels given."""
    bets = [100 if c == t.leader else 0 for c in range(10)]
    return [row(r, bets, [level if b else None for b in bets]) for r, level in enumerate(levels, start=1)]


def flat(rounds: int) -> list[float]:
    return [60 + WOBBLE[r % len(WOBBLE)] for r in range(rounds)]


def test_bb1_flat_readings_argue_against_a_jump(no_change, row, view_of):
    belief = bayesian.belief(view_of(no_change, on_leader(row, no_change, flat(20))))
    leader = no_change.leader
    assert abs(belief.mean[leader] - 60) < 1
    assert belief.changed[leader] < 1 - (1 - bayesian.hazard) ** 20


def test_bb2_a_drop_reads_as_a_jump(no_change, row, view_of):
    levels = [level - (20 if r >= 15 else 0) for r, level in enumerate(flat(20), start=1)]
    rows, leader = on_leader(row, no_change, levels), no_change.leader
    assert bayesian.belief(view_of(no_change, rows[:17])).changed[leader] > 0.9
    assert abs(bayesian.belief(view_of(no_change, rows)).mean[leader] - 40) < 3


def prior_mean(lo_hi) -> float:
    return (lo_hi[0] + lo_hi[1]) / 2


def test_bb3_a_channel_never_read(no_change, row, view_of):
    t = no_change
    view = view_of(t, on_leader(row, t, flat(30)))
    belief, dials = bayesian.belief(view), view.dials
    jump = (dials.hedge_base[0] + dials.leader_base[1]) / 2
    role = {
        t.runner_up: prior_mean(dials.leader_base) - prior_mean(dials.runner_up_gap_points),
        t.hedge: prior_mean(dials.hedge_base),
    }
    changed = 1 - (1 - bayesian.hazard) ** 30
    for c in range(10):
        if c == t.leader:
            continue
        expected = (1 - changed) * role.get(c, prior_mean(dials.field_base)) + changed * jump
        assert belief.changed[c] == pytest.approx(changed, abs=1e-9)
        assert belief.mean[c] == pytest.approx(expected, abs=1e-6)


def test_bb4_pure_and_well_formed(view_of):
    t = make_timeline(SCENARIOS["down_switch"], 3)
    view = view_of(t, play(complacent, t, max_rounds=25).rows)
    before = view.record.copy()
    first, second = bayesian.belief(view), bayesian.belief(view)
    assert bayesian(view) == bayesian(view)
    assert np.array_equal(first.quantiles, second.quantiles)
    q = first.quantiles
    assert q.shape == (10, len(QUANTILE_LEVELS))
    assert np.isfinite(q).all() and (np.diff(q, axis=1) >= 0).all()
    assert ((first.changed >= 0) & (first.changed <= 1)).all() and (first.sd > 0).all()
    assert view.record == before
    with pytest.raises(ValueError):
        q[0, 0] = 0.0


@pytest.mark.parametrize(
    "args",
    [{"hazard": 0.0}, {"hazard": 1.0}, {"rule": "nope"}, {"draws": 0}, {"lookahead_draws": 0}],
    ids=["hazard 0", "hazard 1", "rule", "draws", "lookahead_draws"],
)
def test_bb6_construction_checks(args):
    with pytest.raises(ValueError):
        Bayesian(**args)


def test_bb6_explore_too_big_after_round_1(view_of):
    t = make_timeline(dataclasses.replace(SCENARIOS["no_change"], budget=40), 0)
    player = Bayesian(rule="explore-5")
    assert player(view_of(t)) == tuple(40 if c == t.leader else 0 for c in range(10))
    with pytest.raises(ValueError):
        play(player, t, max_rounds=2)


def test_bb7_lookahead_picks_a_forecast_rule(view_of):
    t = make_timeline(SCENARIOS["down_switch"], 1)
    view = view_of(t, play(complacent, t, max_rounds=12).rows)
    quantiles = Bayesian().belief(view).quantiles
    assert Bayesian(rule="lookahead")(view) in {rule(quantiles, 100) for rule in FORECAST_RULES.values()}


def test_bb7_lookahead_exploits_on_the_last_round(no_change, view_of):
    view = view_of(no_change, play(complacent, no_change, max_rounds=no_change.config.rounds - 1).rows)
    assert view.round == view.dials.rounds
    assert Bayesian(rule="lookahead")(view) == Bayesian(rule="top-pick")(view)


def test_round_1_is_the_leader_whatever_the_rule(no_change, view_of):
    for rule in BAYESIAN_RULES:
        assert Bayesian(rule=rule)(view_of(no_change)) == complacent(view_of(no_change))


def test_bb9_the_frontier_family():
    assert len(HAZARDS) == 5 and list(HAZARDS) == sorted(set(HAZARDS)) and 0 < HAZARDS[0] and HAZARDS[-1] < 1
    assert BAYESIAN_RULES == (*FORECAST_RULES, "lookahead")
    assert bayesian == Bayesian() and bayesian.draws == ODDS_DRAWS and bayesian.lookahead_draws == LOOKAHEAD_DRAWS


@pytest.mark.parametrize("rule", BAYESIAN_RULES)
@pytest.mark.parametrize("hazard", HAZARDS)
def test_bb9_every_player_splits_validly(hazard, rule, check_split):
    for name in ("down_switch", "one_shock"):
        for r in play(Bayesian(hazard=hazard, rule=rule), make_timeline(SCENARIOS[name], 0)).rows:
            check_split(r.bets)
