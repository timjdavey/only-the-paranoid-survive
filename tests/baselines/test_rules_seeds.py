"""BR2, BR6 and BR8, on named seeds, see docs/specs/baselines/tests.md#rules.

Each seed was picked on the real code. If one stops holding, read tests.md#three-sizes first.
"""

import pytest

from paranoid.baselines import hedge_rule, scout_rule
from paranoid.engine import SCENARIOS, Record, Timeline, make_timeline, play


def scouts(record: Record) -> list[int]:
    """The rounds the hedge rule scouted in: more than the pick and the hedge funded."""
    return [r.round for r in record.rows if sum(bet > 0 for bet in r.bets) > 2]


def rise(t: Timeline) -> int:
    """The first round the climate leader is not the round 1 leader."""
    return next(r for r in range(1, t.config.rounds + 1) if t.climate_leader(r) != t.leader)


HOLDS = [("up_switch", 0), ("up_switch", 1), ("up_switch_then_down_switch", 0), ("up_switch_then_down_switch", 1)]


@pytest.mark.parametrize(("name", "seed"), HOLDS)
def test_br2_hedge_rule_holds_through_an_up_switch(name, seed, picks):
    t = make_timeline(SCENARIOS[name], seed)
    record = play(hedge_rule, t)
    assert scouts(record) == []
    assert set(picks(record)) == {t.leader}


def test_br2_a_false_alarm_after_the_rise_finds_the_sleeper(picks):
    t = make_timeline(SCENARIOS["up_switch"], 12)
    record = play(hedge_rule, t)
    assert scouts(record)[0] > rise(t)
    assert picks(record)[-1] == t.sleeper


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_br6_scout_rule_goes_to_the_sleeper_and_back(seed, picks):
    t = make_timeline(SCENARIOS["up_switch_then_down_switch"], seed)
    chosen = picks(play(scout_rule, t))
    moves = [(r, b) for r, (a, b) in enumerate(zip(chosen, chosen[1:]), start=2) if a != b]
    assert len(moves) >= 2
    (to_sleeper, first), (back, last) = moves[0], moves[-1]
    assert first == t.sleeper and to_sleeper > rise(t)
    assert last == t.leader and back > t.events[1].onset
    assert chosen[-1] == t.leader


@pytest.mark.parametrize("seed", [4, 5, 7])
def test_br8_hedge_rule_holds_through_one_shock(seed, picks):
    t = make_timeline(SCENARIOS["one_shock"], seed)
    record = play(hedge_rule, t)
    assert scouts(record) == []
    assert set(picks(record)) == {t.leader}
