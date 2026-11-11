"""write_run_csv and CSV_COLUMNS: one row per run beside the results page. See docs/specs/analysis/tables.md#the-run-csv.

One score per run and the two numbers that pool it. No output, so no total that could place a timeline.
"""

import csv
import io
from pathlib import Path
from typing import Any

import pandas as pd

from .keys import KEY_COLUMNS
from .pool import scored

CSV_COLUMNS: tuple[str, ...] = (
    "model", "reasoning", "skin", "scenario", "seed_set", "seed_index", "seed", "run_score", "gain", "gap", "epochs",
    "gave_up", "retry_rounds", "rounds", "cut_offs", "notes_rounds", "compute_rounds",
    "own_scale", "game_rounds", "tools", "warm_up", "rolling", "tool_choice", "inertia",
    "engine_hash", "prompt_hash", "generator_version", "harness_version", "release", "log",
)  # fmt: skip
SORT = (*KEY_COLUMNS, "scenario", "seed_index")


def text(value: Any) -> str:
    """NA as an empty cell, a bool as 1 or 0, a float as its repr, so the bytes are the same on every machine."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def run_csv_text(runs: pd.DataFrame) -> str:
    """The file's text, from the table after mean_over_epochs. Errored rows are left out."""
    rows = scored(runs).sort_values(list(SORT), na_position="first", kind="mergesort")
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for row in rows[list(CSV_COLUMNS)].itertuples(index=False):
        writer.writerow([text(value.item() if hasattr(value, "item") else value) for value in row])
    return out.getvalue()


def write_run_csv(runs: pd.DataFrame, path: Path) -> None:
    """`path`, one row per run in CSV_COLUMNS order."""
    path.write_text(run_csv_text(runs), encoding="utf-8")

