"""spread and sampling_share. See docs/specs/analysis/scores.md#spread-and-sampling-share."""

import numpy as np
import pandas as pd

from .keys import KEY_COLUMNS, key_values
from .pool import each_key


def spread(runs: pd.DataFrame) -> pd.DataFrame:
    """Per result row and scenario: the SD of run scores over seeds, ddof=1, their 10th percentile, and the seeds."""
    rows = []
    for key, groups in each_key(runs):
        for scenario, group in groups.items():
            scores = group["run_score"].dropna().to_numpy(dtype=float)
            sd = float(np.std(scores, ddof=1)) if len(scores) > 1 else None
            p10 = float(np.percentile(scores, 10)) if len(scores) > 1 else None
            rows.append(key_values(key) | {"scenario": scenario, "sd": sd, "p10": p10, "n": len(group)})
    return pd.DataFrame(rows, columns=[*KEY_COLUMNS, "scenario", "sd", "p10", "n"])


def sampling_share(runs: pd.DataFrame) -> pd.DataFrame:
    """Per result row and scenario, from one row per epoch: how much of the spread is the model's own sampling.

    Variances are over every value, ddof=0, so the within and between parts add up to the total and the share is
    1 when every seed's mean is equal.
    """
    rows = []
    for key, groups in each_key(runs):
        for scenario, group in groups.items():
            scores = group.dropna(subset=["run_score"])
            per_seed = [g["run_score"].to_numpy(dtype=float) for _, g in scores.groupby("seed_index", sort=True)]
            repeated = [values for values in per_seed if len(values) > 1]
            total = float(np.std(scores["run_score"].to_numpy(dtype=float))) if len(scores) else None
            within = float(np.sqrt(np.mean([np.var(values) for values in repeated]))) if repeated else None
            share = within**2 / total**2 if within is not None and total else None
            epochs = int(group["epochs"].max()) if len(group) else 0
            row = {"scenario": scenario, "within_sd": within, "total_sd": total, "share": share}
            rows.append(key_values(key) | row | {"seeds": len(repeated), "epochs": epochs})
    return pd.DataFrame(rows, columns=[*KEY_COLUMNS, "scenario", "within_sd", "total_sd", "share", "seeds", "epochs"])
