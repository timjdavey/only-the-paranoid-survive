"""The provider sections that compare a knob: Bare harness, Tool choice, Rolling conversation and Warm up, and Cost
per run. See docs/specs/analysis/pilot.md#sections and docs/pilot/provider-checks.md.
"""

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from ..cost import write_cost
from ..gaps import paired_gap
from ..keys import ResultKey, keys_in, label, rows_of
from ..pool import by_scenario, scored, share
from ..scores import scenario_scores
from .charts import lines
from .common import Section, read_cell, read_csv

KEEP = ["model", "reasoning", "scenario", "score", "lo", "hi", "n"]


def knob_scores(runs: pd.DataFrame, knob: str, extra: dict[str, Callable[[pd.DataFrame], float]] | None = None) -> pd.DataFrame:
    """Scenario scores with the knob's column, and any extra column computed from each key and scenario's rows."""
    scores = scenario_scores(runs)
    table = scores[[*KEEP[:2], knob, *KEEP[2:]]].copy()
    for name, compute in (extra or {}).items():
        values = []
        for key in keys_in(scores):
            groups = by_scenario(rows_of(runs, key))
            values += [compute(groups[s]) for s in rows_of(scores, key)["scenario"]]
        table[name] = values
    return table


def gaps_against(runs: pd.DataFrame, knob: str, base: object) -> pd.DataFrame:
    """The headline paired gap of every other value of the knob against `base`, per model and reasoning."""
    keys = keys_in(scored(runs))
    rows = []
    for key in keys:
        if getattr(key.setting, knob) == base:
            continue
        bases = [k for k in keys if (k.model, k.reasoning) == (key.model, key.reasoning) and getattr(k.setting, knob) == base]
        if len(bases) != 1:
            continue
        gap = paired_gap(runs, key, bases[0]).set_index("pair").loc["headline"]
        clears = bool(gap["lo"] > 0 or gap["hi"] < 0)
        rows.append(
            {
                "model": label(key),
                knob: getattr(key.setting, knob),
                "against": base,
                "diff": gap["diff"],
                "lo": gap["lo"],
                "hi": gap["hi"],
                "n_shared": gap["n_shared"],
                "clears_zero": clears,
            }
        )
    return pd.DataFrame(rows)


def bare_harness(logs: Path, main: Path | None) -> Section | None:
    runs = read_cell(logs, "bare")
    if runs is None:
        return None
    section = Section()
    section.table("scores", knob_scores(runs, "tools").join(scenario_scores(runs)[["notes_share", "compute_share"]]))
    section.table("gaps", gaps_against(runs, "tools", "notes,compute"))
    return section


def tool_choice(logs: Path, main: Path | None) -> Section | None:
    runs = read_cell(logs, "tool-choice")
    if runs is None:
        return None
    section = Section()
    section.table("scores", knob_scores(runs, "tool_choice", {"no_call_share": lambda g: share(g, "no_calls")}))
    section.table("gaps", gaps_against(runs, "tool_choice", "any"))
    return section


def rolling(logs: Path, main: Path | None) -> Section | None:
    runs, tokens = read_cell(logs, "rolling"), read_csv(logs, "rolling-tokens")
    if runs is None and tokens is None:
        return None
    section = Section()
    if runs is not None:
        section.table("scores", knob_scores(runs, "rolling"))
        section.table("gaps", gaps_against(runs, "rolling", False))
    per_round = None
    if tokens is not None:
        tokens = tokens.assign(read=tokens["input_tokens"] + tokens["cache_read_tokens"] + tokens["cache_write_tokens"])
        per_round = tokens.groupby(["model", "rolling"], sort=True)["read"].mean().rename("input_per_round")
        curve = tokens.groupby(["rolling", "round"], sort=True)["read"].mean().reset_index()
        section.plot(
            "tokens", lambda out: lines(curve, "round", "read", "rolling", "Input tokens a round, fresh and rolling", out)
        )
    if runs is not None or per_round is not None:
        section.table("tokens", token_table(runs, per_round))
    return section


def token_table(runs: pd.DataFrame | None, per_round: pd.Series | None) -> pd.DataFrame:
    """Per model and rolling, tokens per run from the logs and input tokens per round from the token file."""
    frame = pd.DataFrame(columns=["model", "rolling"])
    if runs is not None:
        played = scored(runs).assign(rolling=lambda f: f["rolling"].astype(int))
        played = played.assign(read=played["input_tokens"] + played["cache_read_tokens"] + played["cache_write_tokens"])
        frame = played.groupby(["model", "rolling"], sort=True)["read"].mean().rename("tokens_per_run").reset_index()
    if per_round is not None:
        frame = frame.merge(per_round.reset_index(), on=["model", "rolling"], how="outer")
    return frame


def warm_up(logs: Path, main: Path | None) -> Section | None:
    runs = read_cell(logs, "warm-up")
    if runs is None:
        return None
    kept = {"warm_up_kept": lambda g: g["warm_up_kept"].mean()}
    section = Section()
    section.table("scores", knob_scores(runs, "warm_up", kept))
    rows = []
    for key in keys_in(scored(runs)):
        if key.setting.warm_up is None:
            continue
        cold = [
            k for k in keys_in(scored(runs)) if (k.model, k.reasoning) == (key.model, key.reasoning) and k.setting.warm_up is None
        ]
        if len(cold) == 1:
            rows.append({"model": label(key), "warm_up": key.setting.warm_up} | headline_gap(runs, key, cold[0]))
    section.table("gaps", pd.DataFrame(rows))
    return section


def headline_gap(runs: pd.DataFrame, a: ResultKey, b: ResultKey) -> dict:
    gap = paired_gap(runs, a, b).set_index("pair").loc["headline"]
    return {c: gap[c] for c in ("diff", "lo", "hi", "n_shared")}


def cost_per_run(logs: Path, main: Path | None) -> Section | None:
    cells = {cell: read_cell(logs, cell, per_epoch=True) for cell in ("seeds", "repeats")}
    tokens = read_csv(logs, "seeds-tokens")
    if all(runs is None for runs in cells.values()) and tokens is None:
        return None
    section = Section()
    tables = []
    for cell, runs in cells.items():
        if runs is None:
            continue
        table = write_cost(runs).assign(cell=cell)
        table["retry_share"] = [share(scored(rows_of(runs, key)), "retry_rounds") for key in keys_in(scored(runs))]
        tables.append(table)
    if tables:
        section.table("cost", pd.concat(tables, ignore_index=True))
    if tokens is not None:
        per_model = tokens.groupby("model", sort=True)[["input_tokens", "cache_read_tokens"]].mean().reset_index()
        section.table(
            "tokens", per_model.rename(columns={"input_tokens": "uncached_per_round", "cache_read_tokens": "cached_per_round"})
        )
        curve = tokens.melt(id_vars=["round"], value_vars=["input_tokens", "cache_read_tokens"], var_name="kind")
        curve = curve.groupby(["kind", "round"], sort=True)["value"].mean().reset_index()
        section.plot("tokens", lambda out: lines(curve, "round", "value", "kind", "Input tokens a round, cached and not", out))
    return section
