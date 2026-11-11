"""EG11 to EG20: the record, starting part way, play and view, see docs/specs/engine/tests.md#game."""

import dataclasses
from typing import ClassVar

import numpy as np
import pytest

from paranoid.engine import BetError, Game, Record, Row, View, play

A = (100,) + (0,) * 9
B = (0, 100) + (0,) * 8


def played(timeline, *splits) -> Game:
    game = Game(timeline)
    for split in splits:
        game.play(split)
    return game


def test_eg11_unchanged_rounds(timeline):
    assert played(timeline, A, A, B, B, A).record.unchanged_rounds() == [2, 4]


def test_eg12_readings_of(timeline):
    record = played(timeline, A, B, A, (50, 50) + (0,) * 8).record
    assert [r for r, _ in record.readings_of(0)] == [1, 3, 4]
    assert [r for r, _ in record.readings_of(1)] == [2, 4]
    assert record.readings_of(2) == []
    assert all(isinstance(reading, float) for _, reading in record.readings_of(0))


def test_eg13_starting_part_way(timeline):
    rows = played(timeline, A, A, A, A).record.rows
    with pytest.raises(ValueError):
        Game(timeline, Record([rows[0], rows[1], rows[3]]))
    too_many = [dataclasses.replace(rows[0], round=r) for r in range(1, timeline.config.rounds + 2)]
    with pytest.raises(ValueError):
        Game(timeline, Record(too_many))
    with pytest.raises(ValueError):
        Game(timeline, Record([dataclasses.replace(rows[0], bets=(50,) * 10)]))
    assert Game(timeline, Record(rows[:3])).round == 4


def test_eg14_warm_up(timeline, on_first):
    warm_up = play(on_first, timeline, max_rounds=5)
    assert len(warm_up) == 5
    full = play(on_first, timeline, record=warm_up)
    assert len(full) == timeline.config.rounds
    assert len(warm_up) == 5
    assert full.rows[:5] == warm_up.rows


def test_eg15_bad_policy_raises(timeline):
    @dataclasses.dataclass(frozen=True)
    class Bad:
        peeks: ClassVar[bool] = False

        def __call__(self, view: View):
            return (1,) * view.channels

    with pytest.raises(BetError):
        play(Bad(), timeline)


@pytest.mark.parametrize("peeks", [True, False])
def test_eg16_peeking(timeline, peeks):
    seen = []

    @dataclasses.dataclass(frozen=True)
    class Recording:
        def __call__(self, view: View):
            seen.append(view.timeline)
            return A

    Recording.peeks = peeks
    play(Recording(), timeline, max_rounds=3)
    assert seen == [timeline if peeks else None] * 3


def test_eg17_determinism(timeline, even):
    assert play(even, timeline) == play(even, timeline)


def test_eg18_view(timeline):
    game = played(timeline, A, B)
    view = game.view(False)
    assert view.round == game.round == 3
    assert view.channels == 10 and view.budget == 100
    assert view.start.leader == timeline.leader
    assert view.start.runner_up == timeline.runner_up
    assert view.start.hedge == timeline.hedge
    assert view.start.field == timeline.field
    assert view.record == game.record
    assert view.timeline is None
    assert game.view(True).timeline is timeline


def test_eg19_wrong_shape_fails_at_once(timeline, hand_built):
    bad = hand_built(timeline, levels=np.zeros((timeline.config.rounds, 3)))
    with pytest.raises(ValueError):
        Game(bad)


def test_eg20_rows_are_read_only(timeline):
    record = played(timeline, A, B).record
    with pytest.raises(AttributeError):
        record.rows = ()
    with pytest.raises(AttributeError):
        record.rows.append(record.rows[0])
    copy = record.copy()
    assert copy == record and copy is not record
    copy.append(record.rows[0])
    assert len(record) == 2


def test_eg20_record_constructor_and_row_casts():
    assert Record() == Record(rows=()) and len(Record()) == 0
    assert Record().last_bets() is None
    row = Row(round=np.int64(1), bets=[np.int64(100)] + [0] * 9, readings=[1] + [None] * 9)
    assert row.bets == A and type(row.bets[0]) is int
    assert row.readings[0] == 1.0 and type(row.readings[0]) is float
    assert type(row.round) is int and type(row.output) is float
