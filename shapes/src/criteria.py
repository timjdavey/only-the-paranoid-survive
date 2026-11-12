"""The test: one function per purpose, each over the public seeds. See shapes/README.md.

Every measure of an event reads twin timelines: one seed's event timeline minus its No change timeline is the
event's effect alone, with the weather taken out. Levels are read with no read noise.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

from paranoid.engine import SCENARIOS, Timeline, make_timeline

WINDOW = 8  # rounds from onset in which holding is a real question
SEEN = 3  # rounds from onset an agent has to tell a switch from a shock


@dataclass(frozen=True)
class Row:
    measure: str
    value: str


@dataclass(frozen=True)
class Section:
    purpose: str
    rows: tuple[Row, ...]


class Twins:
    """Every timeline the criteria read, made once per seed."""

    NAMES = ("no_change", "one_shock", "down_switch", "up_switch", "slow_drift")

    def __init__(self, seeds: Sequence[int]):
        self.seeds = list(seeds)
        self.by_name = {name: [make_timeline(SCENARIOS[name], s) for s in self.seeds] for name in self.NAMES}

    def pairs(self, name: str):
        return zip(self.by_name["no_change"], self.by_name[name])


# --- helpers ---------------------------------------------------------------


def others_max(levels: np.ndarray, channel: int) -> np.ndarray:
    return np.delete(levels, channel, axis=1).max(axis=1)


def longest_run(flags: np.ndarray) -> int:
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


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


def swaps(before: np.ndarray, after: np.ndarray) -> int:
    """Pairs of channels whose order flips."""
    above_before = before[:, None] > before[None, :]
    above_after = after[:, None] > after[None, :]
    return int(np.triu(above_before != above_after, k=1).sum())


def sigma(timeline: Timeline) -> float:
    return timeline.config.own_scale


def onset_row(timeline: Timeline) -> int:
    return timeline.events[0].onset - 1


def switch_kind(timeline: Timeline) -> str:
    numbers = timeline.events[0].numbers
    if numbers["kind"] == "rise" and numbers["short"]:
        return "rise_short"
    return str(numbers["kind"])


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


def first_rounds(timeline: Timeline) -> np.ndarray:
    """Each channel's level in the SEEN rounds from onset, less its mean over the three rounds before."""
    row = onset_row(timeline)
    before = timeline.levels[row - 3 : row].mean(axis=0)
    return timeline.levels[row : row + SEEN] - before


def leader_seat(timeline: Timeline) -> np.ndarray:
    return first_rounds(timeline)[:, timeline.leader]


def field_view(timeline: Timeline) -> np.ndarray:
    """The leader's move, and the median and largest move of the other nine, in each round."""
    moves = first_rounds(timeline)
    rest = np.delete(moves, timeline.leader, axis=1)
    return np.concatenate([moves[:, timeline.leader], np.median(rest, axis=1), rest.max(axis=1)])


def moved_at(calm: Timeline, event: Timeline, offset: int) -> int:
    """Channels the event alone moves by more than one sigma, `offset` rounds after onset."""
    row = onset_row(event) + offset
    if row >= event.config.rounds:
        return 0
    return int((np.abs(event.levels[row] - calm.levels[row]) > sigma(event)).sum())


# --- one function per purpose ----------------------------------------------


def weather_moves_the_leader(twins: Twins) -> Section:
    sds, gaps, off_rounds, off_any, off_three, below_three = [], [], [], [], [], []
    for calm in twins.by_name["no_change"]:
        levels, leader = calm.levels, calm.leader
        off = levels[:, leader] < others_max(levels, leader)
        below = levels[:, leader] < levels[:, calm.runner_up]
        sds.append(levels[:, leader].std(ddof=1))
        gaps.append(calm.base[0, leader] - calm.base[0, calm.runner_up])
        off_rounds.append(off.mean())
        off_any.append(off.any())
        off_three.append(longest_run(off) >= 3)
        below_three.append(longest_run(below) >= 3)
    rows = (
        Row("Leader's SD over the run, in points", spread(sds)),
        Row("Leader's gap to the runner-up at round 1, in points", spread(gaps)),
        Row("Share of rounds the leader is off the top spot", share(off_rounds)),
        Row("Share of seeds where the leader is off the top spot at all", share(off_any)),
        Row("Share of seeds where it is off for three rounds running", share(off_three)),
        Row("Share of seeds where it is below the runner-up for three rounds running", share(below_three)),
    )
    return Section("Weather moves the leader", rows)


def shock_numbers(calm: Timeline, shocked: Timeline) -> dict:
    """The shock alone on one seed: its impulse into the shared factor and where it bottoms out."""
    impulse = shocked.factor - calm.factor
    trough = int(np.argmin(impulse))
    effect = shocked.levels - calm.levels
    leader = shocked.leader
    weather_falls = -np.diff(calm.levels[:, leader])
    return {
        "trough": trough,
        "impulse": impulse,
        "effect": effect[trough],
        "leader_fall": -effect[trough, leader],
        "shock_round_fall": float((-np.diff(effect[:, leader])).max()),
        "worst_weather_fall": float(weather_falls.max()),
    }


def shock_is_a_storm(twins: Twins) -> Section:
    ratios, smaller, round_ratios = [], [], []
    for calm, shocked in twins.pairs("one_shock"):
        n = shock_numbers(calm, shocked)
        ratios.append(n["leader_fall"] / n["worst_weather_fall"])
        smaller.append(n["leader_fall"] < n["worst_weather_fall"])
        round_ratios.append(n["shock_round_fall"] / n["worst_weather_fall"])
    rows = (
        Row("Leader's fall at the trough over the worst one round fall weather gives it", spread(ratios, 2)),
        Row("The shock's largest one round fall over that same weather fall", spread(round_ratios, 2)),
        Row("Share of shocks whose whole fall is smaller than that weather fall", share(smaller)),
    )
    return Section("A shock is a storm", rows)


def shock_falls_the_leader(twins: Twins) -> Section:
    falls, depths = [], []
    for calm, shocked in twins.pairs("one_shock"):
        falls.append(shock_numbers(calm, shocked)["leader_fall"])
        depths.append(shocked.events[0].numbers["depth"])
    rows = (
        Row("Leader's fall at the trough, in points", spread(falls)),
        Row("The shock's depth after the cap, in points", spread(depths)),
    )
    return Section("A shock falls the leader", rows)


def shock_shakes_up_the_system(twins: Twins) -> Section:
    fall_1, rise_1, fall_3, rise_3, any_swap, pair_swaps, hedge_climbs, overtaken = [], [], [], [], [], [], [], []
    for calm, shocked in twins.pairs("one_shock"):
        n = shock_numbers(calm, shocked)
        step = sigma(shocked)
        effect = n["effect"]
        fall_1.append((effect < -step).sum())
        rise_1.append((effect > step).sum())
        fall_3.append((effect < -3 * step).sum())
        rise_3.append((effect > 3 * step).sum())
        row, hedge = n["trough"], shocked.hedge
        before = shocked.base[onset_row(shocked) - 1]
        at_trough = shocked.base[row] + shocked.loadings[row] * n["impulse"][row]
        flips = swaps(np.delete(before, hedge), np.delete(at_trough, hedge))
        any_swap.append(flips > 0)
        pair_swaps.append(flips)
        hedge_climbs.append(int((before > before[hedge]).sum() - (at_trough > at_trough[hedge]).sum()))
        overtaken.append(int(np.argmax(at_trough)) != shocked.leader)
    rows = (
        Row("Channels that fall by more than one sigma at the trough", counts(fall_1)),
        Row("Channels that rise by more than one sigma", counts(rise_1)),
        Row("Channels that fall by more than three sigmas", counts(fall_3)),
        Row("Channels that rise by more than three sigmas", counts(rise_3)),
        Row("Places the hedge climbs at the trough, before weather", counts(hedge_climbs)),
        Row("Pairs of channels, hedge aside, that swap places at the trough, of 36", counts(pair_swaps)),
        Row("Share of shocks where any such pair swaps", share(any_swap)),
        Row("Share of shocks where the leader is overtaken at the trough, before weather", share(overtaken)),
    )
    return Section("A shock shakes up the system", rows)


def give_up(levels: np.ndarray, leader: int, start: int) -> tuple[float, bool]:
    """Points a round a holder of the leader gives up to the window's best channel, and whether that is not the leader."""
    window = levels[start : start + WINDOW]
    totals = window.sum(axis=0)
    best = int(np.argmax(totals))
    return float((totals[best] - totals[leader]) / len(window)), best != leader


def shock_makes_holding_a_question(twins: Twins) -> Section:
    off_shock, off_calm, cost_shock, cost_calm, beaten_shock, beaten_calm = [], [], [], [], [], []
    for calm, shocked in twins.pairs("one_shock"):
        start, leader = onset_row(shocked), shocked.leader
        for timeline, off, cost, beaten in (
            (shocked, off_shock, cost_shock, beaten_shock),
            (calm, off_calm, cost_calm, beaten_calm),
        ):
            window = timeline.levels[start : start + WINDOW]
            off.append((window[:, leader] < others_max(window, leader)).sum())
            points, lost = give_up(timeline.levels, leader, start)
            cost.append(points)
            beaten.append(lost)
    rows = (
        Row(f"Rounds the leader is off the top spot in the {WINDOW} from onset, One shock", counts(off_shock)),
        Row("The same rounds on the No change twin", counts(off_calm)),
        Row("Points a round a holder gives up to the window's best channel, One shock", counts(cost_shock)),
        Row("The same on the No change twin", counts(cost_calm)),
        Row("Share of seeds where another channel beats the leader over the window, One shock", share(beaten_shock)),
        Row("The same on the No change twin", share(beaten_calm)),
    )
    return Section("A shock makes holding a real question", rows)


def switch_looks_like_a_shock(twins: Twins) -> Section:
    rows = []
    for name, words in (
        ("one_shock", "One shock"),
        ("down_switch", "Down switch"),
        ("up_switch", "Up switch"),
        ("slow_drift", "Slow drift"),
    ):
        at_onset = [moved_at(calm, event, 0) for calm, event in twins.pairs(name)]
        two_on = [moved_at(calm, event, 2) for calm, event in twins.pairs(name)]
        rows.append(Row(f"{words}: channels moved by more than one sigma at onset", counts(at_onset)))
        rows.append(Row(f"{words}: the same, two rounds on", counts(two_on)))
    shocks, switches = twins.by_name["one_shock"], twins.by_name["down_switch"]
    labels = np.array([0] * len(shocks) + [1] * len(switches))
    train = np.array([i % 2 == 0 for i in range(len(shocks))] * 2)
    for view, words in ((leader_seat, "the leader's seat"), (field_view, "the field")):
        features = np.array([view(t) for t in [*shocks, *switches]])
        rows.append(
            Row(
                f"How well {SEEN} rounds of levels tell Down switch from One shock, from {words} (AUC)",
                f"{fisher_auc(features, labels, train):.2f}",
            )
        )
    return Section("A switch looks like a shock", tuple(rows))


def end_of_change(timeline: Timeline) -> int:
    """The row at which the event has finished moving the climate."""
    event = timeline.events[0]
    length = event.numbers["length"] if event.shape == "drift" else event.numbers["ramp"]
    return min(event.onset - 1 + length - 1, timeline.config.rounds - 1)


def new_state(timelines: Sequence[Timeline]) -> tuple[str, str, str, int]:
    rounds = timelines[0].config.rounds
    changed, stays, runner_up = [], [], []
    for t in timelines:
        first, last = t.climate_leader(1), t.climate_leader(rounds)
        changed.append(last != first)
        after = range(end_of_change(t) + 1, rounds + 1)
        stays.append(all(t.climate_leader(r) != first for r in after))
        runner_up.append(last == t.runner_up)
    return share(changed), share(stays), share(runner_up), len(timelines)


def switch_leaves_a_new_state(twins: Twins) -> Section:
    groups: dict[str, list[Timeline]] = {}
    for name in ("down_switch", "up_switch"):
        for t in twins.by_name[name]:
            groups.setdefault(switch_kind(t), []).append(t)
    groups["drift"] = list(twins.by_name["slow_drift"])
    rows = []
    for kind in ("fall", "fall_and_rise", "rise", "rise_short", "drift"):
        if kind not in groups:
            continue
        changed, stays, runner_up, count = new_state(groups[kind])
        rows.append(
            Row(
                f"`{kind}` ({count} seeds): climate leader changed by the last round, "
                "stayed changed after the ramp, and is the runner-up",
                f"{changed}, {stays}, {runner_up}",
            )
        )
    return Section("A switch leaves a new state", tuple(rows))


def largest_base_fall(timeline: Timeline) -> float:
    return float((-np.diff(timeline.base[:, timeline.leader])).max())


def drift(twins: Twins) -> Section:
    drift_falls = [largest_base_fall(t) for t in twins.by_name["slow_drift"]]
    totals = [t.events[0].numbers["fall"] for t in twins.by_name["slow_drift"]]
    switch_falls = [largest_base_fall(t) for t in twins.by_name["down_switch"]]
    weather = [float((-np.diff(t.levels[:, t.leader])).max()) for t in twins.by_name["no_change"]]
    rows = (
        Row("Slow drift: the leader's whole fall in base level, in points", spread(totals)),
        Row("Slow drift: its largest one round fall in base level", spread(drift_falls)),
        Row("Down switch: the same largest one round fall", spread(switch_falls)),
        Row("No change: the leader's worst one round fall in level, from weather", spread(weather)),
    )
    return Section("A drift", rows)


PURPOSES: tuple[Callable[[Twins], Section], ...] = (
    weather_moves_the_leader,
    shock_is_a_storm,
    shock_falls_the_leader,
    shock_shakes_up_the_system,
    shock_makes_holding_a_question,
    switch_looks_like_a_shock,
    switch_leaves_a_new_state,
    drift,
)


def criteria(seeds: Sequence[int]) -> list[Section]:
    twins = Twins(seeds)
    return [purpose(twins) for purpose in PURPOSES]


def markdown(sections: Sequence[Section], seeds: Sequence[int]) -> str:
    config = SCENARIOS["no_change"]
    lines = [
        "# Shape criteria",
        "",
        "Written by `shapes/src/make.py`. Do not edit by hand. What each measure is for is in [the README](README.md#the-test).",
        "",
        f"- **Seeds.** The first {len(seeds)} public seeds, {seeds[0]} to {seeds[-1]}.",
        f"- **Levels, not readings.** No read noise. One sigma is {config.own_scale:g} points.",
        "- **An event's effect** is its timeline minus the No change twin on the same seed.",
        "- **A size** in points is the median, then the 10th to 90th percentile in brackets.",
        "- **A count** of rounds or channels, and the points a holder gives up, is the mean, then the 10th to 90th percentile.",
        "",
    ]
    for section in sections:
        lines += [f"## {section.purpose}", "", "| Measure | Value |", "|---|---|"]
        lines += [f"| {row.measure} | {row.value} |" for row in section.rows]
        lines.append("")
    return "\n".join(lines)
