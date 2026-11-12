"""The event specs, and the casts and checks every config field goes through.

See docs/specs/engine/config.md#fields.
"""

import math
import numbers
from dataclasses import dataclass, fields
from typing import Any, Literal

Range = tuple[float, float]  # inclusive low, inclusive high, drawn uniform per seed
IntRange = tuple[int, int]  # inclusive low, inclusive high, drawn uniform per seed


# --- casts -----------------------------------------------------------------


def is_whole(value: Any) -> bool:
    """A whole number is an Integral that is not a bool, as for bets."""
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def is_real(value: Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def as_float(value: Any, name: str) -> float:
    if not is_real(value):
        raise TypeError(f"{name} must be a real number, got {value!r}")
    cast = float(value)
    if not math.isfinite(cast):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return cast


def as_int(value: Any, name: str) -> int:
    if not is_whole(value):
        raise TypeError(f"{name} must be a whole number, got {value!r}")
    return int(value)


def as_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool, got {value!r}")
    return value


def as_pair(value: Any, name: str, cast) -> tuple:
    try:
        pair = tuple(value)
    except TypeError:
        raise TypeError(f"{name} must be a pair, got {value!r}") from None
    if len(pair) != 2:
        raise TypeError(f"{name} must be a pair, got {value!r}")
    low, high = (cast(x, name) for x in pair)
    if low > high:
        raise ValueError(f"{name} has its low above its high: {pair!r}")
    return (low, high)


def as_range(value: Any, name: str) -> Range:
    return as_pair(value, name, as_float)


def as_int_range(value: Any, name: str) -> IntRange:
    return as_pair(value, name, as_int)


# Keyed by the declared type itself. Range and IntRange are two distinct objects.
CASTS = [(Range, as_range), (IntRange, as_int_range), (float, as_float), (int, as_int), (bool, as_bool)]


def cast_fields(obj: Any) -> None:
    """Cast every field of a frozen dataclass whose declared type is in CASTS."""
    for field in fields(obj):
        for declared, cast in CASTS:
            if field.type is declared:
                object.__setattr__(obj, field.name, cast(getattr(obj, field.name), field.name))


# --- checks ----------------------------------------------------------------


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def require_word(value: Any, words: tuple[str, ...], name: str) -> None:
    require(value in words, f"{name} must be one of {words}, got {value!r}")


def require_low_at_least_1(spec: Any, *names: str) -> None:
    for name in names:
        require(getattr(spec, name)[0] >= 1, f"{name} must have a low of at least 1")


def require_positive_sizes(spec: Any) -> None:
    for field in fields(spec):
        if field.name.endswith(("_sigmas", "_points")):
            require(getattr(spec, field.name)[0] > 0, f"{field.name} must have a low above 0")


def require_share(value: float, name: str) -> None:
    require(0.0 <= value <= 1.0, f"{name} must be inside [0, 1], got {value}")


# --- the event specs -------------------------------------------------------

SHOCK_PROFILES = ("sharp", "slide", "draw")
SWITCH_KINDS = ("fall", "fall_and_rise", "rise", "undo", "draw")
DRIFT_PROFILES = ("linear", "logistic", "draw")


@dataclass(frozen=True)
class ShockSpec:
    gap: IntRange = (8, 12)
    depth_sigmas: Range = (4.0, 8.0)
    depth_points: Range = (16.0, 32.0)
    half_life: IntRange = (2, 4)
    profile: Literal["sharp", "slide", "draw"] = "draw"

    def __post_init__(self) -> None:
        cast_fields(self)
        require_word(self.profile, SHOCK_PROFILES, "profile")
        require_low_at_least_1(self, "gap", "half_life")
        require_positive_sizes(self)


@dataclass(frozen=True)
class SwitchSpec:
    gap: IntRange = (8, 12)
    kind: Literal["fall", "fall_and_rise", "rise", "undo", "draw"] = "draw"
    riser_share: float = 0.5
    size_sigmas: Range = (1.0, 3.0)
    size_points: Range = (4.0, 12.0)
    rise_sigmas: Range = (3.0, 6.0)
    rise_points: Range = (12.0, 24.0)
    ramp: IntRange = (1, 5)
    short_share: float = 0.0
    short_level: Range = (0.25, 0.75)

    def __post_init__(self) -> None:
        cast_fields(self)
        require_word(self.kind, SWITCH_KINDS, "kind")
        require_share(self.riser_share, "riser_share")
        require_share(self.short_share, "short_share")
        require_low_at_least_1(self, "gap", "ramp")
        require_positive_sizes(self)
        require(
            self.short_share == 0 or self.kind == "rise",
            f"short_share above 0 needs kind 'rise', got {self.kind!r}",
        )
        low, high = self.short_level
        require(0 < low and high < 1, "short_level must lie strictly inside (0, 1)")


@dataclass(frozen=True)
class DriftSpec:
    gap: IntRange = (8, 12)
    size_sigmas: Range = (1.0, 3.0)
    size_points: Range = (4.0, 12.0)
    length: IntRange = (15, 25)
    profile: Literal["linear", "logistic", "draw"] = "draw"

    def __post_init__(self) -> None:
        cast_fields(self)
        require_word(self.profile, DRIFT_PROFILES, "profile")
        require_low_at_least_1(self, "gap", "length")
        require_positive_sizes(self)


EventSpec = ShockSpec | SwitchSpec | DriftSpec

SHAPES: dict[type, str] = {ShockSpec: "shock", SwitchSpec: "switch", DriftSpec: "drift"}
