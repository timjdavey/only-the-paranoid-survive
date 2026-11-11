"""Bets, Row and Record: the agent's own play so far. See docs/specs/engine/game.md#record."""

import operator
from collections.abc import Iterable
from dataclasses import dataclass

Bets = tuple[int, ...]  # one whole number per channel, summing to the budget


@dataclass(frozen=True)
class Row:
    round: int
    bets: Bets
    readings: tuple[float | None, ...]  # one per channel, None where the bet was 0, one decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "round", operator.index(self.round))
        object.__setattr__(self, "bets", tuple(operator.index(bet) for bet in self.bets))
        readings = tuple(None if reading is None else float(reading) for reading in self.readings)
        object.__setattr__(self, "readings", readings)

    @property
    def output(self) -> float:
        """What the bets earned: each bet times its reading, over the budget. Worked out, never stored."""
        paid = sum(bet * reading for bet, reading in zip(self.bets, self.readings) if bet > 0 and reading is not None)
        return float(paid) / sum(self.bets)


class Record:
    """The rows in round order. append is the only writer, and nothing removes a row."""

    __slots__ = ("_rows",)

    def __init__(self, rows: Iterable[Row] = ()) -> None:
        self._rows: list[Row] = list(rows)

    @property
    def rows(self) -> tuple[Row, ...]:
        return tuple(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Record):
            return NotImplemented
        return self._rows == other._rows

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Record({len(self._rows)} rows)"

    def append(self, row: Row) -> None:
        self._rows.append(row)

    def copy(self) -> "Record":
        return Record(self._rows)

    def last_bets(self) -> Bets | None:
        return self._rows[-1].bets if self._rows else None

    def readings_of(self, channel: int) -> list[tuple[int, float]]:
        """(round, reading) for the rounds where the channel had a bet, in round order."""
        return [(row.round, row.readings[channel]) for row in self._rows if row.bets[channel] > 0]

    def unchanged_rounds(self) -> list[int]:
        """Every round from 2 on whose bets equal the round before's."""
        return [now.round for before, now in zip(self._rows, self._rows[1:]) if now.bets == before.bets]
