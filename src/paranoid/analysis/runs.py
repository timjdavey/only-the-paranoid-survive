"""load_runs and mean_over_epochs: logs into the run table. See docs/specs/analysis/runs.md.

One row per epoch of every sample, every column at one of four dtypes, and a report in `attrs["report"]`.
"""

from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from .keys import KEY_COLUMNS, ResultKey
from .read import SCORE_COLUMNS, USAGE_COLUMNS, LogRows, read_log, rows_of_log

RUN_COLUMNS: tuple[str, ...] = (
    "log",
    "started",
    *KEY_COLUMNS,
    "kind",
    "scenario",
    "seed_index",
    "seed",
    "engine_hash",
    "numpy_version",
    "epoch",
    "epochs",
    *SCORE_COLUMNS,
    *USAGE_COLUMNS,
    "errored",
)
STR = ("log", "model", "reasoning", "skin", "seed_set", "tools", "warm_up", "tool_choice", "prompt_hash", "harness_version")
STR += ("release", "kind", "scenario", "engine_hash", "numpy_version")
COUNTS = ("rounds", "warm_up_rounds", "retries", "retry_rounds", "bad_calls", "no_calls", "cut_offs", "notes_rounds")
COUNTS += ("compute_rounds", "unchanged_rounds")
INT = ("game_rounds", "inertia", "generator_version", "seed_index", "seed", "epoch", "epochs", *USAGE_COLUMNS, *COUNTS)
INT += ("sleeper_round",)
AVERAGED = ("output", "uniform", "discerning", "complacent", "perfect", "hedge_rule", "scout_rule", "gain", "gap")
AVERAGED += ("run_score", "explore_points", "warm_up_kept")
FLOAT = ("own_scale", *AVERAGED)
BOOL = ("rolling", "gave_up", "errored")
DTYPES: dict[str, str] = {c: "str" for c in STR} | {c: "Int64" for c in INT} | {c: "float64" for c in FLOAT}
DTYPES |= {c: "boolean" for c in BOOL}
SUMMED = (*COUNTS, *USAGE_COLUMNS)


def discover(paths: Iterable[str | Path]) -> list[tuple[Path, str]]:
    """(path, name) of every log: a folder searched for *.eval, named relative to it. Sorted by path.

    Two logs that get one name raise ValueError, as the `log` column could no longer tell their rows apart.
    """
    found: list[tuple[Path, str]] = []
    for given in map(Path, paths):
        if given.is_dir():
            found += [(path, path.relative_to(given).as_posix()) for path in given.rglob("*.eval")]
        elif given.exists():
            found.append((given, given.name))
        else:
            raise ValueError(f"{given} is not a log or a folder")
    found = sorted(found, key=lambda pair: pair[0].as_posix())
    first: dict[str, Path] = {}
    for path, name in found:
        if name in first and first[name].resolve() != path.resolve():
            raise ValueError(f"logs {first[name]} and {path} are both named {name}. Pass them so their names differ")
        first.setdefault(name, path)
    return found


def load_runs(paths: Iterable[str | Path]) -> pd.DataFrame:
    """One row per epoch of every sample, after duplicates are dropped. See runs.md#behaviour."""
    report: dict[str, Any] = {"read": [], "checked": 0, "skipped": [], "empty": [], "dropped": [], "errored": [], "numpy": []}
    logs: list[LogRows] = []
    for path, name in discover(paths):
        log = read_log(path, name)
        if log is None:
            report["skipped"].append(name)
            continue
        if not log.samples:
            report["empty"].append(name)
            continue
        logs.append(rows_of_log(log, path, name))
    kept = drop_duplicates(logs, report)
    for found in kept:
        report["read"].append((found.name, found.samples))
        report["checked"] += found.checked
        if found.errored:
            report["errored"].append((found.name, found.errored))
    table = frame([row | {"log": f.name, "started": f.started} | key_columns(f.key) for f in kept for row in f.rows])
    report["numpy"] = mixed_numpy(table)
    check_engine_hashes(table)
    table.attrs["report"] = report
    return table


def key_columns(key: ResultKey) -> dict[str, Any]:
    return {"model": key.model, "reasoning": key.reasoning} | asdict(key.setting)


def drop_duplicates(logs: list[LogRows], report: dict[str, Any]) -> list[LogRows]:
    """Within one key, a later log that covers an earlier one wins. Any other overlap raises ValueError."""
    ordered = sorted(logs, key=lambda f: (f.started, f.path.as_posix()))
    kept: list[LogRows] = []
    for later in ordered:
        for earlier in [f for f in kept if f.key == later.key and f.ids & later.ids]:
            if not later.ids >= earlier.ids:
                raise ValueError(
                    f"logs {earlier.name} and {later.name} share a result row and some samples. "
                    f"Only {earlier.name} has {', '.join(sorted(earlier.ids - later.ids))}. "
                    f"Only {later.name} has {', '.join(sorted(later.ids - earlier.ids)) or 'nothing'}. "
                    "Delete one, or rerun"
                )
            kept.remove(earlier)
            report["dropped"].append((earlier.name, later.name))
        kept.append(later)
    return sorted(kept, key=lambda f: f.path.as_posix())


def frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """The rows at RUN_COLUMNS and their dtypes."""
    data: dict[str, Any] = {}
    for column in RUN_COLUMNS:
        values = [row[column] for row in rows]
        if column == "started":
            data[column] = pd.to_datetime(pd.Series(values, dtype="object"), utc=True)
        else:
            data[column] = pd.array(values, dtype=DTYPES[column])
    return pd.DataFrame(data, columns=list(RUN_COLUMNS))


def mixed_numpy(table: pd.DataFrame) -> list[tuple[str, list[str]]]:
    """Each result row whose rows hold more than one numpy_version, by its label."""
    if table.empty:
        return []
    found = []
    for _, group in table.groupby(list(KEY_COLUMNS), dropna=False, sort=False):
        versions = sorted(set(group["numpy_version"].dropna()))
        if len(versions) > 1:
            row = group.iloc[0]
            found.append((f"{row['model']} ({row['reasoning']}) on {row['skin']}", versions))
    return found


def check_engine_hashes(table: pd.DataFrame) -> None:
    """One engine_hash per result row and scenario, else ValueError: the rows would pool two worlds."""
    if table.empty:
        return
    for _, group in table.groupby([*KEY_COLUMNS, "scenario"], dropna=False, sort=False):
        hashes = sorted(set(group["engine_hash"].dropna()))
        if len(hashes) > 1:
            row = group.iloc[0]
            raise ValueError(
                f"{row['model']} ({row['reasoning']}) on {row['skin']} played {row['scenario']} under engine hashes "
                f"{' and '.join(hashes)}, in {', '.join(sorted(set(group['log'])))}. Rerun one, or load them apart"
            )


def mean_over_epochs(runs: pd.DataFrame) -> pd.DataFrame:
    """One row per sample id of each log. The identity, bar `epoch`, when every sample has one epoch."""
    columns = [c for c in RUN_COLUMNS if c != "epoch"]
    if runs.empty or (runs["epochs"] == 1).all():
        result = runs.drop(columns="epoch").reset_index(drop=True)
        result.attrs = dict(runs.attrs)
        return result
    rows = [one_sample(group) for _, group in runs.sort_values("epoch").groupby(["log", "scenario", "seed_index"], sort=False)]
    result = pd.DataFrame(rows, columns=columns).astype({c: DTYPES[c] for c in columns if c in DTYPES})
    result = order_like(result, runs)
    result.attrs = dict(runs.attrs)  # concat and astype keep attrs only when they agree, so set it by hand
    return result


def one_sample(group: pd.DataFrame) -> dict[str, Any]:
    scored = group[~group["errored"].astype(bool)]
    row = group.iloc[0].to_dict()
    row.pop("epoch")
    for column in AVERAGED:
        values = scored[column].dropna()
        row[column] = float(values.mean()) if len(values) else None
    for column in SUMMED:
        row[column] = int(scored[column].sum()) if len(scored) else None
    sleeper = scored["sleeper_round"].dropna()
    positive = sleeper[sleeper > 0]
    row["sleeper_round"] = None if sleeper.empty else int(positive.min()) if len(positive) else 0
    row["gave_up"] = bool(scored["gave_up"].fillna(False).any()) if len(scored) else None
    row["errored"] = scored.empty
    return row


def order_like(result: pd.DataFrame, runs: pd.DataFrame) -> pd.DataFrame:
    """Rows in the order each sample first appears in `runs`."""
    first = runs.drop_duplicates(["log", "scenario", "seed_index"])[["log", "scenario", "seed_index"]].reset_index(drop=True)
    first["order"] = range(len(first))
    merged = result.merge(first, on=["log", "scenario", "seed_index"], how="left")
    return merged.sort_values("order", kind="mergesort").drop(columns="order").reset_index(drop=True)


def report_lines(report: dict[str, Any]) -> list[str]:
    """The report as the command prints it."""
    lines = [f"Read {len(report['read'])} logs, {report['checked']} checked against their own metrics:"]
    lines += [f"  {name}: {samples} samples" for name, samples in report["read"]]
    lines += [f"Skipped {name}, not the paranoid task" for name in report["skipped"]]
    lines += [f"Skipped {name}, it holds no samples" for name in report["empty"]]
    lines += [f"Dropped {name} as a duplicate, {winner} won" for name, winner in report["dropped"]]
    lines += [f"{count} samples errored in {name}" for name, count in report["errored"]]
    lines += [f"{row} holds numpy {', '.join(versions)}, so its timelines may differ" for row, versions in report["numpy"]]
    return lines
