"""One log into rows: the guards, the privacy rules and the metric check. See docs/specs/analysis/runs.md.

Reads `sample.id`, `.scores`, `.metadata`, `.model_usage` and `.epoch`, `log.eval` and `log.results`, and
nothing else, so no reading, bet or skin word reaches the run table.
"""

import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from inspect_ai.log import EvalLog, read_eval_log

from paranoid.engine import SCENARIOS
from paranoid.harness import bootstrap, pooled_score

from .keys import ResultKey, kind_of, result_key

TASK = "paranoid/paranoid"  # what inspect names the task however it was run, see #checked
SCORE_COLUMNS = (
    "output", "uniform", "discerning", "complacent", "perfect", "hedge_rule", "scout_rule", "gain", "gap", "run_score",
    "rounds", "warm_up_rounds", "retries", "retry_rounds", "gave_up", "bad_calls", "no_calls", "cut_offs",
    "notes_rounds", "compute_rounds", "unchanged_rounds", "explore_points", "sleeper_round", "warm_up_kept",
)  # fmt: skip
USAGE_COLUMNS = ("input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "total_tokens")
USAGE_FIELDS = dict(zip(USAGE_COLUMNS, (
    "input_tokens", "input_tokens_cache_read", "input_tokens_cache_write", "output_tokens", "reasoning_tokens", "total_tokens",
)))  # fmt: skip
METRIC_KEYS = (("score", ""), ("lo", "_lo"), ("hi", "_hi"), ("n", "_n"), ("failed", "_failed"))
TOLERANCE = 1e-9


@dataclass
class LogRows:
    """One log read: its key, its rows, and what the report needs from it."""

    path: Path
    name: str  # as the `log` column has it
    started: pd.Timestamp
    key: ResultKey
    rows: list[dict[str, Any]]
    ids: set[str] = field(default_factory=set)
    checked: bool = False

    @property
    def samples(self) -> int:
        return len(self.ids)

    @property
    def errored(self) -> int:
        return sum(1 for row in self.rows if row["errored"])


def read_log(path: Path, name: str) -> EvalLog | None:
    """The log, or None when it is not the paranoid task. A file that is not a log raises ValueError."""
    try:
        log = read_eval_log(str(path))
    except Exception as error:  # inspect raises several kinds on a file that is not a log
        raise ValueError(f"{name} is not an inspect log: {type(error).__name__}") from None
    return log if log.eval.task == TASK else None


def rows_of_log(log: EvalLog, path: Path, name: str) -> LogRows:
    key = result_key(log)
    where = f"log {name}"
    epochs = Counter(str(sample.id) for sample in log.samples or [])
    rows = [sample_row(sample, key, kind_of(log), where, epochs[str(sample.id)]) for sample in log.samples or []]
    started = pd.Timestamp(log.eval.created).tz_convert("UTC")
    found = LogRows(path=path, name=name, started=started, key=key, rows=rows, ids=set(epochs))
    found.checked = check_metrics(log, found, where)
    return found


def sample_row(sample, key: ResultKey, kind: str, where: str, epochs: int) -> dict[str, Any]:
    metadata = sample.metadata or {}
    scenario, index = metadata.get("scenario"), metadata.get("seed_index")
    if scenario not in SCENARIOS:
        raise ValueError(f"{where}: sample {sample.id} claims scenario {scenario!r}, which is not in SCENARIOS")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise ValueError(f"{where}: sample {sample.id} has seed_index {index!r}, not a whole number from 0")
    if key.setting.seed_set == "held-out" and "seed" in metadata:
        raise ValueError(f"{where}: held-out sample {sample.id} has a seed in its metadata")
    choice = metadata.get("tool_choice")
    if choice is not None and choice not in ("any", "auto"):
        raise ValueError(f"{where}: sample {sample.id} has tool_choice {choice!r}, not any or auto")
    score = (sample.scores or {}).get("gain")
    value = score.value if score is not None else None
    errored = not isinstance(value, dict)
    row: dict[str, Any] = {
        "kind": kind, "scenario": scenario, "seed_index": index,
        "seed": metadata.get("seed") if key.setting.seed_set == "public" else None,
        "engine_hash": metadata.get("engine_hash"), "numpy_version": metadata.get("numpy_version"),
        "epoch": sample.epoch, "epochs": epochs, "sample_id": str(sample.id),
    }  # fmt: skip
    for column in SCORE_COLUMNS:
        row[column] = None if errored else value.get(column)  # type: ignore[union-attr]
    usage = list((sample.model_usage or {}).values())
    for column, name in USAGE_FIELDS.items():
        row[column] = None if errored else sum((getattr(u, name, None) or 0) for u in usage)
    row["errored"] = errored
    return row


def logged_metrics(log: EvalLog) -> dict[str, float] | None:
    """The scenario_score metric by the key it returned, found by group and name, never by inspect's dict key."""
    if log.results is None:
        return None
    found = {
        metric.name: metric.value
        for score in log.results.scores
        for metric in score.metrics.values()
        if getattr(metric, "group", None) == "scenario_score"
    }
    return found or None


def check_metrics(log: EvalLog, found: LogRows, where: str) -> bool:
    """Pool the log's own rows and hold them against its metric. False when the check does not apply."""
    metrics = logged_metrics(log)
    if metrics is None or any(row["epochs"] != 1 for row in found.rows):
        return False
    scored = [row for row in found.rows if not row["errored"]]
    for scenario in SCENARIOS:
        group = sorted((row for row in scored if row["scenario"] == scenario), key=lambda row: row["seed_index"])
        if not group:
            continue
        gains = np.array([float(row["gain"]) for row in group])
        gaps = np.array([float(row["gap"]) for row in group])
        lo, hi = bootstrap(gains, gaps)
        mine = {"score": pooled_score(gains, gaps), "lo": lo, "hi": hi, "n": len(group)}
        mine["failed"] = sum(int(row["gave_up"] or 0) for row in group)
        for name, suffix in METRIC_KEYS:
            logged = metrics.get(f"{scenario}{suffix}")
            if logged is None or not math.isclose(mine[name], logged, rel_tol=TOLERANCE, abs_tol=TOLERANCE):
                raise ValueError(f"{where}: scenario {scenario} {name} is {mine[name]} here and {logged} in the log's metric")
    return True
