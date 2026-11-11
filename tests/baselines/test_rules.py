"""BR1, BR3 to BR5, BR7, BR9 and the rules' invariants, see docs/specs/baselines/tests.md#rules.

The rows about named seeds, BR2, BR6 and BR8, are in test_rules_seeds.py.
"""

import pytest

from paranoid.baselines import HedgeRule, ScoutRule, complacent, hedge_rule, scout_rule
from paranoid.engine import SCENARIOS, make_timeline, play


@pytest.fixture
def roles(no_change):
    """The no_change fixture's leader, hedge and the first two field channels that are not the hedge."""
    t = no_change
    field = [c for c in t.field if c != t.hedge]
    return t.leader, t.hedge, field[0], field[1]


def hold(leader: int, hedge: int, explore: int = 2) -> list[int]:
    bets = [0] * 10
    bets[leader], bets[hedge] = 100 - explore, explore
    return bets


def scout_split(hedge: int, explore: int = 2) -> list[int]:
    """`explore` on the hedge, the rest evenly over the other nine, leftovers to the lowest index."""
    others = [c for c in range(10) if c != hedge]
    bets = [0] * 10
    bets[hedge] = explore
    for i, c in enumerate(others):
        bets[c] = (100 - explore) // 9 + (1 if i < (100 - explore) % 9 else 0)
    return bets


def readings(bets: list[int], values: dict[int, float], default: float = 40.0) -> list[float | None]:
    return [None if b == 0 else values.get(c, default) for c, b in enumerate(bets)]


def hedge_rows(row, roles, leader_levels, hedge_levels, start=1):
    leader, hedge, _, _ = roles
    bets = hold(leader, hedge)
    return [
        row(start + i, bets, readings(bets, {leader: lv, hedge: hv}))
        for i, (lv, hv) in enumerate(zip(leader_levels, hedge_levels))
    ]


FALL = [60, 61, 59, 46, 45, 47]  # recent mean 46, earlier mean 60


def test_br1_holds_through_a_fall_with_a_tell(no_change, roles, row, view_of):
    leader, hedge, _, _ = roles
    rows = hedge_rows(row, roles, FALL, [24, 24, 24, 31, 30, 32])
    assert hedge_rule(view_of(no_change, rows)) == tuple(hold(leader, hedge))


def test_br1_needs_window_earlier_readings(no_change, roles, row, view_of):
    leader, hedge, _, _ = roles
    rows = hedge_rows(row, roles, FALL[1:], [24] * 5)
    assert hedge_rule(view_of(no_change, rows)) == tuple(hold(leader, hedge))


def test_br1_scouts_then_moves_never_to_the_hedge(no_change, roles, row, view_of):
    leader, hedge, best, runner = roles
    rows = hedge_rows(row, roles, FALL, [24] * 6)
    assert hedge_rule(view_of(no_change, rows)) == tuple(scout_split(hedge))
    scouted = scout_split(hedge)
    for r in (7, 8):
        rows.append(row(r, scouted, readings(scouted, {hedge: 90, best: 70, runner: 66, leader: 50})))
        if r == 7:
            assert hedge_rule(view_of(no_change, rows)) == tuple(scout_split(hedge))
    assert hedge_rule(view_of(no_change, rows)) == tuple(hold(best, hedge))


def test_br1_a_false_alarm_returns_to_the_pick(no_change, roles, row, view_of):
    leader, hedge, best, _ = roles
    rows = hedge_rows(row, roles, FALL, [24] * 6)
    scouted = scout_split(hedge)
    rows += [row(r, scouted, readings(scouted, {leader: 62, best: 50})) for r in (7, 8)]
    assert hedge_rule(view_of(no_change, rows)) == tuple(hold(leader, hedge))


def scout_rows(row, roles, values_by_round, start=1):
    leader, _, _, _ = roles
    bets = [1] * 10
    bets[leader] = 91
    return [row(start + i, bets, readings(bets, values)) for i, values in enumerate(values_by_round)]


def picked(split) -> int:
    return max(range(len(split)), key=lambda c: split[c])


def test_br3_moves_after_exactly_n_rounds(no_change, roles, row, view_of):
    leader, hedge, riser, _ = roles
    calm = {leader: 60, hedge: 24, riser: 50}
    beat = {leader: 60, hedge: 24, riser: 63}
    rows = scout_rows(row, roles, [calm, calm, beat, beat])
    assert picked(scout_rule(view_of(no_change, rows))) == leader
    rows = scout_rows(row, roles, [calm, beat, beat, beat])
    split = scout_rule(view_of(no_change, rows))
    assert picked(split) == riser and split.count(1) == 9


def test_br3_a_tie_is_no_beat(no_change, roles, row, view_of):
    leader, hedge, riser, _ = roles
    calm, level = {leader: 60, hedge: 24}, {leader: 60, hedge: 24, riser: 60}
    rows = scout_rows(row, roles, [calm, level, level, level])
    assert picked(scout_rule(view_of(no_change, rows))) == leader


def test_br3_no_move_when_the_hedge_tells(no_change, roles, row, view_of):
    leader, hedge, riser, _ = roles
    calm = {leader: 60, hedge: 24}
    told = {leader: 50, hedge: 30, riser: 55}
    rows = scout_rows(row, roles, [calm, told, told, told])
    assert picked(scout_rule(view_of(no_change, rows))) == leader


def test_br4_scout_rule_too_big_for_the_view(no_change, view_of):
    with pytest.raises(ValueError):
        ScoutRule(s=12)(view_of(no_change))
    assert sum(ScoutRule(s=11)(view_of(no_change))) == 100


@pytest.mark.parametrize(
    "build",
    [
        lambda: HedgeRule(explore=0),
        lambda: HedgeRule(window=0),
        lambda: HedgeRule(scout_rounds=0),
        lambda: HedgeRule(fall_points=0.0),
        lambda: HedgeRule(tell_points=float("inf")),
        lambda: ScoutRule(s=0),
        lambda: ScoutRule(n=0),
        lambda: ScoutRule(tell_points=float("nan")),
    ],
)
def test_br5_construction_checks(build):
    with pytest.raises(ValueError):
        build()


@pytest.mark.parametrize("explore", [100, 95])
def test_br5_hedge_rule_too_big_for_the_view(no_change, view_of, explore):
    with pytest.raises(ValueError):
        HedgeRule(explore=explore)(view_of(no_change))


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_br7_from_a_complacent_warm_up(seed, check_split, picks):
    t = make_timeline(SCENARIOS["down_switch"], seed)
    warm_up = play(complacent, t, max_rounds=5)
    hedged = play(hedge_rule, t, record=warm_up)
    scouted = play(scout_rule, t, record=warm_up)
    for record in (hedged, scouted):
        for r in record.rows:
            check_split(r.bets)
    scouting = [r.round for r in hedged.rows if sum(b > 0 for b in r.bets) > 2]
    assert min(scouting, default=99) >= 6 + 2 * hedge_rule.window
    moves = [r for r, pick in enumerate(picks(scouted), start=1) if pick != t.leader]
    assert min(moves, default=99) >= 6 + scout_rule.n


def test_br7_first_round_each_rule_can_act(no_change, roles, row, view_of):
    leader, hedge, riser, _ = roles
    warm = [100 if c == leader else 0 for c in range(10)]
    warm_up = [row(r, warm, readings(warm, {leader: 60})) for r in range(1, 6)]
    falling = hedge_rows(row, roles, FALL, [24] * 6, start=6)
    assert hedge_rule(view_of(no_change, warm_up + falling[:5])) == tuple(hold(leader, hedge))
    assert hedge_rule(view_of(no_change, warm_up + falling)) == tuple(scout_split(hedge))
    beat = {leader: 60, hedge: 24, riser: 63}
    beaten = scout_rows(row, roles, [beat] * 3, start=6)
    assert picked(scout_rule(view_of(no_change, warm_up + beaten[:2]))) == leader
    assert picked(scout_rule(view_of(no_change, warm_up + beaten))) == riser


@pytest.mark.parametrize("rule", [hedge_rule, scout_rule], ids=["hedge_rule", "scout_rule"])
def test_br9_pure(rule, view_of):
    t = make_timeline(SCENARIOS["down_switch"], 4)
    record = play(rule, t)
    for k in range(len(record)):
        view = view_of(t, record.rows[:k])
        assert rule(view) == rule(view) == record.rows[k].bets
    rule(view_of(t, record.rows))
    assert rule(view_of(t, record.rows[:10])) == record.rows[10].bets


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_rule_invariants(name):
    for seed in range(3):
        t = make_timeline(SCENARIOS[name], seed)
        for r in play(hedge_rule, t).rows:
            assert r.bets[t.hedge] == hedge_rule.explore and picked(r.bets) != t.hedge
        for r in play(scout_rule, t).rows:
            assert sorted(r.bets)[:-1] == [scout_rule.s] * 9
