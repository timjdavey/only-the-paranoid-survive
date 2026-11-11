"""Headings, labels and slugs, shared by the page and the plots. See docs/specs/analysis/tables.md#headings-and-file-names.

Every string here is built from guarded strings and numbers, so none holds a path step.
"""

import re
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from paranoid.engine import SCENARIOS

from .keys import ResultKey, Setting, label

GAME_ROUNDS = SCENARIOS["no_change"].rounds  # every scenario's default length
DEFAULTS: dict[str, Any] = {
    "own_scale": None, "game_rounds": GAME_ROUNDS, "tools": "notes,compute", "warm_up": None, "rolling": False,
    "tool_choice": "any", "inertia": None,
}  # fmt: skip
VERSIONS = ("prompt_hash", "generator_version", "release")  # named only where two settings on the page differ
SLUG_RUN = re.compile(r"[^a-z0-9._]+")


def knob(name: str, value: Any) -> str:
    """A knob as a heading names it, such as `tools none` or `rolling`."""
    if name == "rolling":
        return "rolling"
    if name == "game_rounds":
        return f"rounds {value}"
    if name == "prompt_hash":
        return f"prompt_hash {str(value)[:8]}"
    return f"{name} {value}"


def off_default(setting: Setting) -> list[str]:
    """The knobs off their default, in field order, as a heading names them."""
    return [knob(name, getattr(setting, name)) for name, default in DEFAULTS.items() if is_off(setting, name, default)]


def is_off(setting: Setting, name: str, default: Any) -> bool:
    value = getattr(setting, name)
    return value is not None and value != default


def heading(setting: Setting, others: Sequence[Setting] = ()) -> str:
    """The skin, the seed set, every knob off its default, then each version two settings on the page differ in."""
    parts = [setting.skin, setting.seed_set, *off_default(setting)]
    for name in VERSIONS:
        if len({getattr(s, name) for s in (setting, *others)}) > 1:
            parts.append(knob(name, getattr(setting, name)))
    return ", ".join(parts)


def curve_heading(setting: Setting, others: Sequence[Setting] = ()) -> str:
    """The heading of a curve's settings, without its own_scale part."""
    return heading(_without_scale(setting), [_without_scale(s) for s in others])


def _without_scale(setting: Setting) -> Setting:
    return replace(setting, own_scale=None)


def slug(text: str) -> str:
    """Lower case, every run of characters outside [a-z0-9._] as one `-`, none at either end."""
    return SLUG_RUN.sub("-", text.lower()).strip("-")


def row_label(key: ResultKey, versioned: bool = False) -> str:
    """The Model cell. `versioned` ends it with the harness version, for two rows that differ in nothing else."""
    return f"{label(key)} at {key.setting.harness_version}" if versioned else label(key)
