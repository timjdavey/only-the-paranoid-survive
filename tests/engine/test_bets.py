"""EG1 to EG9: bets, readings and output, see docs/specs/engine/tests.md#game."""

import dataclasses
import math

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, BetError, Game, make_timeline

FIRST = [100] + [0] * 9

BAD_SPLITS = {
    "nine values": ([10] * 9, "shape"),
    "eleven values summing wrong": ([10] * 11, "shape"),
    "a bool": ([True] + [11] * 9, "shape"),
    "a float": ([10.0] + [10] * 9, "shape"),
    "a string": (["10"] + [10] * 9, "shape"),
    "not a sequence": (100, "shape"),
    "a negative": ([-10, 30] + [10] * 8, "sign"),
    "too much": ([11] + [10] * 9, "sum"),
    "too little": ([9] + [10] * 9, "sum"),
}


@pytest.mark.parametrize("split, check", BAD_SPLITS.values(), ids=BAD_SPLITS.keys())
def test_eg1_bad_splits(timeline, split, check):
    with pytest.raises(BetError) as error:
        Game(timeline).play(split)
    assert error.value.check == check
    assert str(error.value) == f"Bad tool call: {check}."
    assert isinstance(error.value, ValueError)


def test_eg1_numpy_ints_pass(timeline):
    row = Game(timeline).play([np.int64(10)] * 10)
    assert row.bets == (10,) * 10


def test_eg2_bet_error_changes_nothing(timeline):
    game = Game(timeline)
    game.play(FIRST)
    before = (game.round, game.done, len(game.record))
    with pytest.raises(BetError):
        game.play([1] * 10)
    assert (game.round, game.done, len(game.record)) == before


def test_eg3_inertia():
    config = dataclasses.replace(SCENARIOS["no_change"], inertia_cap=20)
    game = Game(make_timeline(config, 0))
    game.play(FIRST)
    with pytest.raises(BetError) as error:
        game.play([79, 21] + [0] * 8)
    assert error.value.check == "inertia"
    game.play([80, 20] + [0] * 8)
    assert game.round == 3


def test_eg4_readings(timeline, hand_built):
    t = hand_built(timeline, read_noise_z=np.ones_like(timeline.read_noise_z))
    k, game = t.config.read_noise_k, Game(t)
    first = game.play([4, 16, 80] + [0] * 7)
    level = t.levels[0]
    assert first.readings[:3] == (
        round(float(level[0]) + k / 2, 1),
        round(float(level[1]) + k / 4, 1),
        round(float(level[2]) + k / math.sqrt(80), 1),
    )
    second = game.play(FIRST)
    assert second.readings[0] == round(float(t.levels[1, 0]) + k / 10, 1)


def test_eg5_unfunded_channels_read_none(timeline):
    row = Game(timeline).play([50, 0, 25, 0, 25, 0, 0, 0, 0, 0])
    assert [r is None for r in row.readings] == [b == 0 for b in row.bets]


def test_eg6_output_is_exact(timeline, hand_built):
    t = hand_built(timeline, read_noise_z=np.full_like(timeline.read_noise_z, 2.0))
    bets = [40, 30, 30] + [0] * 7
    row = Game(t).play(bets)
    exact = sum(b / 100 * float(level) for b, level in zip(bets, t.levels[0]))
    from_readings = sum(b / 100 * r for b, r in zip(bets, row.readings) if r is not None)
    assert row.output == round(exact, 1)
    assert row.output != round(from_readings, 1)


def test_eg7_negative_reading(timeline, hand_built):
    z = np.zeros_like(timeline.read_noise_z)
    z[0, 0] = -3.0
    t = hand_built(timeline, levels=np.ones_like(timeline.levels), read_noise_z=z)
    row = Game(t).play([1, 99] + [0] * 8)
    assert row.readings[0] == round(1.0 - t.config.read_noise_k * 3.0, 1) < 0


def test_eg8_finished_game(timeline):
    game = Game(timeline)
    for _ in range(timeline.config.rounds):
        assert not game.done
        game.play(FIRST)
    assert game.done
    with pytest.raises(RuntimeError):
        game.play(FIRST)


@pytest.mark.parametrize(
    "bets",
    [[10] * 10, np.array([10] * 10), tuple(np.int64(10) for _ in range(10))],
    ids=["list", "array", "tuple of np.int64"],
)
def test_eg9_bets_are_stored_as_ints(timeline, bets):
    game = Game(timeline)
    row = game.play(bets)
    assert type(row.bets) is tuple
    assert all(type(b) is int for b in row.bets)
    assert row is game.record.rows[-1]
