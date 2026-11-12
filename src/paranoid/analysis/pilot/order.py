"""The engine sections that check an order or a pass line: Bayesian frontier, Baseline order, Reachable gain and
Timestral checks. See docs/specs/analysis/pilot.md#sections and docs/pilot/engine-checks.md.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from ..names import design_name, number
from .charts import lines
from .common import BLIND, BOTH_WAYS, SWITCH_OR_DRIFT, Section, engine_scores, holds, read_csv, share

REACHABLE_GAIN_FLOOR = 0.3  # the reachable gain check's three pass lines, see docs/pilot/engine-checks.md#reachable-gain
BAYESIAN_GAIN_PERCENTAGE_FLOOR = 50
BAYESIAN_MOVE_SHARE_FLOOR = 0.5
APPROX = 0.05  # how close two scores are for ≈, and how far below ≥ may sit: room for a blind baseline's explore cost
NAMES = {
    "perfect": "Perfect",
    "discerning": "Discerning",
    "hedge_rule": "hedge rule",
    "complacent": "Complacent",
    "uniform": "Uniform",
    "scout_rule": "Scout rule",
    "stayer": "Stayer",
}
DOWN = ["perfect", ">", "discerning", ">", "hedge_rule", ">", "complacent", ">", "uniform"]
UP = ["perfect", ">", "discerning", ">", "scout_rule", ">", "complacent", "≈", "hedge_rule", ">", "uniform"]
ORDERS = [  # (scenario, order), from the Baseline order check's Measure
    ("down_switch", DOWN),
    ("up_switch", UP),
    ("up_switch (rise_short)", ["complacent", "≈", "discerning", "≈", "hedge_rule", "≥", "scout_rule"]),
    ("no_change", ["complacent", "≈", "discerning", "≈", "hedge_rule"]),
    ("switch_then_shock", DOWN),
    (BOTH_WAYS, ["perfect", ">", "discerning", ">", "scout_rule", ">", "stayer", ">", "uniform"]),
    (BOTH_WAYS, ["complacent", "≥", "hedge_rule"]),
]


def bayesian_frontier(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "bayesian-frontier")
    if frame is None:
        return None
    frame = frame.assign(
        player=[b if pd.isna(h) else f"bayesian {h} {r}" for b, h, r in zip(frame["baseline"], frame["hazard"], frame["rule"])]
    )
    players = with_headline(engine_scores(frame, ["scenario"], player="player"))
    seeds = sorted(frame["seed"].unique())
    split = seeds[len(seeds) // 2]  # the lower half of the seeds picks and the rest report
    early, late = (
        with_headline(engine_scores(part, ["scenario"], player="player"))
        for part in (frame[frame["seed"] < split], frame[frame["seed"] >= split])
    )
    section = Section()
    section.table("players", players)
    heads = early[(early["scenario"] == "headline") & early["player"].str.startswith("bayesian ")]
    if len(heads):
        best = heads.sort_values(["score", "player"], ascending=[False, True]).iloc[0]["player"]
        later = late[late["player"] == best].set_index("scenario")["score"]
        down = later.get("down_switch")
        pick = {
            "player": best,
            "headline_early": heads.set_index("player").loc[best, "score"],
            "headline_late": later.get("headline"),
        }
        section.table(
            "pick", pd.DataFrame([pick | {"down_switch_late": down, "irreducible_lag": None if down is None else 1 - down}])
        )
    planes = players.pivot_table(index="player", columns="scenario", values="score").reset_index()
    if {"down_switch", "no_change"} <= set(planes.columns):
        section.plot(
            "planes",
            lambda out: lines(
                planes.sort_values("no_change"), "no_change", "down_switch", None, "Down switch against No change", out
            ),
        )
    return section


def with_headline(scores: pd.DataFrame) -> pd.DataFrame:
    """Each player's scenario scores, and a `headline` row: their plain mean."""
    head = scores.groupby("player", sort=True).agg(seeds=("seeds", "min"), score=("score", "mean")).reset_index()
    return pd.concat([scores, head.assign(scenario="headline")], ignore_index=True)[list(scores.columns)]


def order_scores(frame: pd.DataFrame) -> pd.DataFrame:
    """Pooled output and scenario score per scenario and baseline, the rise_short Up switch seeds apart."""
    short = (frame["scenario"] == "up_switch") & (frame["kind"] == "rise_short")
    frame = frame.assign(scenario=frame["scenario"].where(~short, "up_switch (rise_short)"))
    scores = engine_scores(frame, ["scenario"])
    outputs = frame.groupby(["scenario", "baseline"], sort=False)["output"].sum().rename("output").reset_index()
    return scores.merge(outputs, on=["scenario", "baseline"], how="left")


def compare(a: float, sign: str, b: float) -> bool:
    if sign == ">":
        return a > b
    if sign == "≥":
        return a >= b - APPROX
    return abs(a - b) <= APPROX


def baseline_order(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "baseline-order")
    if frame is None:
        return None
    scores = order_scores(frame)
    section = Section()
    section.table("outputs", scores)
    by = scores.set_index(["scenario", "baseline"])["score"]
    rows = []
    for scenario, order in ORDERS:
        names = order[::2]
        if not all((scenario, n) in by.index for n in names):
            continue
        ok = all(compare(by[(scenario, a)], sign, by[(scenario, b)]) for a, sign, b in zip(order[::2], order[1::2], order[2::2]))
        text = " ".join(NAMES.get(t, t) for t in order)
        rows.append({"scenario": scenario, "order": holds(f"{scenario_words(scenario)}: {text}", ok)})
    section.table("orders", pd.DataFrame(rows))
    return section


def scenario_words(scenario: str) -> str:
    """A scenario's design name, or `Up switch, rise_short seeds` for the seeds apart."""
    name, _, rest = scenario.partition(" (")
    return design_name(name) + (f", {rest.rstrip(')')} seeds" if rest else "")


def reachable_gain(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "baseline-order")
    if frame is None:
        return None
    by = engine_scores(frame, ["scenario"]).set_index(["scenario", "baseline"])["score"]
    rows, lines_ = [], []
    for scenario in SWITCH_OR_DRIFT:
        base = "stayer" if scenario == BOTH_WAYS else "complacent"
        if (scenario, base) not in by.index:
            continue
        reachable = by[(scenario, "discerning")] - by[(scenario, base)]
        bayesian = by.get((scenario, "bayesian"), np.nan) - by[(scenario, base)]
        percentage = 100 * bayesian / reachable if reachable else np.nan
        row = {
            "scenario": scenario,
            "against": base,
            "reachable_gain": reachable,
            "bayesian_gain": bayesian,
            "bayesian_gain_percentage": percentage,
        }
        name = design_name(scenario)
        lines_.append(
            {
                "line": holds(
                    f"{name}: reachable gain {number(reachable)} against a floor of {REACHABLE_GAIN_FLOOR}",
                    reachable >= REACHABLE_GAIN_FLOOR,
                )
            }
        )
        lines_.append(
            {
                "line": holds(
                    f"{name}: Bayesian gain percentage {number(percentage, 0)}% against a floor of "
                    f"{BAYESIAN_GAIN_PERCENTAGE_FLOOR}%",
                    percentage >= BAYESIAN_GAIN_PERCENTAGE_FLOOR,
                )
            }
        )
        if scenario == BOTH_WAYS:
            bayes = frame[(frame["scenario"] == scenario) & (frame["baseline"] == "bayesian")]
            moved = share(bayes["move_round"] > 0)
            row["bayesian_move_share"] = moved
            if moved is not None:
                lines_.append(
                    {
                        "line": holds(
                            f"{name}: the Bayesian baseline moves on {number(moved)} of seeds against a floor of "
                            f"{BAYESIAN_MOVE_SHARE_FLOOR}",
                            moved >= BAYESIAN_MOVE_SHARE_FLOOR,
                        )
                    }
                )
        rows.append(row)
    section = Section()
    table = pd.DataFrame(rows)
    section.table("gains", table)
    calm = [{"baseline": b, "explore_cost": 1 - by[("no_change", b)]} for b in BLIND if ("no_change", b) in by.index]
    section.table("explore-cost", pd.DataFrame(calm))
    section.table("lines", pd.DataFrame(lines_))
    if len(table):
        section.plot(
            "gains",
            lambda out: lines(
                table,
                "reachable_gain",
                "bayesian_gain",
                None,
                "Bayesian gain against reachable gain",
                out,
                marks=[REACHABLE_GAIN_FLOOR],
            ),
        )
    return section


def timestral_checks(logs: Path, main: Path | None) -> Section | None:
    probe, rounding, grid = (read_csv(logs, n) for n in ("timestral", "timestral-rounding", "timestral-grid"))
    if probe is None and rounding is None and grid is None:
        return None
    section = Section()
    if probe is not None:
        gaps = probe[probe["probe"] == "gap"].groupby(["joint", "gap"], sort=True)["spread"].mean().reset_index()
        same = probe[probe["probe"] == "determinism"][["joint", "equal"]]
        section.table(
            "gap-test",
            pd.concat([gaps.assign(probe="gap"), same.assign(probe="determinism")], ignore_index=True)[
                ["probe", "joint", "gap", "spread", "equal"]
            ],
        )
        section.plot("gap-test", lambda out: lines(gaps, "gap", "spread", "joint", "Spread against blanks", out))
    if rounding is not None:
        section.table("rounding", rounded(rounding))
    noise = read_csv(logs, "noise-grid")
    if grid is not None and noise is not None:
        keys = ["setting", "scenario", "seed"]
        marks = noise[noise["baseline"].isin(["uniform", "discerning", "hedge_rule", "complacent"])][
            [*keys, "baseline", "output"]
        ]
        played = grid.rename(columns={"model": "baseline"})[[*keys, "baseline", "output"]]
        marks = marks.merge(played[keys].drop_duplicates(), on=keys)  # the marks on the seeds the policies played
        section.table("grid", engine_scores(pd.concat([marks, played], ignore_index=True), ["setting", "scenario"]))
    return section


def rounded(frame: pd.DataFrame) -> pd.DataFrame:
    """The mean rounded_out a round and the share of rounds where it is above 0, per model."""
    return (
        frame.groupby("model", sort=True)["rounded_out"]
        .agg(mean_rounded_out="mean", rounded_share=lambda v: float((v > 0).mean()))
        .reset_index()
    )
