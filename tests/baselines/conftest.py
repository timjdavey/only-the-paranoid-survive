"""Fixtures for the baselines suite, see docs/specs/baselines/tests.md#three-sizes.

Views come from the engine's own Game, so a hand-built view is exactly what `play` would hand a policy.
"""

import dataclasses
import math
from collections.abc import Sequence

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, Bets, Game, Record, Row, Timeline, View, make_timeline


def check_split(split: Bets, channels: int = 10, budget: int = 100) -> None:
    """A valid split: `channels` ints, none negative, summing to `budget`."""
    assert isinstance(split, tuple) and len(split) == channels
    assert all(type(bet) is int and bet >= 0 for bet in split)
    assert sum(split) == budget


def row(number: int, bets: Sequence[int], readings: Sequence[float | None]) -> Row:
    """A hand-written row. Output is the bet-weighted mean of the readings, which no rule reads."""
    output = math.fsum(b * (r or 0.0) for b, r in zip(bets, readings)) / sum(bets)
    return Row(round=number, bets=tuple(bets), readings=tuple(readings), output=round(output, 1))


def view_of(timeline: Timeline, rows: Sequence[Row] = (), peeks: bool = False) -> View:
    """The view a policy would see after these rows, built by the engine."""
    return Game(timeline, Record(rows)).view(peeks)


def scripted(timeline: Timeline, levels: np.ndarray) -> Timeline:
    """A timeline whose levels are the climate exactly: no weather, no shared factor, no read noise."""
    levels = np.array(levels, dtype=float)
    zeros = np.zeros_like(levels)
    arrays = {
        "levels": levels,
        "base": levels,
        "weather": zeros,
        "factor": np.zeros(levels.shape[0]),
        "impulse": zeros,
        "read_noise_z": zeros,
    }
    for array in arrays.values():
        array.setflags(write=False)
    return dataclasses.replace(timeline, **arrays)


def picks(record: Record) -> list[int]:
    """The channel with the most points in each round, lowest index on a tie."""
    return [int(np.argmax(r.bets)) for r in record.rows]


# The suite runs with --import-mode=importlib, so tests take each helper as a fixture.


@pytest.fixture(scope="session", name="check_split")
def check_split_fixture():
    return check_split


@pytest.fixture(scope="session", name="row")
def row_fixture():
    return row


@pytest.fixture(scope="session", name="view_of")
def view_of_fixture():
    return view_of


@pytest.fixture(scope="session", name="scripted")
def scripted_fixture():
    return scripted


@pytest.fixture(scope="session", name="picks")
def picks_fixture():
    return picks


@pytest.fixture
def no_change() -> Timeline:
    return make_timeline(SCENARIOS["no_change"], 0)
