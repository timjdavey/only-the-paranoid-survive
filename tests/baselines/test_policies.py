"""BP1 to BP6, BP9, BP10 and BP13, see docs/specs/baselines/tests.md#policies."""

import dataclasses

import numpy as np
import pytest

from paranoid.baselines import complacent, discerning, perfect, uniform
from paranoid.engine import SCENARIOS, make_timeline, play

FIXED = {"uniform": uniform, "discerning": discerning, "complacent": complacent, "perfect": perfect}
SEEDS = range(50)


@pytest.mark.parametrize("name", list(SCENARIOS))
@pytest.mark.parametrize("policy", list(FIXED.values()), ids=list(FIXED))
def test_bp1_fixed_baselines_play_valid_splits(policy, name, check_split):
    for seed in SEEDS:
        record = play(policy, make_timeline(SCENARIOS[name], seed))
        assert len(record) == SCENARIOS[name].rounds
        for r in record.rows:
            check_split(r.bets)


def test_bp2_uniform_ignores_the_view(no_change, view_of):
    other = make_timeline(SCENARIOS["down_switch"], 7)
    record = play(uniform, other, max_rounds=9)
    views = [view_of(no_change), view_of(other, record.rows), view_of(other, record.rows, peeks=True)]
    assert {uniform(v) for v in views} == {(10,) * 10}


def test_bp3_complacent_equals_discerning_on_round_1(view_of):
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["down_switch"], seed)
        assert complacent(view_of(t)) == discerning(view_of(t, peeks=True))
    for seed in range(5):
        t = make_timeline(SCENARIOS["no_change"], seed)
        assert play(complacent, t) == play(discerning, t)


def test_bp4_discerning_moves_at_the_switch(picks):
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["down_switch"], seed)
        chosen = picks(play(discerning, t))
        moved = next(r for r, pick in enumerate(chosen, start=1) if pick != t.leader)
        passed = next(r for r in range(1, t.config.rounds + 1) if t.climate_leader(r) != t.leader)
        assert moved == passed
        assert moved >= t.events[0].onset


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_bp5_perfect_beats_discerning_every_round(name):
    for seed in SEEDS:
        t = make_timeline(SCENARIOS[name], seed)
        best, yardstick = play(perfect, t), play(discerning, t)
        assert all(p.output >= d.output for p, d in zip(best.rows, yardstick.rows))


@pytest.mark.parametrize("policy", [uniform, complacent], ids=["uniform", "complacent"])
def test_bp6_non_peeking_ignore_the_timeline(policy, view_of):
    t = make_timeline(SCENARIOS["switch_then_shock"], 3)
    record = play(policy, t)
    for k in range(len(record)):
        rows = record.rows[:k]
        assert policy(view_of(t, rows, peeks=False)) == policy(view_of(t, rows, peeks=True))


@pytest.mark.parametrize("policy", list(FIXED.values()), ids=list(FIXED))
def test_bp9_peeks_is_a_class_var(policy):
    assert isinstance(policy.peeks, bool)
    assert "peeks" not in {f.name for f in dataclasses.fields(policy)}
    assert callable(policy)
    assert dataclasses.is_dataclass(policy) and type(policy).__dataclass_params__.frozen


def test_bp9_only_the_yardstick_peeks():
    assert {name for name, policy in FIXED.items() if policy.peeks} == {"discerning", "perfect"}


def test_bp10_discerning_never_moves_on_a_short_up_switch(picks):
    config = SCENARIOS["up_switch"]
    shorts = (t for t in (make_timeline(config, s) for s in range(1000)) if t.events[0].numbers["short"])
    for _, t in zip(SEEDS, shorts):
        assert set(picks(play(discerning, t))) == {t.leader}


def test_bp10_discerning_goes_to_the_sleeper_and_back(picks):
    for seed in SEEDS:
        t = make_timeline(SCENARIOS["up_switch_then_down_switch"], seed)
        chosen = picks(play(discerning, t))
        moves = [(a, b) for a, b in zip(chosen, chosen[1:]) if a != b]
        assert moves == [(t.leader, t.sleeper), (t.sleeper, t.leader)]
        assert chosen[-1] == t.leader


def test_bp13_discerning_ignores_a_one_channel_shock():
    config = dataclasses.replace(SCENARIOS["one_shock"], one_channel_shock=True)
    for seed in range(20):
        shocked = play(discerning, make_timeline(config, seed))
        calm = play(discerning, make_timeline(SCENARIOS["no_change"], seed))
        assert [r.bets for r in shocked.rows] == [r.bets for r in calm.rows]


def test_discerning_and_perfect_break_ties_low(no_change, view_of):
    flat = np.full((no_change.config.rounds, 10), 50.0)
    t = dataclasses.replace(no_change, base=flat, levels=flat)
    view = view_of(t, peeks=True)
    assert discerning(view) == perfect(view) == (100,) + (0,) * 9
