"""The provider sections that read a model's logs: Seeds and repeats, Recognition, Channel order, Up against down
and Jev checks. See docs/specs/analysis/pilot.md#sections and docs/pilot/provider-checks.md.
"""

import math
from itertools import combinations
from pathlib import Path

import pandas as pd

from paranoid.harness import bootstrap

from ..gaps import paired_gap, scenario_gap
from ..keys import compared, keys_in, label, rows_of
from ..kinds import WORLD, switch_kinds
from ..names import slug
from ..plots import strip_plot
from ..pool import by_scenario, pooled, scored
from ..runs import load_runs, mean_over_epochs
from ..scores import load_recognition
from ..spread import sampling_share, spread
from .charts import lines
from .common import CELL_COLUMNS, Section, median, read_cell, read_csv, share
from .order import rounded

TARGETS = (0.02, 0.05, 0.1)  # the bar half widths the seeds check sizes for
GAPS = (
    ("one_shock", "down_switch"),
    ("up_switch", "no_change"),
    ("up_switch_then_down_switch", "up_switch"),
    ("switch_then_shock", "down_switch"),
)  # the four the up against down check reads


def seeds_and_repeats(logs: Path, main: Path | None) -> Section | None:
    seeds, repeats = read_cell(logs, "seeds"), read_cell(logs, "repeats", per_epoch=True)
    if seeds is None and repeats is None:
        return None
    section = Section()
    if seeds is not None:
        spreads = spread(seeds)
        section.table("spread", spreads)
        widest = spreads.dropna(subset=["sd"]).sort_values("sd", ascending=False, kind="mergesort").head(1)
        if len(widest):
            row = widest.iloc[0]
            needed = [
                {
                    "model": row["model"],
                    "reasoning": row["reasoning"],
                    "scenario": row["scenario"],
                    "sd": row["sd"],
                    "target": t,
                    "seeds_needed": math.ceil(round(1.5 * (row["sd"] / t) ** 2, 9)),
                }
                for t in TARGETS
            ]
            section.table("seeds-needed", pd.DataFrame(needed))
        for key in keys_in(scored(seeds)):
            section.plot(f"strip-{slug(label(key))}", lambda out, k=key: strip_plot(seeds, k, out))
    if repeats is not None:
        section.table("sampling-share", sampling_share(repeats))
    return section


def recognition(logs: Path, main: Path | None) -> Section | None:
    path = logs / "recognition.csv"
    if not path.exists():
        return None
    header = list(pd.read_csv(path, nrows=0).columns)
    if header != list(CELL_COLUMNS["recognition"]):
        raise ValueError(f"{path} has columns its cell does not write: {', '.join(header)}")
    table = load_recognition(path)  # the reply is never read
    rows = []
    for (model, skin), group in table.groupby(["model", "skin"], sort=True):
        probed = group[group["probe"].isin(["round_1", "round_20"])]
        hits = int((probed["lint_hits"].fillna(0) > 0).sum())
        rows.append(
            {
                "model": model,
                "skin": skin,
                "probes": len(probed),
                "hits": hits,
                "hit_share": hits / len(probed) if len(probed) else None,
                "canary_finished": int(group["canary_finished"].fillna(False).astype(bool).sum()),
            }
        )
    section = Section()
    section.table("hits", pd.DataFrame(rows))
    return section


def channel_order(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "channel-order")
    if frame is None:
        return None
    rows = []
    for keys, group in [
        *frame.groupby(["model", "skin", "shape"], sort=True),
        *((k + ("all", "all"), g) for k, g in frame.groupby(["model"])),
    ]:
        valid = group[group["valid"] == 1]
        rows.append(
            dict(zip(("model", "skin", "shape"), keys))
            | {
                "probes": len(group),
                "called_share": share(group["called"] == 1),
                "valid_share": share(group["valid"] == 1),
                "slip_share": share(valid["slipped"] == 1),
                "own_numbers_share": share((valid["matched"] != 1) & (valid["slipped"] != 1)),
            }
        )
    slips = []
    for _, row in frame[frame["slipped"] == 1].iterrows():
        wanted, sent = str(row["wanted"]).split(), str(row["sent"]).split()
        slips.append({"model": row["model"], "place": next(i for i, (w, s) in enumerate(zip(wanted, sent)) if w != s)})
    section = Section()
    section.table("shares", pd.DataFrame(rows))
    if slips:
        section.table("slips", pd.DataFrame(slips).groupby(["model", "place"]).size().rename("slips").reset_index())
    return section


def up_against_down(logs: Path, main: Path | None) -> Section | None:
    played = read_cell(logs, "up-against-down")
    if played is None:
        return None
    seeds = read_cell(logs, "seeds")
    table = played
    for key in keys_in(played):
        if seeds is None:
            continue
        mine = [
            k
            for k in keys_in(seeds)
            if (k.model, k.reasoning) == (key.model, key.reasoning) and compared(k.setting) == compared(key.setting)
        ]
        for other in mine:  # the One shock rows only, as the Up switch ids would clash, under this log's version
            shock = rows_of(seeds, other)
            shock = shock[shock["scenario"] == "one_shock"].assign(harness_version=key.setting.harness_version)
            table = pd.concat([table, shock], ignore_index=True)
    table = table.astype(played.dtypes.to_dict())
    kinds = scored(table).merge(switch_kinds(table), on=list(WORLD), how="left")
    section = Section()
    section.table("kinds", kinds_table(kinds))
    section.table("gaps", gaps_table(table, kinds))
    section.table("sleeper", sleeper_table(scored(table)))
    labelled = pd.concat([rows_of(kinds, k).assign(row=label(k)) for k in keys_in(kinds)] or [kinds.assign(row="")])
    if main is None:
        section.notes.append("_Inertia needs --main._")
    else:
        section.table("inertia", inertia_table(mean_over_epochs(load_runs([main]))))
    section.plot(
        "kinds",
        lambda out: lines(
            labelled.dropna(subset=["run_score"]),
            "switch_kind",
            "run_score",
            "scenario",
            "Run score by switch kind",
            out,
            panels="row",
        ),
    )
    return section


def kinds_table(kinds: pd.DataFrame) -> pd.DataFrame:
    """Per result row, scenario and switch kind: the seeds and the pooled score with its bar."""
    rows = []
    for key in keys_in(kinds):
        for (scenario, kind), group in rows_of(kinds, key).groupby(["scenario", "switch_kind"], sort=True):
            group = group.sort_values("seed_index")
            lo, hi = bootstrap(group["gain"].to_numpy(float), group["gap"].to_numpy(float))
            row = {"model": label(key), "scenario": scenario, "switch_kind": kind, "seeds": len(group)}
            rows.append(row | {"score": pooled(group), "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def gaps_table(table: pd.DataFrame, kinds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    risen = kinds[(kinds["scenario"] == "up_switch") & (kinds["switch_kind"] != "rise_short")]["seed_index"].tolist()
    for key in keys_in(scored(table)):
        groups = by_scenario(rows_of(table, key))
        for a, b in GAPS:
            if a in groups and b in groups:
                seeds = risen if (a, b) == ("up_switch_then_down_switch", "up_switch") else None
                gap = scenario_gap(table, key, a, b, seeds)
                rows.append({"model": label(key)} | gap.iloc[0].to_dict())
    return pd.DataFrame(rows)


def sleeper_table(table: pd.DataFrame) -> pd.DataFrame:
    """Per result row and scenario: how often and how soon a bet reached the sleeper, and the mean explore points."""
    rows = []
    for key in keys_in(table):
        for scenario, group in by_scenario(rows_of(table, key)).items():
            sleeper = group["sleeper_round"].dropna()
            reached = sleeper[sleeper > 0]
            rows.append(
                {
                    "model": label(key),
                    "scenario": scenario,
                    "reached_share": share(sleeper > 0) if len(sleeper) else None,
                    "median_round": median(reached.astype(float)),
                    "explore_points": group["explore_points"].mean(),
                }
            )
    return pd.DataFrame(rows)


def inertia_table(main: pd.DataFrame) -> pd.DataFrame:
    """One row per two result rows of main that share a setting: their Down switch and Slow drift gaps."""
    rows = []
    for a, b in combinations(keys_in(scored(main)), 2):
        if compared(a.setting) != compared(b.setting):
            continue
        gap = paired_gap(main, a, b).set_index("pair")
        row = {"a": label(a), "b": label(b)}
        for scenario in ("down_switch", "slow_drift"):
            if scenario in gap.index:
                row |= {f"{scenario}_{c}": gap.loc[scenario, c] for c in ("diff", "lo", "hi")}
        rows.append(row)
    return pd.DataFrame(rows)


def jev_checks(logs: Path, main: Path | None) -> Section | None:
    played, frame = read_cell(logs, "jev"), read_csv(logs, "jev")
    if played is None and frame is None:
        return None
    section = Section()
    if frame is not None:
        section.table("rounding", rounded(frame))
    if played is not None:
        calm = scored(played)[scored(played)["scenario"] == "no_change"]
        section.table("explore", calm.groupby(["model", "reasoning"], sort=True)["explore_points"].mean().reset_index())
    return section
