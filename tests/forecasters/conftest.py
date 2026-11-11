"""Fixtures for the forecasters suite, see docs/specs/forecasters/tests.md.

Every test's forecast cache is a temporary folder, so no test reads another's forecasts or the machine's own.
"""

import numpy as np
import pytest

from paranoid.baselines import QUANTILE_LEVELS
from paranoid.engine import SCENARIOS, Bets, Game, Record, Timeline, View, make_timeline

SPREAD = np.linspace(-10.0, 10.0, len(QUANTILE_LEVELS))  # strictly ascending, centred on 0


class Fake:
    """A forecaster that records its inputs and forecasts each channel's last reading, plus `lift`."""

    def __init__(self, key: str = "fake", lift: dict[int, float] | None = None, reverse: bool = False) -> None:
        self.key = key
        self.lift = lift or {}
        self.reverse = reverse
        self.calls: list[tuple[np.ndarray, np.ndarray | None]] = []

    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray:
        self.calls.append((readings.copy(), None if bets is None else bets.copy()))
        last = [column[np.isfinite(column)][-1] for column in readings.T]
        rows = np.array([centre + self.lift.get(c, 0.0) + SPREAD for c, centre in enumerate(last)])
        return rows[:, ::-1] if self.reverse else rows


def check_split(split: Bets, channels: int = 10, budget: int = 100) -> None:
    """A valid split: `channels` ints, none negative, summing to `budget`."""
    assert isinstance(split, tuple) and len(split) == channels
    assert all(type(bet) is int and bet >= 0 for bet in split)
    assert sum(split) == budget


def view_of(timeline: Timeline, record: Record | None = None, peeks: bool = False) -> View:
    """The view a policy would see after this record, built by the engine."""
    return Game(timeline, record).view(peeks)


# The suite runs with --import-mode=importlib, so tests take each helper as a fixture.


@pytest.fixture(autouse=True)
def cache_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("PARANOID_CACHE", str(tmp_path))
    return tmp_path


@pytest.fixture(name="Fake")
def fake_fixture():
    return Fake


@pytest.fixture(scope="session", name="check_split")
def check_split_fixture():
    return check_split


@pytest.fixture(scope="session", name="view_of")
def view_of_fixture():
    return view_of


@pytest.fixture
def down_switch() -> Timeline:
    return make_timeline(SCENARIOS["down_switch"], 0)
