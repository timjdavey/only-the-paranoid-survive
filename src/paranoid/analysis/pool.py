"""What every score shares: scored rows, a result row's rows per scenario, and draws. See docs/specs/analysis/scores.md#pooling.

Rows are ordered by seed_index before any draw and scenarios walked in SCENARIOS order, so the draws are the
ones the log's metric made.
"""

from collections.abc import Iterator

import numpy as np
import pandas as pd

from paranoid.engine import SCENARIOS
from paranoid.harness import BOOTSTRAP_DRAWS, BOOTSTRAP_SEED, draws_of, pooled_score

from .keys import ResultKey, keys_in, rows_of


def scored(runs: pd.DataFrame) -> pd.DataFrame:
    """The rows that did not error. They are in no score."""
    return runs[~runs["errored"].astype(bool)]


def by_scenario(rows: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """One result row's scored rows per scenario, scenarios in SCENARIOS order and seeds by seed_index."""
    rows = scored(rows)
    found = {}
    for name in SCENARIOS:
        group = rows[rows["scenario"] == name]
        if len(group):
            found[name] = group.sort_values("seed_index", kind="mergesort")
    return found


def each_key(runs: pd.DataFrame) -> Iterator[tuple[ResultKey, dict[str, pd.DataFrame]]]:
    """Every result row with scored rows, in the order it first appears, and its rows per scenario."""
    for key in keys_in(runs):
        groups = by_scenario(rows_of(runs, key))
        if groups:
            yield key, groups


def arrays(group: pd.DataFrame, gain: str = "gain") -> tuple[np.ndarray, np.ndarray]:
    """The gains and gaps that pool a group. `gain` may name a baseline, whose gain is its output less uniform's."""
    gaps = group["gap"].to_numpy(dtype=float)
    if gain == "gain":
        return group["gain"].to_numpy(dtype=float), gaps
    return (group[gain] - group["uniform"]).to_numpy(dtype=float), gaps


def pooled(group: pd.DataFrame, gain: str = "gain") -> float:
    return pooled_score(*arrays(group, gain))


def fresh_rng() -> np.random.Generator:
    return np.random.default_rng(BOOTSTRAP_SEED)


def draws(group: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """The pooled score of each of BOOTSTRAP_DRAWS resamples, the draws bootstrap makes."""
    gains, gaps = arrays(group)
    return draws_of(gains, gaps, rng, BOOTSTRAP_DRAWS)


def percentiles(values: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(lo), float(hi)


def share(group: pd.DataFrame, column: str) -> float:
    """sum(column) / sum(rounds), 0 with no round."""
    rounds = group["rounds"].sum()
    return float(group[column].sum() / rounds) if rounds else 0.0
