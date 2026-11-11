"""Game, BetError and play: the round loop. See docs/specs/engine/game.md."""

import math
from collections.abc import Sequence

from .record import Bets, Record, Row
from .specs import is_whole
from .timeline import Timeline
from .view import Dials, Policy, Start, View

ARRAYS = ("levels", "base", "weather", "loadings", "impulse", "read_noise_z")


class BetError(ValueError):
    """A split that fails a check. The message is generic, the harness answers with the skin's words."""

    def __init__(self, check: str) -> None:
        self.check = check  # shape, sign, sum or inertia
        super().__init__(f"Bad tool call: {check}.")


def check_timeline(timeline: Timeline) -> None:
    config = timeline.config
    for name in ARRAYS:
        if getattr(timeline, name).shape != (config.rounds, config.channels):
            raise ValueError(f"timeline.{name} must have shape ({config.rounds}, {config.channels})")
    if timeline.factor.shape != (config.rounds,):
        raise ValueError(f"timeline.factor must have shape ({config.rounds},)")


def check_record(record: Record, timeline: Timeline) -> None:
    config = timeline.config
    if len(record) > config.rounds:
        raise ValueError(f"the record has {len(record)} rows, more than {config.rounds} rounds")
    for expected, row in enumerate(record.rows, start=1):
        if row.round != expected:
            raise ValueError(f"the record's rounds must be 1, 2, 3… in order, found {row.round} at {expected}")
        if len(row.bets) != config.channels or len(row.readings) != config.channels:
            raise ValueError(f"round {row.round} does not have {config.channels} channels")
        if sum(row.bets) != config.budget or min(row.bets) < 0:
            raise ValueError(f"round {row.round}'s bets do not split the budget of {config.budget}")


class Game:
    def __init__(self, timeline: Timeline, record: Record | None = None) -> None:
        check_timeline(timeline)
        record = Record() if record is None else record.copy()
        check_record(record, timeline)
        self.timeline = timeline
        self.record = record  # the game's own copy

    @property
    def round(self) -> int:
        """The round about to be played, from 1."""
        return len(self.record) + 1

    @property
    def done(self) -> bool:
        return self.round > self.timeline.config.rounds

    def view(self, peeks: bool) -> View:
        t, config = self.timeline, self.timeline.config
        return View(
            round=self.round,
            channels=config.channels,
            budget=config.budget,
            start=Start(leader=t.leader, runner_up=t.runner_up, hedge=t.hedge, field=t.field),
            dials=Dials(
                rounds=config.rounds,
                own_scale=config.own_scale,
                persistence=config.persistence,
                factor_scale=config.factor_scale,
                read_noise_k=config.read_noise_k,
                leader_base=config.leader_base,
                runner_up_gap_points=config.runner_up_gap_points,
                field_base=config.field_base,
                hedge_base=config.hedge_base,
            ),
            record=self.record.copy(),
            timeline=t if peeks else None,
        )

    def check(self, bets: Sequence[int]) -> Bets:
        """Check a split in the spec's order and return it as a tuple of int."""
        config = self.timeline.config
        try:
            values = list(bets)
        except TypeError:
            raise BetError("shape") from None
        if len(values) != config.channels or not all(is_whole(v) for v in values):
            raise BetError("shape")
        split = tuple(int(v) for v in values)
        if any(v < 0 for v in split):
            raise BetError("sign")
        if sum(split) != config.budget:
            raise BetError("sum")
        before = self.record.last_bets()
        cap = config.inertia_cap
        if cap is not None and before is not None and any(abs(a - b) > cap for a, b in zip(split, before)):
            raise BetError("inertia")
        return split

    def play(self, bets: Sequence[int]) -> Row:
        """Play one round and return the row it appended."""
        if self.done:
            raise RuntimeError("the game is finished")
        split = self.check(bets)
        t, config = self.timeline, self.timeline.config
        row = self.round - 1
        levels = [float(level) for level in t.levels[row]]
        readings = tuple(
            None if bet == 0 else round(levels[c] + config.read_noise_k / math.sqrt(bet) * float(t.read_noise_z[row, c]), 1)
            for c, bet in enumerate(split)
        )
        played = Row(round=self.round, bets=split, readings=readings)
        self.record.append(played)
        return played


def play(policy: Policy, timeline: Timeline, *, max_rounds: int | None = None, record: Record | None = None) -> Record:
    """Run a policy to the end, or for max_rounds rounds from where the record left off."""
    game = Game(timeline, record)
    played = 0
    while not game.done and (max_rounds is None or played < max_rounds):
        game.play(policy(game.view(policy.peeks)))
        played += 1
    return game.record
