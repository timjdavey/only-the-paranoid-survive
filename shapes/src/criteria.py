"""The test: one function per purpose, each run in both worlds. See shapes/README.md#the-test.

Each purpose gives the same rows in either world, so criteria.md sets them side by side. The tools are in measures.py.
"""

from collections.abc import Sequence

import numpy as np
from measures import (
    SEATS,
    SEEN,
    WINDOW,
    Row,
    Twins,
    before_weather,
    chase_against_hold,
    counts,
    features,
    first_change,
    longest_run,
    moved_at,
    moves,
    onset_row,
    others_max,
    pop_channel,
    readings,
    seat_bets,
    share,
    sigma,
    spread,
    storm_of,
    swaps,
    switch_kind,
    tell_apart,
    trough_row,
    worst_fall,
)

from paranoid.engine import Timeline


def weather(twins: Twins) -> list[Row]:
    sds, gaps, off_rounds, off_any, off_three, below_three, as_deep, chase = [], [], [], [], [], [], [], []
    k = twins.world["no_change"].read_noise_k
    for calm, shocked in twins.pairs("one_shock"):
        levels, leader = calm.levels, calm.leader
        off = levels[:, leader] < others_max(levels, leader)
        below = levels[:, leader] < levels[:, calm.runner_up]
        sds.append(levels[:, leader].std(ddof=1))
        gaps.append(calm.base[0, leader] - calm.base[0, calm.runner_up])
        off_rounds.append(off.mean())
        off_any.append(off.any())
        off_three.append(longest_run(off) >= 3)
        below_three.append(longest_run(below) >= 3)
        row = onset_row(shocked)
        storm_three = shocked.levels[row - 1, leader] - shocked.levels[row + 2, leader]
        as_deep.append(worst_fall(levels[:, leader], 3) >= storm_three)
        chase.append(chase_against_hold(calm, k))
    return [
        Row("Leader's SD over the run, in points", spread(sds)),
        Row("Leader's gap to the runner-up at round 1, in points", spread(gaps)),
        Row("Share of rounds the leader is off the top spot", share(off_rounds)),
        Row("Share of seeds where the leader is off the top spot at all", share(off_any)),
        Row("Share of seeds where it is off for three rounds running", share(off_three)),
        Row("Share of seeds where it is below the runner-up for three rounds running", share(below_three)),
        Row("Share of seeds where calm weather gives the leader a three round fall as deep as the storm's first three",
            share(as_deep)),
        Row("Points a round chasing last round's best reading earns over holding, one point looks, the world's k",
            spread(chase, 2)),
    ]  # fmt: skip


def shock(twins: Twins) -> list[Row]:
    m = {key: [] for key in ("ratio", "round", "smaller", "fall", "depth", "ahead", "beats", "leave", "to_pop")}
    shake = {key: [] for key in ("fall_1", "rise_1", "fall_3", "rise_3", "climbs", "pairs", "any", "overtaken")}
    hold = {key: [] for key in ("off_shock", "off_calm", "cost_shock", "cost_calm", "beaten_shock", "beaten_calm")}
    k = twins.world["one_shock"].read_noise_k
    for calm, shocked in twins.pairs("one_shock"):
        row, trough, leader, hedge = onset_row(shocked), trough_row(shocked), shocked.leader, shocked.hedge
        effect = shocked.levels - calm.levels
        weather_fall = float((-np.diff(calm.levels[:, leader])).max())
        leader_fall = -effect[trough, leader]
        m["ratio"].append(leader_fall / weather_fall)
        m["round"].append(float((-np.diff(effect[:, leader])).max()) / weather_fall)
        m["smaller"].append(leader_fall < weather_fall)
        m["fall"].append(leader_fall)
        m["depth"].append(shocked.events[0].numbers["depth"])
        calm_view = before_weather(calm, shocked)
        window = calm_view[row : row + WINDOW]
        ahead = window[:, [leader]] - np.delete(window, leader, axis=1)
        m["ahead"].append((ahead >= shocked.config.hedge_margin_points - 1e-9).all(axis=1).mean())
        seen = readings(shocked, seat_bets(shocked, 1), k)[row : row + WINDOW]
        m["beats"].append((others_max(seen, leader) > seen[:, leader]).mean())
        best = int(np.argmax(np.where(np.arange(shocked.config.channels) == leader, -np.inf, shocked.levels[trough])))
        after = shocked.levels[trough + 1 : trough + 1 + WINDOW]
        m["leave"].append(float((after[:, leader] - after[:, best]).mean()))
        m["to_pop"].append(best == pop_channel(shocked))
        at_trough, before = calm_view[trough], shocked.base[row - 1]
        step = sigma(shocked)
        shake["fall_1"].append((effect[trough] < -step).sum())
        shake["rise_1"].append((effect[trough] > step).sum())
        shake["fall_3"].append((effect[trough] < -3 * step).sum())
        shake["rise_3"].append((effect[trough] > 3 * step).sum())
        shake["climbs"].append(int((before > before[hedge]).sum() - (at_trough > at_trough[hedge]).sum()))
        flips = swaps(np.delete(before, hedge), np.delete(at_trough, hedge))
        shake["pairs"].append(flips)
        shake["any"].append(flips > 0)
        shake["overtaken"].append(int(np.argmax(at_trough)) != leader)
        for t, words in ((shocked, "shock"), (calm, "calm")):
            levels = t.levels[row : row + WINDOW]
            hold[f"off_{words}"].append((levels[:, leader] < others_max(levels, leader)).sum())
            totals = levels.sum(axis=0)
            hold[f"cost_{words}"].append(float((totals.max() - totals[leader]) / len(levels)))
            hold[f"beaten_{words}"].append(int(np.argmax(totals)) != leader)
    return [
        Row("Leader's fall at the trough over the worst one round fall weather gives it", spread(m["ratio"], 2)),
        Row("The shock's largest one round fall over that same weather fall", spread(m["round"], 2)),
        Row("Share of shocks whose whole fall is smaller than that weather fall", share(m["smaller"])),
        Row("Leader's fall at the trough, in points", spread(m["fall"])),
        Row("The shock's depth after the cap, in points", spread(m["depth"])),
        Row("Channels that fall by more than one sigma at the trough", counts(shake["fall_1"])),
        Row("Channels that rise by more than one sigma", counts(shake["rise_1"])),
        Row("Channels that fall by more than three sigmas", counts(shake["fall_3"])),
        Row("Channels that rise by more than three sigmas", counts(shake["rise_3"])),
        Row("Places the hedge climbs at the trough, before weather", counts(shake["climbs"])),
        Row("Pairs of channels, hedge aside, that swap places at the trough, of 36", counts(shake["pairs"])),
        Row("Share of shocks where any such pair swaps", share(shake["any"])),
        Row("Share of shocks where the leader is overtaken at the trough, before weather", share(shake["overtaken"])),
        Row(f"Share of the {WINDOW} storm rounds the leader is at least the margin ahead, before weather",
            share(m["ahead"])),
        Row(f"Share of the {WINDOW} storm rounds a one point reading of another channel beats the leader's, "
            "the world's k", share(m["beats"])),
        Row("Points a round leaving at the trough for the best other channel costs, over the next "
            f"{WINDOW} rounds", spread(m["leave"])),
        Row("Share of those moves that go to the pop", share(m["to_pop"])),
        Row(f"Rounds the leader is off the top spot in the {WINDOW} from onset, One shock", counts(hold["off_shock"])),
        Row("The same rounds on the No change twin", counts(hold["off_calm"])),
        Row("Points a round a holder gives up to the window's best channel, One shock", counts(hold["cost_shock"])),
        Row("The same on the No change twin", counts(hold["cost_calm"])),
        Row("Share of seeds where another channel beats the leader over the window, One shock",
            share(hold["beaten_shock"])),
        Row("The same on the No change twin", share(hold["beaten_calm"])),
    ]  # fmt: skip


def end_of_change(timeline: Timeline) -> int:
    """The row at which the event has finished moving the climate. A storm switch has no end, so its first change."""
    event = timeline.events[0]
    if event.shape == "drift":
        length = event.numbers["length"]
    elif storm_of(event) is not None:
        length = (first_change(timeline) or 0) + 1
    else:
        length = event.numbers["ramp"]
    return min(event.onset - 1 + length - 1, timeline.config.rounds - 1)


def new_state(timelines: Sequence[Timeline], kind: str) -> Row:
    rounds = timelines[0].config.rounds
    changed, stays, runner_up = [], [], []
    for t in timelines:
        first, last = t.climate_leader(1), t.climate_leader(rounds)
        changed.append(last != first)
        stays.append(all(t.climate_leader(r) != first for r in range(end_of_change(t) + 1, rounds + 1)))
        runner_up.append(last == t.runner_up)
    value = f"{share(changed)}, {share(stays)}, {share(runner_up)} of {len(timelines)}" if timelines else "none"
    return Row(f"`{kind}`: climate leader changed by the last round, stayed changed, and is the runner-up", value)


def by_kind(twins: Twins) -> dict[str, list[Timeline]]:
    groups: dict[str, list[Timeline]] = {}
    for name in ("down_switch", "up_switch"):
        for t in twins.by_name[name]:
            groups.setdefault(switch_kind(t), []).append(t)
    groups["drift"] = list(twins.by_name["slow_drift"])
    return groups


def switch(twins: Twins) -> list[Row]:
    rows, groups = [], by_kind(twins)
    for name, words in (("one_shock", "One shock"), ("down_switch", "Down switch"),
                        ("up_switch", "Up switch"), ("slow_drift", "Slow drift")):  # fmt: skip
        rows.append(Row(f"{words}: channels moved by more than one sigma at onset",
                        counts([moved_at(calm, event, 0) for calm, event in twins.pairs(name)])))  # fmt: skip
        rows.append(Row(f"{words}: the same, two rounds on",
                        counts([moved_at(calm, event, 2) for calm, event in twins.pairs(name)])))  # fmt: skip
    match, part, change, popped = [], [], [], []
    lose = {2: [], 4: [], 8: []}
    for shocked, switched in zip(twins.by_name["one_shock"], twins.by_name["down_switch"]):
        row, rounds = onset_row(switched), switched.config.rounds
        apart = np.abs(shocked.levels[row:] - switched.levels[row:])
        match.append(int(np.argmax(apart.max(axis=1) > 0)))
        part.append(int(np.argmax(apart.max(axis=1) > sigma(switched))))
        change.append(first_change(switched))
        popped.append(pop_channel(switched) is not None and switched.climate_leader(rounds) == pop_channel(switched))
        for after in lose:
            r = min(trough_row(switched) + after, rounds - 1)
            lose[after].append(float(switched.base[r].max() - switched.base[r, switched.leader]))
    rows += [
        Row("Rounds from onset One shock and Down switch match exactly on every channel", counts(match)),
        Row("Rounds from onset until they part by more than a sigma on some channel", counts(part)),
        Row("Rounds from onset until the climate leader changes, Down switch", counts([c for c in change if c is not None])),
        *[Row(f"Points a holder gives up {after} rounds after the trough, in base level", spread(lose[after]))
          for after in lose],
        Row("Share of Down switch seeds where the channel that popped is the climate leader at the last round",
            share(popped)),
        new_state(groups.get("fall", []), "fall"),
        new_state(groups.get("fall_and_rise", []), "fall_and_rise"),
    ]  # fmt: skip
    return rows


def largest_base_fall(timeline: Timeline, rounds: int = 1) -> float:
    return worst_fall(timeline.base[:, timeline.leader], rounds)


def drift(twins: Twins) -> list[Row]:
    drifts = twins.by_name["slow_drift"]
    weather_one = [worst_fall(t.levels[:, t.leader], 1) for t in twins.by_name["no_change"]]
    weather_three = [worst_fall(t.levels[:, t.leader], 3) for t in twins.by_name["no_change"]]
    between = []
    for t in drifts:
        row, cost = onset_row(t), first_change(t)
        fallen = t.base[row - 1, t.leader] - t.base[row:, t.leader]
        tell = int(np.argmax(fallen >= 2 * sigma(t)))
        if cost is not None and fallen.max() >= 2 * sigma(t):
            between.append(cost - tell)
    return [
        Row("Slow drift: the leader's whole fall in base level, in points", spread([t.events[0].numbers["fall"] for t in drifts])),
        Row("Slow drift: its largest one round fall in base level", spread([largest_base_fall(t) for t in drifts])),
        Row("Down switch: the same largest one round fall", spread([largest_base_fall(t) for t in twins.by_name["down_switch"]])),
        Row("No change: the leader's worst one round fall in level, from weather", spread(weather_one)),
        Row("Slow drift: its largest three round fall in base level", spread([largest_base_fall(t, 3) for t in drifts])),
        Row("No change: the leader's worst three round fall in level, from weather", spread(weather_three)),
        Row("Rounds from a two sigma fall in base level to the climate leader changing", counts(between)),
        new_state(by_kind(twins)["drift"], "drift"),
    ]  # fmt: skip


def rise(twins: Twins) -> list[Row]:
    groups, moved, short, worse = by_kind(twins), [], [], []
    for calm, up in twins.pairs("up_switch"):
        moved.append(not np.array_equal(calm.levels[:, calm.leader], up.levels[:, up.leader]))
        short.append(switch_kind(up) == "rise_short")
        start = onset_row(up) + up.events[0].numbers["ramp"]
        later = up.levels[start:]
        worse.append(later[:, up.sleeper].sum() < later[:, up.leader].sum())
    return [
        Row("Share of Up switch seeds where the leader's levels differ from No change", share(moved)),
        Row("Share of Up switch seeds that stop short", share(short)),
        Row("Share of Up switch seeds where moving to the sleeper when its ramp ends earns less than holding",
            share(worse)),
        new_state(groups.get("rise", []), "rise"),
        new_state(groups.get("rise_short", []), "rise_short"),
    ]  # fmt: skip


def looking(twins: Twins) -> list[Row]:
    shocks, switches = twins.by_name["one_shock"], twins.by_name["down_switch"]
    rows = []
    for field, words in ((False, "the leader's seat"), (True, "the field")):
        auc = tell_apart(shocks, switches, lambda t: features(moves(t.levels, t, SEEN), t.leader, field))
        rows.append(Row(f"How well {SEEN} rounds of levels tell Down switch from One shock, from {words} (AUC)",
                        f"{auc:.2f}"))  # fmt: skip
    for k in (8.0, 12.0):
        for seat, each in SEATS.items():
            for rounds in (1, 3, 6):

                def view(t, each=each, rounds=rounds, k=k):
                    seen = readings(t, seat_bets(t, each), k)
                    return features(moves(seen, t, rounds), t.leader, field=each > 0)

                auc = tell_apart(shocks, switches, view)
                rows.append(Row(f"Readings at k {k:g}, {seat}, after {rounds} round{'s' * (rounds > 1)} (AUC)",
                                f"{auc:.2f}"))  # fmt: skip
    return rows


PURPOSES = {"Weather": weather, "Shock": shock, "Switch": switch, "Drift": drift, "Rise": rise, "Looking": looking}


def criteria(worlds: dict, seeds: Sequence[int]) -> dict[str, list[tuple[str, str, str]]]:
    """Each purpose's rows as (measure, today, new)."""
    twins = {name: Twins(world, seeds) for name, world in worlds.items()}
    out = {}
    for purpose, measure in PURPOSES.items():
        today, new = measure(twins["today"]), measure(twins["new"])
        assert [r.measure for r in today] == [r.measure for r in new], purpose
        out[purpose] = [(a.measure, a.value, b.value) for a, b in zip(today, new)]
    return out
