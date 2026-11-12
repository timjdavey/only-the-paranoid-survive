"""The sweep cells: game-length, reading-roughness, up-and-down and bayesian-frontier.

See docs/specs/harness/pilot.md#engine-cells. A knob is a replace on the config in memory.
Each cell is its blocks and a module level function from a block and a seed to rows, as in weather.py.
"""

from dataclasses import replace
from pathlib import Path

from paranoid.baselines import POLICIES, Bayesian, HedgeRule, ScoutRule
from paranoid.baselines import complacent, discerning, hedge_rule, uniform
from paranoid.engine import SCENARIOS, SwitchSpec, make_timeline, play

from .common import CellArgs, Rows, defaults, last_end, move_round, onset, output, seed_rows, stayer, switch_kind, write_csv

ONE_EVENT = ("one_shock", "down_switch", "up_switch", "slow_drift")
TWO_EVENTS = ("shock_then_switch", "switch_then_shock", "up_switch_then_down_switch")
BOTH_WAYS = "up_switch_then_down_switch"  # the one scenario the Stayer plays
FRONTIER_PLAYERS = ((0.005, "odds"), (0.025, "odds"), (0.1, "odds"))  # hazard and rule: the ends of HAZARDS and the default
FRONTIER_SEEDS = 10  # a coarse read, so a knob move reruns the frontier in seconds
STREAKS = (3, 4, 5)  # the Scout rule's `n` that up-and-down plays at `s` of 1, the default among them once


def game_length(args: CellArgs) -> list[Path]:
    columns = (
        "rounds", "onset_low", "onset_high", "gap_low", "gap_high", "scenario", "seed", "onset_1", "onset_2",
        "last_end", "baseline", "output", "output_window_1", "output_window_2", "clear_round_1", "clear_round_2",
        "move_round",
    )  # fmt: skip
    gaps = ((6, 8), (8, 12), (12, 16))

    def settings():
        for rounds in (30, 40, 60):
            for start in ((6, 10), (8, 12), (12, 20)):
                for name in ONE_EVENT:
                    yield rounds, start, None, name
                for name in TWO_EVENTS:
                    for gap in gaps:
                        yield rounds, start, gap, name

    def blocks():
        for rounds, start, gap, name in settings():
            config = SCENARIOS[name]
            events = config.events if gap is None else tuple(replace(spec, gap=gap) for spec in config.events)
            config = replace(config, rounds=rounds, onset=start, events=events)
            players = defaults() + ([("stayer", stayer)] if name == BOTH_WAYS else [])
            yield rounds, start, gap, name, config, players

    return write_csv(args, "game-length", columns, lambda: seed_rows(args, length_rows, blocks()))


def length_rows(block, seed: int) -> Rows:
    rounds, start, gap, name, config, players = block
    t = make_timeline(config, seed)
    onsets = [event.onset for event in t.events] + [None]
    gap_cells = (None, None) if gap is None else gap
    records = {baseline: play(policy, t) for baseline, policy in players}
    rows = []
    for baseline, record in records.items():
        windows = [window(record, onsets, k) for k in (0, 1)]
        clear = [None, None]
        if baseline == "discerning":
            clear = [clear_round(record, records["complacent"], onsets, k) for k in (0, 1)]
        rows.append((
            rounds, *start, *gap_cells, name, seed, onsets[0], onsets[1], last_end(t), baseline,
            output(record), *windows, *clear, move_round(record, t.leader),
        ))  # fmt: skip
    return rows


def window(record, onsets: list[int | None], k: int) -> float | None:
    """Output from event k's onset to the round before the next one's, or to the end. Empty with no event k."""
    rounds = window_rounds(record, onsets, k)
    return None if rounds is None else output(record, slice(rounds.start - 1, rounds.stop - 1))


def window_rounds(record, onsets: list[int | None], k: int) -> range | None:
    """Event k's window, from its onset to the round before the next one's, or to the end. An onset may pass the end."""
    if k >= len(onsets) - 1 or onsets[k] is None:
        return None
    end = len(record) + 1
    return range(min(onsets[k], end), min(onsets[k + 1] or end, end))


def clear_round(ahead, behind, onsets: list[int | None], k: int) -> int | None:
    """The first round of window k from which `ahead`'s output since onset stays above `behind`'s. 0 if never."""
    rounds = window_rounds(ahead, onsets, k)
    if rounds is None:
        return None
    lead, clear = 0.0, 0
    for r in rounds:
        lead += ahead.rows[r - 1].output - behind.rows[r - 1].output
        if lead <= 0:
            clear = 0
        elif clear == 0:
            clear = r
    return clear


def reading_roughness(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "baseline", "parameter", "scout_rounds", "seed", "output", "move_round")
    hedges = [("hedge_rule", e, k, HedgeRule(explore=e, scout_rounds=k)) for e in (1, 2, 5) for k in (1, 2, 3)]
    scouts = [("scout_rule", s, None, ScoutRule(s=s)) for s in (1, 2, 5)]
    base = [("complacent", None, None, complacent)]  # never explores, so the explore cost's base
    plan = [("down_switch", base + hedges), ("no_change", base + hedges + scouts), ("up_switch", base + scouts)]

    blocks = [
        (setting, name, replace(SCENARIOS[name], read_noise_k=setting), players)
        for setting in (4.0, 8.0, 16.0)
        for name, players in plan
    ]
    return write_csv(args, "reading-roughness", columns, lambda: seed_rows(args, roughness_rows, blocks))


def roughness_rows(block, seed: int) -> Rows:
    setting, name, config, players = block
    t = make_timeline(config, seed)
    rows = []
    for baseline, parameter, scout_rounds, policy in players:
        record = play(policy, t)
        rows.append((setting, name, baseline, parameter, scout_rounds, seed, output(record), move_round(record, t.leader)))
    return rows


def up_and_down(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "kind", "baseline", "parameter", "streak", "seed", "onset", "output", "move_round")
    scouts = [ScoutRule(s=s) for s in (1, 2, 5)] + [ScoutRule(n=n) for n in STREAKS if n != ScoutRule().n]
    players = [
        ("uniform", None, None, uniform), ("discerning", None, None, discerning), ("complacent", None, None, complacent),
        ("hedge_rule", None, None, hedge_rule), *(("scout_rule", rule.s, rule.n, rule) for rule in scouts),
    ]  # fmt: skip

    def blocks():
        for rise in ((2.0, 5.0), (3.0, 6.0), (4.0, 7.0)):
            for name in ("down_switch", "up_switch", "no_change"):
                config = SCENARIOS[name]
                events = tuple(replace(e, rise_sigmas=rise) if isinstance(e, SwitchSpec) else e for e in config.events)
                yield rise[0], name, replace(config, events=events), players

    return write_csv(args, "up-and-down", columns, lambda: seed_rows(args, up_down_rows, blocks()))


def up_down_rows(block, seed: int) -> Rows:
    setting, name, config, players = block
    t = make_timeline(config, seed)
    kind, start, rows = switch_kind(t), onset(t), []
    for baseline, parameter, streak, policy in players:
        record = play(policy, t)
        rows.append((setting, name, kind, baseline, parameter, streak, seed, start, output(record), move_round(record, t.leader)))
    return rows


def bayesian_frontier(args: CellArgs) -> list[Path]:
    columns = ("scenario", "baseline", "hazard", "rule", "seed", "output")
    fixed = [(name, None, None, POLICIES[name]()) for name in ("uniform", "discerning", "complacent", "hedge_rule", "scout_rule")]
    frontier = [("bayesian", h, r, Bayesian(hazard=h, rule=r)) for h, r in FRONTIER_PLAYERS]
    blocks = [(name, config, frontier + fixed) for name, config in SCENARIOS.items()]
    few = replace(args, seeds=min(args.seeds, FRONTIER_SEEDS))
    return write_csv(args, "bayesian-frontier", columns, lambda: seed_rows(few, frontier_rows, blocks))


def frontier_rows(block, seed: int) -> Rows:
    name, config, players = block
    t = make_timeline(config, seed)
    return [(name, baseline, hazard, rule, seed, output(play(policy, t))) for baseline, hazard, rule, policy in players]
