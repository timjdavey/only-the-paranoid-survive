"""The sweep cells: game-length, reading-roughness, up-and-down and bayesian-frontier.

See docs/specs/harness/pilot.md#engine-cells. A knob is a replace on the config in memory.
"""

from dataclasses import replace
from pathlib import Path

from paranoid.baselines import BAYESIAN_RULES, HAZARDS, POLICIES, Bayesian, HedgeRule, ScoutRule
from paranoid.baselines import complacent, discerning, hedge_rule, uniform
from paranoid.engine import SCENARIOS, SwitchSpec, make_timeline, play

from .common import CellArgs, defaults, engine_seeds, last_end, move_round, onset, output, stayer, switch_kind, write_csv

ONE_EVENT = ("one_shock", "down_switch", "up_switch", "slow_drift")
TWO_EVENTS = ("shock_then_switch", "switch_then_shock", "up_switch_then_down_switch")
BOTH_WAYS = "up_switch_then_down_switch"  # the one scenario the Stayer plays


def game_length(args: CellArgs) -> list[Path]:
    columns = (
        "rounds", "onset_low", "onset_high", "gap_low", "gap_high", "scenario", "seed", "onset_1", "onset_2",
        "last_end", "baseline", "output", "output_window_1", "output_window_2", "move_round",
    )  # fmt: skip
    gaps = ((6, 8), (8, 12), (12, 16))

    def settings():
        for rounds in (30, 40, 60):
            for start in ((8, 12), (12, 20), (16, 24)):
                for name in ONE_EVENT:
                    yield rounds, start, None, name
                for name in TWO_EVENTS:
                    for gap in gaps:
                        yield rounds, start, gap, name

    def rows():
        for rounds, start, gap, name in settings():
            config = SCENARIOS[name]
            events = config.events if gap is None else tuple(replace(spec, gap=gap) for spec in config.events)
            config = replace(config, rounds=rounds, onset=start, events=events)
            players = defaults() + ([("stayer", stayer)] if name == BOTH_WAYS else [])
            for seed in engine_seeds(args):
                t = make_timeline(config, seed)
                onsets = [event.onset for event in t.events] + [None]
                gap_cells = (None, None) if gap is None else gap
                for baseline, policy in players:
                    record = play(policy, t)
                    windows = [window(record, onsets, k) for k in (0, 1)]
                    yield (
                        rounds, *start, *gap_cells, name, seed, onsets[0], onsets[1], last_end(t), baseline,
                        output(record), *windows, move_round(record, t.leader),
                    )  # fmt: skip

    return write_csv(args, "game-length", columns, rows)


def window(record, onsets: list[int | None], k: int) -> float | None:
    """Output from event k's onset to the round before the next one's, or to the end. Empty with no event k."""
    if k >= len(onsets) - 1 or onsets[k] is None:
        return None
    end = onsets[k + 1] - 1 if onsets[k + 1] is not None else len(record)
    return output(record, slice(onsets[k] - 1, end))


def reading_roughness(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "baseline", "parameter", "scout_rounds", "seed", "output", "move_round")
    hedges = [("hedge_rule", e, k, HedgeRule(explore=e, scout_rounds=k)) for e in (1, 2, 5) for k in (1, 2, 3)]
    scouts = [("scout_rule", s, None, ScoutRule(s=s)) for s in (1, 2, 5)]
    plan = [("down_switch", hedges), ("no_change", hedges), ("up_switch", scouts), ("no_change", scouts)]

    def rows():
        for setting in (4.0, 8.0, 16.0):
            for name, players in plan:
                config = replace(SCENARIOS[name], read_noise_k=setting)
                for seed in engine_seeds(args):
                    t = make_timeline(config, seed)
                    for baseline, parameter, scout_rounds, policy in players:
                        record = play(policy, t)
                        yield setting, name, baseline, parameter, scout_rounds, seed, output(record), move_round(record, t.leader)

    return write_csv(args, "reading-roughness", columns, rows)


def up_and_down(args: CellArgs) -> list[Path]:
    columns = ("setting", "scenario", "kind", "baseline", "parameter", "seed", "onset", "output", "move_round")
    players = [
        ("uniform", None, uniform), ("discerning", None, discerning), ("complacent", None, complacent),
        ("hedge_rule", None, hedge_rule), *(("scout_rule", s, ScoutRule(s=s)) for s in (1, 2, 5)),
    ]  # fmt: skip

    def rows():
        for rise in ((1.0, 3.0), (2.0, 4.0), (3.0, 5.0)):
            for name in ("down_switch", "up_switch", "no_change"):
                config = SCENARIOS[name]
                events = tuple(replace(e, rise_sigmas=rise) if isinstance(e, SwitchSpec) else e for e in config.events)
                config = replace(config, events=events)
                for seed in engine_seeds(args):
                    t = make_timeline(config, seed)
                    for baseline, parameter, policy in players:
                        record = play(policy, t)
                        yield (
                            rise[0], name, switch_kind(t), baseline, parameter, seed, onset(t), output(record),
                            move_round(record, t.leader),
                        )  # fmt: skip

    return write_csv(args, "up-and-down", columns, rows)


def bayesian_frontier(args: CellArgs) -> list[Path]:
    columns = ("scenario", "baseline", "hazard", "rule", "seed", "output")
    fixed = [(name, None, None, POLICIES[name]()) for name in ("uniform", "discerning", "complacent", "hedge_rule", "scout_rule")]
    frontier = [("bayesian", h, r, Bayesian(hazard=h, rule=r)) for h in HAZARDS for r in BAYESIAN_RULES]

    def rows():
        for name, config in SCENARIOS.items():
            for seed in engine_seeds(args):
                t = make_timeline(config, seed)
                for baseline, hazard, rule, policy in frontier + fixed:
                    yield name, baseline, hazard, rule, seed, output(play(policy, t))

    return write_csv(args, "bayesian-frontier", columns, rows)
