"""The weather cells: streaks, tell, luck, timeline-sanity and noise-grid. See docs/specs/harness/pilot.md#engine-cells.

Each cell is its blocks, one per setting, and a module level function from a block and a seed to that seed's rows,
which `seed_rows` may hand to another process.
"""

from dataclasses import replace
from pathlib import Path

import numpy as np

from paranoid.baselines import HedgeRule, ScoutRule, complacent, discerning, perfect, uniform
from paranoid.engine import SCENARIOS, Game, Record, Timeline, make_timeline, play

from ..config import scenario_config
from ..seeds import load_grid
from .common import CellArgs, Rows, defaults, engine_seeds, first_switch, largest, move_round, onset, output, seed_rows, write_csv


def longest_run(flags: list[bool]) -> int:
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


def before_onset(timeline: Timeline) -> range:
    """Rounds before the first onset, or every round with no event, from 1."""
    start = onset(timeline)
    return range(1, (start if start is not None else timeline.config.rounds + 1))


def streaks(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "seed", "onset", "leader_below_streak", "rounds_to_separate", "field_beats_leader_streak")

    blocks = [
        (setting, name, replace(SCENARIOS[name], persistence=setting))
        for setting in (0.0, 0.5, 0.8, 0.9)
        for name in ("no_change", "down_switch")
    ]
    return write_csv(args, "streaks", columns, lambda: seed_rows(args, streak_rows, blocks))


def streak_rows(block, seed: int) -> Rows:
    setting, name, config = block
    t = make_timeline(config, seed)
    levels, leader, runner = t.levels, t.leader, t.runner_up
    calm = before_onset(t)
    below = [levels[r - 1, leader] < levels[r - 1, runner] for r in calm]
    record = play(ScoutRule(s=1, n=config.rounds), t)
    field = [c for c in range(config.channels) if c not in (leader, t.hedge)]
    beats = [longest_run([record.rows[r - 1].readings[c] > record.rows[r - 1].readings[leader] for r in calm]) for c in field]
    return [(setting, name, seed, onset(t), longest_run(below), separate(t), max(beats, default=0))]


def separate(t: Timeline) -> int | None:
    """Rounds from onset to the first round from which the leader stays below the runner-up. Empty without."""
    start = onset(t)
    if start is None:
        return None
    below = t.levels[:, t.leader] < t.levels[:, t.runner_up]
    if not below[-1]:
        return None
    first = len(below)
    while first > 0 and below[first - 1]:
        first -= 1
    return max(first + 1, start) - start


def tell(args: CellArgs) -> list[Path]:
    columns = (
        "factor_scale", "loading_low", "window", "fall_points", "tell_points", "scenario", "seed", "onset",
        "depth_capped", "hedge_rise", "held", "move_round", "fall_rounds", "tell_rounds", "field_together_rounds",
    )  # fmt: skip
    scenarios = ("one_shock", "down_switch", "no_change")
    first = [(scale, loading, HedgeRule(), False) for scale in (1.5, 3.0, 4.5, 6.0) for loading in ((0.3, 1.0), (0.5, 1.0))]
    thresholds = [
        (3.0, (0.3, 1.0), HedgeRule(window=w, fall_points=f, tell_points=p), True)
        for w in (2, 3, 4)
        for f in (4.0, 8.0, 12.0)
        for p in (2.0, 4.0, 6.0)
    ]

    blocks = [
        (scale, loading, rule, named, name, replace(SCENARIOS[name], factor_scale=scale, loading=loading))
        for scale, loading, rule, named in first + thresholds
        for name in scenarios
    ]
    return write_csv(args, "tell", columns, lambda: seed_rows(args, tell_rows, blocks))


def tell_rows(block, seed: int) -> Rows:
    scale, loading, rule, named, name, config = block
    t = make_timeline(config, seed)
    record = play(rule, t)
    knobs = (rule.window, rule.fall_points, rule.tell_points) if named else (None, None, None)
    return [(
        scale, loading[0], *knobs, name, seed, onset(t), depth_capped(t), hedge_rise(t, record, rule),
        int(largest(record.rows[-1].bets) == t.leader),
        move_round(record, t.leader), *fall_and_tell(t, record, rule), field_together(t),
    )]  # fmt: skip


def depth_capped(t: Timeline) -> int | None:
    shock = next((event for event in t.events if event.shape == "shock"), None)
    if shock is None:
        return None
    return int(shock.numbers["depth"] < shock.numbers["depth_drawn"])


def hedge_rise(t: Timeline, record: Record, rule: HedgeRule) -> float | None:
    """The hedge rule's mean hedge reading over `window` rounds from onset, minus its mean before onset."""
    start = onset(t)
    if start is None:
        return None
    readings = dict(record.readings_of(t.hedge))
    after = [readings[r] for r in range(start, start + rule.window) if r in readings]
    before = [readings[r] for r in range(1, start) if r in readings]
    if not after or not before:
        return None
    return float(np.mean(after) - np.mean(before))


def fall_and_tell(t: Timeline, record: Record, rule: HedgeRule) -> tuple[int | None, int | None]:
    """Rounds from onset on which the rule's fall test fired, and of those the ones its tell test stopped.

    Replays the rule's own steps on its record. The test runs only while it holds, so scout rounds are not counted.
    A rule whose tell can never fire gives the fall test alone.
    """
    start = onset(t)
    if start is None:
        return None, None
    blind = replace(rule, tell_points=1e300)
    readings = [dict(record.readings_of(c)) for c in range(t.config.channels)]
    state = rule.state(Game(t).view(False))  # the hold on round 1
    falls = tells = 0
    for r in range(2, len(record) + 1):
        if state.scout_start is None and r >= start:
            pick, hedge = readings[state.pick], readings[t.hedge]
            if blind.falls_without_tell(state, r, pick, hedge):
                falls += 1
                tells += not rule.falls_without_tell(state, r, pick, hedge)
        state = rule.step(state, r, readings, t.hedge)
    return falls, tells


def field_together(t: Timeline) -> int:
    """Rounds in which every channel but the hedge moved by more than own_scale, all the same way, on levels."""
    others = [c for c in range(t.config.channels) if c != t.hedge]
    steps = np.diff(t.levels[:, others], axis=0)
    big = np.abs(steps) > t.config.own_scale
    same = (steps > 0).all(axis=1) | (steps < 0).all(axis=1)
    return int((big.all(axis=1) & same).sum())


def luck(args: CellArgs) -> list[Path]:
    def blocks():
        return [(setting, scenario_config("down_switch", own_scale=setting)) for setting in load_grid().own_scale]

    columns = ("setting", "seed", "perfect", "discerning", "uniform")
    return write_csv(args, "luck", columns, lambda: seed_rows(args, luck_rows, blocks()))


def luck_rows(block, seed: int) -> Rows:
    setting, config = block
    t = make_timeline(config, seed)
    return [(setting, seed, *(output(play(policy, t)) for policy in (perfect, discerning, uniform)))]


def timeline_sanity(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "seed", "below_zero_rounds", "below_zero_readings", "discerning", "complacent")
    grid = load_grid().own_scale

    blocks = [(setting, name, scenario_config(name, own_scale=setting)) for setting in grid for name in SCENARIOS]

    def sparklines():
        setting = SCENARIOS["no_change"].own_scale
        for name in SCENARIOS:
            config = scenario_config(name, own_scale=setting) if setting in grid else SCENARIOS[name]
            leaders = np.array([(t := make_timeline(config, s)).levels[:, t.leader] for s in engine_seeds(args)])
            for r in range(config.rounds):
                column = leaders[:, r]
                yield name, r + 1, float(np.median(column)), *(float(np.percentile(column, p)) for p in (10, 90))

    paths = write_csv(args, "timeline-sanity", columns, lambda: seed_rows(args, sanity_rows, blocks))
    return paths + write_csv(args, "timeline-sanity-sparklines", ("scenario", "round", "median", "p10", "p90"), sparklines)


def sanity_rows(block, seed: int) -> Rows:
    setting, name, config = block
    t = make_timeline(config, seed)
    scout = play(ScoutRule(s=1, n=config.rounds), t)
    readings = [r for row in scout.rows for r in row.readings if r is not None and r < 0]
    below = int((t.levels < 0).sum())
    return [(setting, name, seed, below, len(readings), output(play(discerning, t)), output(play(complacent, t)))]


def noise_grid(args: CellArgs) -> list[Path]:
    players = defaults()

    def blocks():
        return [
            (setting, name, scenario_config(name, own_scale=setting), players)
            for setting in load_grid().own_scale
            for name in ("one_shock", "down_switch", "up_switch")
        ]

    columns = ("setting", "scenario", "baseline", "seed", "size", "output")
    return write_csv(args, "noise-grid", columns, lambda: seed_rows(args, noise_rows, blocks()))


def noise_rows(block, seed: int) -> Rows:
    setting, name, config, players = block
    t = make_timeline(config, seed)
    switch = first_switch(t)
    size = None if switch is None else switch.numbers["size"]
    return [(setting, name, baseline, seed, size, output(play(policy, t))) for baseline, policy in players]
