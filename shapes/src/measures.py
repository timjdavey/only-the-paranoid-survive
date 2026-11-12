"""The tools every purpose in criteria.py measures with. See shapes/README.md#the-test.

Every measure of an event reads twin timelines: one seed's event timeline minus its No change timeline is the
event's effect alone, with the weather taken out. A measure from the agent's seat reads readings, which add read
noise to levels as the game does.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from paranoid.engine import ScenarioConfig, Timeline, make_timeline

WINDOW = 8  # rounds from onset in which holding is a real question
SEEN = 3  # rounds from onset an agent has to tell a switch from a shock, in the levels rows
SEATS = {"all on the leader": 0, "one point on each other channel": 1, "four points on each": 4}  # points on each other


@dataclass(frozen=True)
class Row:
    measure: str
    value: str


class Twins:
    """Every timeline the criteria read in one world, made once per seed."""

    NAMES = ("no_change", "one_shock", "down_switch", "up_switch", "slow_drift")

    def __init__(self, world: Mapping[str, ScenarioConfig], seeds: Sequence[int]):
        self.world, self.seeds = world, list(seeds)
        self.by_name = {name: [make_timeline(world[name], s) for s in self.seeds] for name in self.NAMES}

    def pairs(self, name: str):
        return zip(self.by_name["no_change"], self.by_name[name])


# --- formatting ------------------------------------------------------------


def share(flags) -> str:
    return f"{np.mean(flags):.2f}"


def spread(values, digits: int = 1) -> str:
    """The median, then the 10th to 90th percentile."""
    low, mid, high = np.percentile(values, [10, 50, 90])
    return f"{mid:.{digits}f} ({low:.{digits}f} to {high:.{digits}f})"


def counts(values) -> str:
    """The mean, then the 10th to 90th percentile, for a count of rounds or channels."""
    low, high = (f"{x:g}" if float(x).is_integer() else f"{x:.1f}" for x in np.percentile(values, [10, 90]))
    return f"{np.mean(values):.1f} ({low} to {high})"


# --- one timeline ----------------------------------------------------------


def others_max(levels: np.ndarray, channel: int) -> np.ndarray:
    return np.delete(levels, channel, axis=1).max(axis=1)


def longest_run(flags: np.ndarray) -> int:
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


def worst_fall(series: np.ndarray, rounds: int) -> float:
    """The deepest fall over `rounds` rounds anywhere in the series."""
    return float((series[:-rounds] - series[rounds:]).max())


def swaps(before: np.ndarray, after: np.ndarray) -> int:
    """Pairs of channels whose order flips."""
    above_before = before[:, None] > before[None, :]
    above_after = after[:, None] > after[None, :]
    return int(np.triu(above_before != above_after, k=1).sum())


def sigma(timeline: Timeline) -> float:
    return timeline.config.own_scale


def onset_row(timeline: Timeline) -> int:
    return timeline.events[0].onset - 1


def storm_of(event) -> dict | None:
    """The storm keys of a shock, or of a storm switch with the prefix taken off. None for a quiet event."""
    n = event.numbers
    if event.shape == "shock":
        return dict(n)
    if event.shape == "switch" and n.get("storm_depth") is not None:
        return {key[len("storm_") :]: value for key, value in n.items() if key.startswith("storm_")}
    return None


def trough_row(timeline: Timeline) -> int:
    """The row of the first event's trough. The onset row for a quiet event."""
    storm = storm_of(timeline.events[0])
    if storm is None:
        return onset_row(timeline)
    return onset_row(timeline) + (storm["half_life"] if storm["profile"] == "slide" else 0)


def pop_channel(timeline: Timeline) -> int | None:
    storm = storm_of(timeline.events[0])
    return storm["pop_channel"] if storm else None


def before_weather(calm: Timeline, event: Timeline) -> np.ndarray:
    """The event's levels with the weather taken out: base plus the event's effect on level beyond base."""
    return event.base + (event.levels - calm.levels) - (event.base - calm.base)


def switch_kind(timeline: Timeline) -> str:
    numbers = timeline.events[0].numbers
    if numbers["kind"] == "rise" and numbers["short"]:
        return "rise_short"
    return str(numbers["kind"])


def first_change(timeline: Timeline) -> int | None:
    """Rounds from onset until the climate leader is not the leader, or None if it never changes."""
    changed = np.flatnonzero(np.argmax(timeline.base[onset_row(timeline) :], axis=1) != timeline.leader)
    return int(changed[0]) if len(changed) else None


# --- the agent's seat ------------------------------------------------------


def seat_bets(timeline: Timeline, each: int) -> np.ndarray:
    """`each` points on every channel but the leader, the rest on the leader."""
    channels, budget = timeline.config.channels, timeline.config.budget
    bets = np.full(channels, each, dtype=float)
    bets[timeline.leader] = budget - each * (channels - 1)
    return bets


def readings(timeline: Timeline, bets: np.ndarray, k: float) -> np.ndarray:
    """Every round's readings for a fixed split, to one decimal as the game rounds them. NaN where the bet is 0."""
    with np.errstate(divide="ignore", invalid="ignore"):
        noise = np.where(bets > 0, k / np.sqrt(bets), np.nan)
    return np.round(timeline.levels + noise * timeline.read_noise_z, 1)


def chase_against_hold(timeline: Timeline, k: float) -> float:
    """From the one point seat: move the big bet each round to last round's best reading, against never moving."""
    hold = seat_bets(timeline, 1)
    budget, big = timeline.config.budget, hold[timeline.leader]
    held = (timeline.levels @ hold).sum() / budget
    bets, chased = hold.copy(), 0.0
    for row in range(timeline.config.rounds):
        chased += timeline.levels[row] @ bets / budget
        seen = timeline.levels[row] + k / np.sqrt(bets) * timeline.read_noise_z[row]
        bets = np.ones_like(hold)
        bets[int(np.argmax(np.round(seen, 1)))] = big
    return float((chased - held) / timeline.config.rounds)


# --- telling a switch from a shock -----------------------------------------


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """The chance a random switch scores above a random shock, ties counted half."""
    positive, negative = scores[labels == 1], scores[labels == 0]
    above = (positive[:, None] > negative[None, :]).mean()
    tied = (positive[:, None] == negative[None, :]).mean()
    return float(above + 0.5 * tied)


def fisher_auc(features: np.ndarray, labels: np.ndarray, train: np.ndarray) -> float:
    """Fit Fisher's linear discriminant on the train rows and read its AUC on the rest."""
    x, y = features[train], labels[train]
    mean_0, mean_1 = x[y == 0].mean(axis=0), x[y == 1].mean(axis=0)
    pooled = np.cov(x[y == 0], rowvar=False) + np.cov(x[y == 1], rowvar=False)
    pooled = np.atleast_2d(pooled) + 1e-6 * np.eye(features.shape[1])
    weights = np.linalg.solve(pooled, mean_1 - mean_0)
    return auc(features[~train] @ weights, labels[~train])


def moves(seen: np.ndarray, timeline: Timeline, rounds: int) -> np.ndarray:
    """Each channel's value in `rounds` rounds from onset, less its mean over the three rounds before."""
    row = onset_row(timeline)
    return seen[row : row + rounds] - seen[row - 3 : row].mean(axis=0)


def features(moved: np.ndarray, leader: int, field: bool) -> np.ndarray:
    """The leader's move each round, and with the field the median and largest move of the others."""
    if not field:
        return moved[:, leader]
    rest = np.delete(moved, leader, axis=1)
    return np.concatenate([moved[:, leader], np.median(rest, axis=1), rest.max(axis=1)])


def tell_apart(shocks: Sequence[Timeline], switches: Sequence[Timeline], view) -> float:
    """How well `view`, a function of one timeline, tells Down switch from One shock, as an AUC."""
    labels = np.array([0] * len(shocks) + [1] * len(switches))
    train = np.array([i % 2 == 0 for i in range(len(shocks))] * 2)
    return fisher_auc(np.array([view(t) for t in [*shocks, *switches]]), labels, train)


def moved_at(calm: Timeline, event: Timeline, offset: int) -> int:
    """Channels the event alone moves by more than one sigma, `offset` rounds after onset."""
    row = onset_row(event) + offset
    if row >= event.config.rounds:
        return 0
    return int((np.abs(event.levels[row] - calm.levels[row]) > sigma(event)).sum())
