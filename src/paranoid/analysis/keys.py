"""Setting, ResultKey and result_key: what was played and who played it. See docs/specs/analysis/runs.md#result-key.

Also the reasoning read back from a log, the guards on what a log says about itself, and how two settings are
compared, which is every field but `harness_version`.
"""

import re
from dataclasses import dataclass, fields, replace
from typing import Any, Literal

import pandas as pd
from inspect_ai.log import EvalLog

from paranoid.harness import BUDGETS, REASONING

PROVIDER_PREFIXES = ("baseline/", "jev/", "timestral/")
SKIN_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/-]*$")
SEED_SETS = ("public", "held-out")
TOOL_CHOICES = ("any", "auto")
UNCOMPARED = "harness_version"  # left out whenever two settings are compared, see #comparing-settings


@dataclass(frozen=True)
class Setting:
    """What was played, apart from who played it."""

    skin: str
    seed_set: Literal["public", "held-out"]
    own_scale: float | None  # None means the frozen default
    game_rounds: int  # the metadata's `rounds`, the game length
    tools: str
    warm_up: str | None
    rolling: bool
    tool_choice: Literal["any", "auto"] | None  # None only when no sample reached round 1
    inertia: int | None
    prompt_hash: str
    generator_version: int
    harness_version: str
    release: str


@dataclass(frozen=True)
class ResultKey:
    model: str  # the inspect model string
    reasoning: str  # one of REASONING, "n/a" for a provider, or "unknown"
    setting: Setting


SETTING_FIELDS: tuple[str, ...] = tuple(field.name for field in fields(Setting))
KEY_COLUMNS: tuple[str, ...] = ("model", "reasoning", *SETTING_FIELDS)
METADATA_NAME = {"game_rounds": "rounds"}  # a Setting field whose metadata key is not its own name
CASTS: dict[str, type] = {"own_scale": float, "game_rounds": int, "rolling": bool, "inertia": int, "generator_version": int}


def is_provider(model: str) -> bool:
    return model.startswith(PROVIDER_PREFIXES)


def kind_of(log: EvalLog) -> str:
    """The eval metadata's `kind`, else the provider prefix, else llm."""
    kind = (log.eval.metadata or {}).get("kind")
    if kind:
        return str(kind)
    model = log.eval.model
    return model.split("/")[0] if is_provider(model) else "llm"


def reasoning_of(log: EvalLog) -> str:
    """The setting the log played: its metadata, else n/a for a provider, else read back from the config."""
    written = (log.eval.metadata or {}).get("reasoning")
    if written:
        return str(written)
    if is_provider(log.eval.model):
        return "n/a"
    config = log.eval.model_generate_config
    effort = getattr(config, "reasoning_effort", None)
    if effort is not None:
        effort = "off" if effort == "none" else str(effort)
        return effort if effort in REASONING else "unknown"
    tokens = getattr(config, "reasoning_tokens", None)
    if tokens is not None:  # a budget of 0 is not off, so it reads unknown like any other off the table
        return next((name for name, budget in BUDGETS.items() if budget == tokens), "unknown")
    return "unknown"


def guard_model(model: str, where: str) -> None:
    if not MODEL_NAME.match(model) or ".." in model:
        raise ValueError(f"{where}: model {model!r} is not a model string this layer can name a file after")


def setting_of(log: EvalLog, where: str) -> Setting:
    """Every field from the samples' metadata. Samples that disagree, or lack a field, raise ValueError."""
    values: dict[str, Any] = {}
    for name in SETTING_FIELDS:
        key = METADATA_NAME.get(name, name)
        seen: set[Any] = set()
        for sample in log.samples or []:
            metadata = sample.metadata or {}
            if key not in metadata:
                if name == "tool_choice":  # the solver's, written in round 1, so an early error lacks it
                    continue
                raise ValueError(f"{where}: sample {sample.id} has no {key!r} in its metadata")
            seen.add(metadata[key])
        if len(seen) > 1:
            raise ValueError(f"{where}: the samples disagree on {name}: {', '.join(sorted(map(repr, seen)))}")
        value = next(iter(seen), None)
        values[name] = None if value is None else CASTS.get(name, str)(value)
    setting = Setting(**values)
    guard_setting(setting, where)
    return setting


def guard_setting(setting: Setting, where: str) -> None:
    if not SKIN_NAME.match(setting.skin):
        raise ValueError(f"{where}: skin {setting.skin!r} is not a skin name")
    if setting.seed_set not in SEED_SETS:
        raise ValueError(f"{where}: seed_set must be public or held-out, got {setting.seed_set!r}")
    if setting.tool_choice is not None and setting.tool_choice not in TOOL_CHOICES:
        raise ValueError(f"{where}: tool_choice must be any or auto, got {setting.tool_choice!r}")


def result_key(log: EvalLog) -> ResultKey:
    """The log's key, from `log.eval` and the samples' metadata alone."""
    where = f"log {log.location}"
    guard_model(log.eval.model, where)
    return ResultKey(model=log.eval.model, reasoning=reasoning_of(log), setting=setting_of(log, where))


def compared(setting: Setting) -> Setting:
    """The setting as two settings are compared: without harness_version."""
    return replace(setting, harness_version="")


def differing(a: Setting, b: Setting) -> list[str]:
    """The compared fields in which two settings differ, in field order."""
    return [name for name in SETTING_FIELDS if name != UNCOMPARED and getattr(a, name) != getattr(b, name)]


def cell(value: Any) -> Any:
    """A table cell as a key value: NA is None, numpy scalars are Python ones."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    return value.item() if hasattr(value, "item") else value


def key_of(row: Any) -> ResultKey:
    """The ResultKey of a run table row, or of a mapping of the key columns."""
    values = {name: cell(row[name]) for name in SETTING_FIELDS}
    values = {name: None if v is None else CASTS.get(name, str)(v) for name, v in values.items()}
    return ResultKey(model=str(row["model"]), reasoning=str(row["reasoning"]), setting=Setting(**values))


def key_values(key: ResultKey) -> dict[str, Any]:
    return {"model": key.model, "reasoning": key.reasoning} | {name: getattr(key.setting, name) for name in SETTING_FIELDS}


def keys_in(runs: pd.DataFrame) -> list[ResultKey]:
    """Every result row in the table, in the order it first appears."""
    if runs.empty:
        return []
    firsts = runs.drop_duplicates(subset=list(KEY_COLUMNS))
    return [key_of(row) for _, row in firsts.iterrows()]


def mask_of(runs: pd.DataFrame, key: ResultKey) -> pd.Series:
    """The rows of one result row. NA in a column matches a None in the key."""
    mask = pd.Series(True, index=runs.index)
    for name, value in key_values(key).items():
        column = runs[name]
        mask &= column.isna() if value is None else (column == value).fillna(False).astype(bool)
    return mask


def rows_of(runs: pd.DataFrame, key: ResultKey) -> pd.DataFrame:
    return runs[mask_of(runs, key)]


def label(key: ResultKey) -> str:
    """The model string, then the reasoning setting in parentheses when it is not n/a."""
    return key.model if key.reasoning == "n/a" else f"{key.model} ({key.reasoning})"
