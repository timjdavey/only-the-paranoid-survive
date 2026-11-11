"""write_cost: tokens per run, the cached share and what the full study would cost. See docs/specs/analysis/tables.md#cost.

It takes the table with one row per epoch, as an epoch is a run, and writes and prints nothing.
"""

import tomllib
from pathlib import Path

import pandas as pd

from paranoid.engine import SCENARIOS
from paranoid.harness import load_models

from .keys import keys_in, rows_of
from .pool import scored

KINDS = {"input": "input_tokens", "cache_read": "cache_read_tokens", "cache_write": "cache_write_tokens"}
KINDS |= {"output": "output_tokens"}  # the four kinds a run is billed for, each at its own price
COLUMNS = ("model", "reasoning", "kind", "skin", "runs", *KINDS, "reasoning_tokens", "cached_share", "cut_off_share", "projected")


def load_prices(path: Path) -> tuple[dict[str, dict[str, float]], str | None]:
    """Price per million tokens per model id, each kind, a missing cache price priced as input. And the read_on date."""
    with path.open("rb") as file:
        data = tomllib.load(file)
    prices = {}
    for table in data.get("price", []):
        if "id" not in table or "input" not in table or "output" not in table:
            raise ValueError(f"{path}: every [[price]] needs id, input and output")
        prices[table["id"]] = {kind: float(table.get(kind, table["input"])) for kind in KINDS}
    read_on = data.get("read_on")
    return prices, None if read_on is None else str(read_on)


def write_cost(
    runs: pd.DataFrame, *, models: Path | None = None, seeds: int | None = None, prices: Path | None = None
) -> pd.DataFrame:
    """One row per result row, see tables.md#cost."""
    settings = {row.id: len(row.reasoning) for row in load_models(models)} if models is not None else {}
    priced, read_on = load_prices(prices) if prices is not None else ({}, None)
    rows = []
    for key in keys_in(runs):
        group = scored(rows_of(runs, key))
        if group.empty:
            continue
        means = {kind: float(group[column].mean()) for kind, column in KINDS.items()}
        read = sum(float(group[column].sum()) for column in ("input_tokens", "cache_read_tokens", "cache_write_tokens"))
        rounds = float(group["rounds"].sum())
        runs_of_model = seeds * len(SCENARIOS) * settings[key.model] if seeds and key.model in settings else None
        row = {
            "model": key.model,
            "reasoning": key.reasoning,
            "kind": str(group["kind"].iloc[0]),
            "skin": key.setting.skin,
            "runs": len(group),
            **means,
            "reasoning_tokens": float(group["reasoning_tokens"].mean()),
            "cached_share": float(group["cache_read_tokens"].sum()) / read if read else 0.0,
            "cut_off_share": float(group["cut_offs"].sum()) / rounds if rounds else 0.0,
            "projected": None if runs_of_model is None else sum(means.values()) * runs_of_model,
        }
        if prices is not None:
            price = priced.get(key.model)
            known = price is not None and runs_of_model is not None
            per_run = sum(means[k] * price[k] for k in KINDS) if known else 0.0  # type: ignore[index]
            row["cost"] = per_run * runs_of_model / 1e6 if known else None  # type: ignore[operator]
        rows.append(row)
    table = pd.DataFrame(rows, columns=list(COLUMNS) + (["cost"] if prices is not None else []))
    if read_on is not None:
        table.attrs["read_on"] = read_on
    return table
