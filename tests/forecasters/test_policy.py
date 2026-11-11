"""FP1 to FP10, see docs/specs/forecasters/tests.md#policy."""

import dataclasses
from dataclasses import replace

import numpy as np
import pytest

from paranoid.baselines import FORECAST_RULES, complacent, uniform
from paranoid.engine import SCENARIOS, make_timeline, play
from paranoid.forecasters import TIMESTRAL_POLICIES, ForecastPolicy, Timestral, timestral

IDS = ("top-pick", "odds", "explore-1", "explore-2", "explore-5", "odds-bet-aware")


def with_fake(name: str, fake) -> ForecastPolicy:
    return replace(TIMESTRAL_POLICIES[name], forecaster=fake)


def test_fp1_what_the_forecaster_is_sent(Fake, down_switch):
    fake = Fake()
    record = play(with_fake("top-pick", fake), down_switch)
    assert record.rows[0].bets == (10,) * 10  # uniform's split
    assert len(fake.calls) == len(record) - 1  # never called for round 1
    first, second = fake.calls[0][0], fake.calls[1][0]
    assert first.shape == (1, 10) and np.isfinite(first).all()
    assert second.shape == (2, 10) and np.isnan(second[-1]).sum() == 9
    assert all(bets is None for _, bets in fake.calls)


def test_fp2_bets_go_in_when_asked(Fake, down_switch):
    fake = Fake()
    record = play(ForecastPolicy(FORECAST_RULES["odds"], with_bets=True, forecaster=fake), down_switch, max_rounds=4)
    for (readings, bets), rounds in zip(fake.calls, (1, 2, 3)):
        assert bets.dtype == np.float64 and bets.shape == readings.shape == (rounds, 10)
        assert np.array_equal(bets, np.array([row.bets for row in record.rows[:rounds]], dtype=float))


def test_fp3_a_channel_never_read_is_left_out(Fake, down_switch, view_of):
    view = view_of(down_switch, play(complacent, down_switch, max_rounds=5))
    leader = view.start.leader
    fake = Fake()
    quantiles = with_fake("top-pick", fake).forecast(view).quantiles
    assert fake.calls[0][0].shape == (5, 1)
    assert np.isnan(quantiles).all(axis=1).sum() == 9 and np.isfinite(quantiles[leader]).all()
    assert with_fake("explore-1", fake)(view) == tuple(91 if c == leader else 1 for c in range(10))
    assert with_fake("top-pick", fake)(view) == tuple(100 if c == leader else 0 for c in range(10))


def test_fp4_the_reply_is_sorted_and_checked(Fake, down_switch, view_of):
    view = view_of(down_switch, play(uniform, down_switch, max_rounds=3))
    for name in ("top-pick", "odds"):
        assert with_fake(name, Fake("up"))(view) == with_fake(name, Fake("down", reverse=True))(view)

    class Bad(Fake):
        def __init__(self, key, spoil):
            super().__init__(key)
            self.spoil = spoil

        def __call__(self, readings, bets):
            return self.spoil(super().__call__(readings, bets))

    def with_nan(rows):
        rows[0, 0] = np.nan
        return rows

    for key, spoil in (("columns", lambda rows: rows[:, :20]), ("rows", lambda rows: rows[:-1]), ("nan", with_nan)):
        with pytest.raises(ValueError):
            with_fake("top-pick", Bad(key, spoil))(view)


def test_fp5_the_cache(Fake, down_switch, view_of, cache_folder):
    record = play(uniform, down_switch, max_rounds=3)
    view = view_of(down_switch, record)
    fake = Fake()
    policy = with_fake("odds", fake)
    first, second = policy.forecast(view), policy.forecast(view)
    assert len(fake.calls) == 1
    assert first.cache_key == second.cache_key and np.array_equal(first.quantiles, second.quantiles)
    assert (cache_folder / "forecasts" / f"{first.cache_key}.npy").is_file()

    last = record.rows[-1]
    readings = (last.readings[0] + 0.1, *last.readings[1:])
    moved = view_of(down_switch, type(record)([*record.rows[:-1], replace(last, readings=readings)]))
    others = (
        with_fake("odds", Fake("another")).forecast(view),
        replace(policy, with_bets=True).forecast(view),
        policy.forecast(moved),
    )
    assert len({first.cache_key, *(other.cache_key for other in others)}) == 4


def test_fp6_a_second_play_never_calls_the_forecaster(Fake, down_switch):
    fake = Fake()
    policy = with_fake("explore-2", fake)
    first = play(policy, down_switch)
    calls = len(fake.calls)
    assert play(policy, down_switch) == first
    assert len(fake.calls) == calls


def test_fp7_the_policy_is_pure(Fake, down_switch, view_of):
    policy = with_fake("odds", Fake())
    empty = view_of(down_switch)
    assert policy.forecast(empty) is None and policy.rounded_out(empty) is False
    assert policy(empty) == uniform(empty)

    record = play(uniform, down_switch, max_rounds=4)
    before = record.copy()
    view = view_of(down_switch, record)
    quantiles = policy.forecast(view).quantiles
    with pytest.raises(ValueError):
        quantiles[0, 0] = 0.0
    assert policy(view) == policy(view_of(down_switch, record, peeks=True))
    assert view.timeline is None and record == before


def test_fp8_rounded_out(Fake, down_switch, view_of):
    view = view_of(down_switch, play(uniform, down_switch, max_rounds=2))
    fake = Fake(lift={0: 1000.0})
    assert with_fake("odds", fake)(view) == (100, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert with_fake("odds", fake).rounded_out(view) is True
    assert with_fake("top-pick", fake).rounded_out(view) is False
    assert with_fake("explore-1", fake).rounded_out(view) is False


def test_fp9_the_six_policies():
    assert tuple(TIMESTRAL_POLICIES) == IDS
    with pytest.raises(TypeError):
        TIMESTRAL_POLICIES["nope"] = TIMESTRAL_POLICIES["odds"]
    for name, policy in TIMESTRAL_POLICIES.items():
        aware = name == "odds-bet-aware"
        assert policy.rule is FORECAST_RULES["odds" if aware else name]
        assert policy.with_bets is aware
        assert policy.forecaster == (Timestral(joint=False) if aware else timestral)
        assert policy.peeks is False and "peeks" not in {field.name for field in dataclasses.fields(policy)}


@pytest.mark.parametrize("name", IDS)
def test_fp10_valid_splits_on_whole_runs(name, Fake, check_split):
    for scenario in ("one_shock", "down_switch", "up_switch"):
        timeline = make_timeline(SCENARIOS[scenario], 0)
        record = play(with_fake(name, Fake()), timeline)
        assert len(record) == timeline.config.rounds
        for row in record.rows:
            check_split(row.bets)
