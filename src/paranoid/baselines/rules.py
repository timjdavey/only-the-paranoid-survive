"""The hedge rule and the Scout rule, the two players that read the tell.

See docs/specs/baselines/rules.md. Neither keeps state: each call replays the record
from round 1, reading readings only, so a record another baseline wrote works too.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import ClassVar

from paranoid.engine import Bets, View, split_budget

Readings = list[dict[int, float]]  # per channel, round to reading, for the rounds it had a bet


def readings_by_channel(view: View) -> Readings:
    return [dict(view.record.readings_of(c)) for c in range(view.channels)]


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return math.fsum(values) / len(values)


def require_positive(value: float, name: str) -> None:
    if not (math.isfinite(value) and value > 0):
        raise ValueError(f"{name} must be finite and above 0, got {value}")


def require_at_least_1(value: int, name: str) -> None:
    if value < 1:
        raise ValueError(f"{name} must be at least 1, got {value}")


@dataclass(frozen=True)
class Hold:
    """The hedge rule's state for one round. `scout_start` is None while it holds."""

    pick: int
    moved_at: int
    scout_start: int | None = None


@dataclass(frozen=True)
class HedgeRule:
    """`explore` on the hedge, the rest on its pick. Scouts when the pick falls and the hedge does not rise."""

    peeks: ClassVar[bool] = False
    explore: int = 1
    window: int = 3
    fall_points: float = 8.0
    tell_points: float = 4.0
    scout_rounds: int = 1

    def __post_init__(self) -> None:
        require_at_least_1(self.explore, "explore")
        require_at_least_1(self.window, "window")
        require_at_least_1(self.scout_rounds, "scout_rounds")
        require_positive(self.fall_points, "fall_points")
        require_positive(self.tell_points, "tell_points")

    def __call__(self, view: View) -> Bets:
        if self.explore >= view.budget or view.budget - self.explore < view.channels - 1:
            raise ValueError(f"explore {self.explore} leaves too little of {view.budget} to scout {view.channels - 1}")
        state = self.state(view)
        hedge = view.start.hedge
        if state.scout_start is None:
            weights = [1 if c == state.pick else 0 for c in range(view.channels)]
        else:
            weights = [0 if c == hedge else 1 for c in range(view.channels)]
        bets = list(split_budget(weights, view.budget - self.explore))
        bets[hedge] += self.explore
        return tuple(bets)

    def state(self, view: View) -> Hold:
        """Replay rounds 2 to view.round from round 1, each from the readings below it."""
        readings, hedge = readings_by_channel(view), view.start.hedge
        state = Hold(pick=view.start.leader, moved_at=1)
        for r in range(2, view.round + 1):
            state = self.step(state, r, readings, hedge)
        return state

    def step(self, state: Hold, r: int, readings: Readings, hedge: int) -> Hold:
        if state.scout_start is not None:
            if r < state.scout_start + self.scout_rounds:
                return state
            scouted = range(state.scout_start, r)
            pick = best_by_mean([c for c in range(len(readings)) if c != hedge], scouted, readings)
            return Hold(pick=state.pick if pick is None else pick, moved_at=r)
        if self.falls_without_tell(state, r, readings[state.pick], readings[hedge]):
            return replace(state, scout_start=r)
        return state

    def falls_without_tell(self, state: Hold, r: int, pick: dict[int, float], hedge: dict[int, float]) -> bool:
        """The fall test on the rounds since moved_at, below r, where the pick and the hedge both read."""
        both = [k for k in range(state.moved_at, r) if k in pick and k in hedge]
        if len(both) < 2 * self.window:
            return False
        recent, earlier = both[-self.window :], both[: -self.window]
        falls = mean(pick[k] for k in recent) < mean(pick[k] for k in earlier) - self.fall_points
        tells = mean(hedge[k] for k in recent) - mean(hedge[k] for k in earlier) > self.tell_points
        return falls and not tells


def best_by_mean(channels: Iterable[int], rounds: range, readings: Readings) -> int | None:
    """The channel with the highest mean over the rounds it read in, lowest index on a tie. None if none read."""
    best, top = None, -math.inf
    for c in channels:
        values = [readings[c][k] for k in rounds if k in readings[c]]
        if values and mean(values) > top:
            best, top = c, mean(values)
    return best


@dataclass(frozen=True)
class Pick:
    """The Scout rule's state for one round."""

    pick: int
    moved_at: int


@dataclass(frozen=True)
class ScoutRule:
    """`s` on every channel but its pick. Moves when a channel beats the pick `n` rounds running and the hedge holds."""

    peeks: ClassVar[bool] = False
    s: int = 1
    n: int = 3
    tell_points: float = 4.0

    def __post_init__(self) -> None:
        require_at_least_1(self.s, "s")
        require_at_least_1(self.n, "n")
        require_positive(self.tell_points, "tell_points")

    def __call__(self, view: View) -> Bets:
        if self.s * (view.channels - 1) >= view.budget:
            raise ValueError(f"s {self.s} on {view.channels - 1} channels leaves nothing of {view.budget}")
        pick = self.state(view).pick
        rest = view.budget - self.s * (view.channels - 1)
        return tuple(rest if c == pick else self.s for c in range(view.channels))

    def state(self, view: View) -> Pick:
        readings, hedge = readings_by_channel(view), view.start.hedge
        state = Pick(pick=view.start.leader, moved_at=1)
        for r in range(2, view.round + 1):
            state = self.step(state, r, readings, hedge)
        return state

    def step(self, state: Pick, r: int, readings: Readings, hedge: int) -> Pick:
        """The move test, once n rounds have passed since moved_at."""
        if r - state.moved_at < self.n:
            return state
        last = range(r - self.n, r)
        pick, hedged = readings[state.pick], readings[hedge]
        if any(k not in pick or k not in hedged for k in last):
            return state
        candidates = [
            c
            for c in range(len(readings))
            if c not in (state.pick, hedge) and all(k in readings[c] and readings[c][k] > pick[k] for k in last)
        ]
        if not candidates:
            return state
        earlier = [k for k in range(state.moved_at, r - self.n) if k in hedged]
        if earlier and mean(hedged[k] for k in last) - mean(hedged[k] for k in earlier) > self.tell_points:
            return state
        return Pick(pick=best_by_mean(candidates, last, readings), moved_at=r)


hedge_rule = HedgeRule()
scout_rule = ScoutRule()
