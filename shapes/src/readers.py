"""The optional `--readers` step: two good readers play both worlds. See shapes/README.md#two-readers.

It plays the hedge rule and the Bayesian baseline at each of its hazards on No change, One shock and Down
switch, and scores each run as the harness does: output less the Uniform baseline's, over the Discerning
baseline's less the Uniform's. Both readers were built for today's shapes, so read this as a first look.
"""

from collections.abc import Mapping, Sequence

import numpy as np

from paranoid.baselines import HAZARDS, Bayesian, HedgeRule, complacent, discerning, uniform
from paranoid.engine import ScenarioConfig, make_timeline, play

NAMES = ("no_change", "one_shock", "down_switch")
READERS = {"hedge rule": HedgeRule(), **{f"Bayesian {h:g}": Bayesian(hazard=h) for h in HAZARDS}}
MARKS = {"uniform": uniform, "discerning": discerning, "complacent": complacent}


def output(policy, timeline) -> float:
    return sum((row.output for row in play(policy, timeline).rows), 0.0)


def scores(world: Mapping[str, ScenarioConfig], seeds: Sequence[int]) -> dict[str, dict[str, float]]:
    """Each reader's mean run score on each scenario."""
    out: dict[str, dict[str, list[float]]] = {reader: {name: [] for name in NAMES} for reader in READERS}
    for name in NAMES:
        for seed in seeds:
            t = make_timeline(world[name], seed)
            low, high = output(MARKS["uniform"], t), output(MARKS["discerning"], t)
            for reader, policy in READERS.items():
                out[reader][name].append((output(policy, t) - low) / (high - low))
    return {reader: {name: float(np.mean(v)) for name, v in by_name.items()} for reader, by_name in out.items()}


def markdown(by_world: Mapping[str, dict[str, dict[str, float]]], seeds: Sequence[int]) -> str:
    lines = [
        "# Two readers",
        "",
        "Written by `shapes/src/make.py --readers`. Do not edit by hand. What it is for is in "
        "[the README](README.md#two-readers).",
        "",
        f"- **Seeds.** The first {len(seeds)} public seeds. A run scores 0 at the Uniform baseline and 1 at the Discerning.",
        "- **A shock's cost** is a reader's score on No change less its score on One shock.",
        "",
        "| Reader | World | No change | One shock | Down switch | A shock's cost |",
        "|---|---|---|---|---|---|",
    ]
    for reader in READERS:
        for world, scored in by_world.items():
            s = scored[reader]
            lines.append(
                f"| {reader} | {world} | {s['no_change']:.2f} | {s['one_shock']:.2f} | {s['down_switch']:.2f} | "
                f"{s['no_change'] - s['one_shock']:.2f} |"
            )
    lines += ["", "| World | Best hazard on One shock | Best hazard on Down switch | They differ |", "|---|---|---|---|"]
    for world, scored in by_world.items():
        best = {name: max((r for r in READERS if r.startswith("Bayesian")), key=lambda r: scored[r][name]) for name in NAMES}
        shock, switch = best["one_shock"].split()[1], best["down_switch"].split()[1]
        lines.append(f"| {world} | {shock} | {switch} | {'yes' if shock != switch else 'no'} |")
    return "\n".join(lines) + "\n"


def readers(worlds: Mapping[str, Mapping[str, ScenarioConfig]], seeds: Sequence[int]) -> str:
    return markdown({world: scores(configs, seeds) for world, configs in worlds.items()}, seeds)
