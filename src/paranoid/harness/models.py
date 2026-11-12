"""The models config and the reasoning mapping. See docs/specs/harness/command.md#models-config.

Columns are explained in docs/harness/models.md#columns.
"""

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal, cast

from inspect_ai.model import GenerateConfig

Kind = Literal["llm", "baseline", "jev", "timestral"]
ReasoningKind = Literal["effort", "budget", "n/a"]

KINDS: tuple[Kind, ...] = ("llm", "baseline", "jev", "timestral")
PROVIDER_KINDS = ("baseline", "jev", "timestral")  # each kind's id starts with `<kind>/`
REASONING = ("off", "low", "medium", "high", "max", "on")
EFFORT_PREFIXES = ("openai/", "anthropic/", "google/", "openrouter/")  # inspect maps an effort for all four
SKIN_READERS = ("llm", "jev")  # the kinds whose model reads the skin
BUDGETS = {"low": 1024, "medium": 4096, "high": 16384, "max": 32768}  # ours, so inspect's table never moves a row


@dataclass(frozen=True)
class ModelRow:
    id: str  # the inspect model string
    kind: Kind
    reasoning: tuple[str, ...]  # one or more of the grid, or ("n/a",) for a provider row
    reasoning_kind: ReasoningKind
    max_tokens: int | None = None
    released: date | None = None
    eci: float | None = None
    notes: str = ""
    pilot: bool = True  # false keeps the row out of every pilot cell, see docs/harness/models.md#columns


def load_models(path: str | Path) -> list[ModelRow]:
    """Every `[[model]]` table as a ModelRow, checked. Raises ValueError naming the row."""
    with Path(path).open("rb") as file:
        tables = tomllib.load(file).get("model", [])
    rows = [model_row(table, index) for index, table in enumerate(tables, start=1)]
    seen: set[tuple[str, str]] = set()
    for row in rows:
        for setting in row.reasoning:
            if (row.id, setting) in seen:
                raise ValueError(f"model {row.id}: reasoning {setting!r} is listed twice")
            seen.add((row.id, setting))
    return rows


def model_row(table: dict, index: int) -> ModelRow:
    model_id = table.get("id")
    label = f"model {model_id}" if isinstance(model_id, str) else f"model {index}"
    if not isinstance(model_id, str) or not model_id:
        raise ValueError(f"{label}: id must be a non-empty string")
    kind = table.get("kind")
    if kind not in KINDS:
        raise ValueError(f"{label}: kind must be one of {', '.join(KINDS)}, got {kind!r}")
    provider = kind in PROVIDER_KINDS
    prefixed = [k for k in PROVIDER_KINDS if model_id.startswith(f"{k}/")]
    if provider and prefixed != [kind]:
        raise ValueError(f"{label}: a {kind} row's id must start with {kind}/")
    if not provider and prefixed:
        raise ValueError(f"{label}: an llm row's id must not start with {prefixed[0]}/")
    reasoning = reasoning_of(table.get("reasoning"), label, provider)
    max_tokens = table.get("max_tokens")
    if max_tokens is not None and (isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens < 1):
        raise ValueError(f"{label}: max_tokens must be a positive whole number, got {max_tokens!r}")
    released = table.get("released")
    if released is not None and not isinstance(released, date):
        raise ValueError(f"{label}: released must be a date")
    eci = table.get("eci")
    if eci is not None and (isinstance(eci, bool) or not isinstance(eci, int | float)):
        raise ValueError(f"{label}: eci must be a number")
    pilot = table.get("pilot", True)
    if not isinstance(pilot, bool):
        raise ValueError(f"{label}: pilot must be true or false, got {pilot!r}")
    return ModelRow(
        id=model_id,
        kind=cast(Kind, kind),
        reasoning=reasoning,
        reasoning_kind=reasoning_kind_of(table, model_id, label, provider),
        max_tokens=max_tokens,
        released=released,
        eci=None if eci is None else float(eci),
        notes=str(table.get("notes", "")),
        pilot=pilot,
    )


def reasoning_of(value: object, label: str, provider: bool) -> tuple[str, ...]:
    values = (value,) if isinstance(value, str) else tuple(value) if isinstance(value, list) else ()
    if not values:
        raise ValueError(f"{label}: reasoning must be a setting or a list of them")
    for setting in values:
        if provider and setting != "n/a":
            raise ValueError(f"{label}: a provider row's reasoning must be n/a, got {setting!r}")
        if not provider and setting not in REASONING:
            raise ValueError(f"{label}: reasoning must be one of {', '.join(REASONING)}, got {setting!r}")
    return values


def reasoning_kind_of(table: dict, model_id: str, label: str, provider: bool) -> ReasoningKind:
    """n/a for a provider row, else the file's column, else effort for EFFORT_PREFIXES and budget otherwise."""
    column = table.get("reasoning_kind")
    if provider:
        if column is not None:
            raise ValueError(f"{label}: reasoning_kind is set on a provider row")
        return "n/a"
    if column is not None:
        if column not in ("effort", "budget"):
            raise ValueError(f"{label}: reasoning_kind must be effort or budget, got {column!r}")
        return column
    return "effort" if model_id.startswith(EFFORT_PREFIXES) else "budget"


def generate_config(row: ModelRow, reasoning: str) -> GenerateConfig:
    """The shared grid in inspect's terms. Never sets temperature or cache_prompt."""
    if reasoning not in row.reasoning:
        raise ValueError(f"model {row.id} does not list reasoning {reasoning!r}")
    settings: dict[str, object] = {}
    if row.max_tokens is not None:
        settings["max_tokens"] = row.max_tokens
    if reasoning == "off":
        settings["reasoning_effort"] = "none"  # the explicit off, for both kinds: a budget of 0 is not off
    elif reasoning in BUDGETS:
        if row.reasoning_kind == "budget":
            settings["reasoning_tokens"] = BUDGETS[reasoning]
        else:
            settings["reasoning_effort"] = reasoning
    return GenerateConfig(**settings)  # type: ignore[arg-type]
