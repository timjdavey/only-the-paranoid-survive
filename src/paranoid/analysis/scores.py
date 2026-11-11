"""scenario_scores, headlines, load_recognition and the flags. See docs/specs/analysis/scores.md.

Every pooled score is the harness's pooled_score and every scenario bar its bootstrap, so a table here equals the
log's own metric.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from paranoid.harness import TRAITS, bootstrap

from .keys import KEY_COLUMNS, key_values, rows_of
from .pool import arrays, draws, each_key, fresh_rng, percentiles, pooled, share

RETRY_FLAG = 0.1  # retry share that flags a bar, pilot to confirm
RECOGNITION_FLAG = 0.25  # recognition hit share that flags a model, pilot to confirm
RECOGNITION_COLUMNS = ("model", "skin", "probe", "lint_hits", "canary_finished")
SCORED_PROBES = ("round_1", "round_20")  # a canary reply is never a hit, so it stays out of the share
MARKS = ("complacent", "hedge_rule", "scout_rule", "perfect")
FLAGS = "†‡§¶"


def load_recognition(path: Path) -> pd.DataFrame:
    """The recognition CSV's five columns. The reply is never read, so no function here can hold one."""
    header = pd.read_csv(path, nrows=0).columns
    missing = [column for column in RECOGNITION_COLUMNS if column not in header]
    if missing:
        raise ValueError(f"{path} has no {', '.join(missing)} column")
    table = pd.read_csv(path, usecols=list(RECOGNITION_COLUMNS), dtype={"model": "str", "skin": "str", "probe": "str"})
    table["lint_hits"] = table["lint_hits"].astype("Int64")
    table["canary_finished"] = table["canary_finished"].astype("Int64").astype("boolean")
    return table[list(RECOGNITION_COLUMNS)]


def model_flags(model: str, recognition: pd.DataFrame | None) -> str:
    """§ and ¶ for one model, from the recognition table."""
    if recognition is None:
        return ""
    mine = recognition[recognition["model"] == model]
    probed = mine[mine["probe"].isin(SCORED_PROBES)]
    flags = ""
    if len(probed) and (probed["lint_hits"].fillna(0) > 0).mean() > RECOGNITION_FLAG:
        flags += "§"
    if mine["canary_finished"].fillna(False).astype(bool).any():
        flags += "¶"
    return flags


def ordered(flags: str) -> str:
    return "".join(flag for flag in FLAGS if flag in flags)


def scenario_scores(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per ResultKey and scenario, see scores.md#scenario-scores."""
    rows = []
    for key, groups in each_key(runs):
        recognised = model_flags(key.model, recognition)
        for scenario, group in groups.items():
            rows.append(key_values(key) | scenario_row(scenario, group, recognised))
    columns = [*KEY_COLUMNS, "scenario", "trait", "score", "lo", "hi", "n", "failed", "retry_share", "cut_off_share"]
    columns += ["notes_share", "compute_share", *MARKS, "flags"]
    return pd.DataFrame(rows, columns=columns)


def scenario_row(scenario: str, group: pd.DataFrame, recognised: str) -> dict:
    gains, gaps = arrays(group)
    lo, hi = bootstrap(gains, gaps)
    failed = int(group["gave_up"].fillna(False).astype(bool).sum())
    retry = share(group, "retry_rounds")
    flags = ("†" if failed else "") + ("‡" if retry > RETRY_FLAG else "") + recognised
    row = {
        "scenario": scenario, "trait": TRAITS[scenario], "score": pooled(group), "lo": lo, "hi": hi,
        "n": len(group), "failed": failed, "retry_share": retry, "cut_off_share": share(group, "cut_offs"),
        "notes_share": share(group, "notes_rounds"), "compute_share": share(group, "compute_rounds"),
    }  # fmt: skip
    return row | {mark: pooled(group, mark) for mark in MARKS} | {"flags": ordered(flags)}


def headlines(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per ResultKey, see scores.md#headlines."""
    scores = scenario_scores(runs, recognition=recognition)
    rows = []
    for key, groups in each_key(runs):
        rows.append(key_values(key) | headline_row(key, groups, scores))
    columns = [*KEY_COLUMNS, "headline", "lo", "hi", "scenarios", "weakest_scenario", "weakest_trait"]
    return pd.DataFrame(rows, columns=columns + ["weakest_score", "flags"])


def headline_row(key, groups: dict[str, pd.DataFrame], scores: pd.DataFrame) -> dict:
    rng = fresh_rng()  # one rng, one block of draws per scenario in SCENARIOS order
    drawn = np.mean([draws(group, rng) for group in groups.values()], axis=0)
    lo, hi = percentiles(drawn)
    pooled_scores = {scenario: pooled(group) for scenario, group in groups.items()}
    weakest = min(pooled_scores, key=lambda s: pooled_scores[s])  # min keeps the first of a tie
    mine = rows_of(scores, key)
    return {
        "headline": float(np.mean(list(pooled_scores.values()))), "lo": lo, "hi": hi, "scenarios": len(groups),
        "weakest_scenario": weakest, "weakest_trait": TRAITS[weakest], "weakest_score": pooled_scores[weakest],
        "flags": ordered("".join(mine["flags"])),
    }  # fmt: skip
