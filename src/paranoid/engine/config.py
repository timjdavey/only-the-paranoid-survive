"""ScenarioConfig, its validation and engine_hash. See docs/specs/engine/config.md."""

import dataclasses
import hashlib
import json
from dataclasses import dataclass

from .specs import (
    SHAPES,
    EventSpec,
    IntRange,
    Range,
    ShockSpec,
    SwitchSpec,
    as_int,
    cast_fields,
    require,
)

# Bumped whenever make_timeline changes what it produces for a config it already accepted.
GENERATOR_VERSION = 1


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    # shape
    channels: int = 10
    rounds: int = 40
    budget: int = 100
    # ladder, in level points unless the name says sigmas
    leader_base: Range = (90.0, 100.0)
    runner_up_gap_sigmas: Range = (2.0, 4.0)
    runner_up_gap_points: Range = (8.0, 16.0)
    field_base: Range = (60.0, 85.0)
    field_headroom: float = 4.0
    hedge_base: Range = (50.0, 58.0)
    # weather
    own_scale: float = 4.0
    persistence: float = 0.8
    factor_scale: float = 3.0
    loading: Range = (0.3, 1.0)
    hedge_loading: Range = (-0.6, -0.3)
    # what the agent sees
    read_noise_k: float = 8.0
    # events
    events: tuple[EventSpec, ...] = ()
    onset: IntRange = (8, 12)
    pin_in_level_points: bool = False
    hedge_margin_points: float = 4.0
    # hard-variant knobs
    hedge_may_overtake: bool = False
    one_channel_shock: bool = False
    inertia_cap: int | None = None

    def __post_init__(self) -> None:
        self._cast()
        self._check_shape()
        self._check_weather()
        self._check_ladder()
        self._check_events()

    def _cast(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError(f"name must be a str, got {self.name!r}")
        cast_fields(self)
        if self.inertia_cap is not None:
            object.__setattr__(self, "inertia_cap", as_int(self.inertia_cap, "inertia_cap"))
        try:
            events = tuple(self.events)
        except TypeError:
            raise TypeError(f"events must be a sequence of event specs, got {self.events!r}") from None
        for spec in events:
            if type(spec) not in SHAPES:
                raise TypeError(f"events must hold event specs only, got {spec!r}")
        object.__setattr__(self, "events", events)

    def _check_shape(self) -> None:
        require(self.channels >= 4, "channels must be at least 4")
        require(self.rounds >= 1, "rounds must be at least 1")
        require(self.budget >= self.channels, "budget must be at least channels")
        require(self.inertia_cap is None or self.inertia_cap >= 0, "inertia_cap must not be negative")

    def _check_weather(self) -> None:
        require(0.0 <= self.persistence < 1.0, "persistence must be inside [0, 1)")
        for name in ("own_scale", "factor_scale", "read_noise_k", "field_headroom", "hedge_margin_points"):
            require(getattr(self, name) > 0, f"{name} must be positive")
        require(self.loading[0] > 0, "loading must have a low above 0")
        require(self.hedge_loading[1] < 0, "hedge_loading must have a high below 0")

    def _check_ladder(self) -> None:
        require(self.runner_up_gap_sigmas[0] > 0, "runner_up_gap_sigmas must have a low above 0")
        require(self.runner_up_gap_points[0] > 0, "runner_up_gap_points must have a low above 0")
        require(self.onset[0] >= 2, "onset must have a low of at least 2")
        require(self.onset[1] <= self.rounds, "onset must have a high of at most rounds")
        require(self.hedge_base[1] < self.field_base[0], "hedge_base must lie below field_base")
        top = self.leader_base[0] - self._widest_gap() - self.field_headroom
        require(
            self.field_base[0] <= top,
            f"field_base low {self.field_base[0]} is above {top}, so a field channel could pass the runner-up",
        )

    def _widest_gap(self) -> float:
        """The widest runner-up gap the engine can draw, from the pair it reads."""
        if self.pin_in_level_points:
            return self.runner_up_gap_points[1]
        return self.runner_up_gap_sigmas[1] * self.own_scale

    def _check_events(self) -> None:
        last_switch: SwitchSpec | None = None
        for index, spec in enumerate(self.events):
            if shape_knob_on(spec) and (self.one_channel_shock or self.hedge_may_overtake):
                raise ValueError("a shape knob cannot be on with one_channel_shock or hedge_may_overtake")
            if isinstance(spec, SwitchSpec):
                if spec.kind == "undo":
                    require(index > 0, "an undo cannot be the first event")
                    require(
                        last_switch is not None and last_switch.kind in ("rise", "fall_and_rise"),
                        "an undo needs a 'rise' or 'fall_and_rise' switch before it",
                    )
                last_switch = spec


def shape_knob_on(spec: EventSpec) -> bool:
    """A storm on a switch, or any shape knob on a shock."""
    if isinstance(spec, SwitchSpec):
        return spec.storm is not None
    return isinstance(spec, ShockSpec) and spec.knobs_on


def canonical_json(config: ScenarioConfig) -> str:
    """The string engine_hash hashes, see docs/specs/engine/config.md#engine-hash."""
    d = dataclasses.asdict(config)
    for event_dict, spec in zip(d["events"], config.events, strict=True):
        event_dict["shape"] = SHAPES[type(spec)]
    d["generator_version"] = GENERATOR_VERSION
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def engine_hash(config: ScenarioConfig) -> str:
    """The first 12 hex characters of the SHA-256 of the config's canonical JSON."""
    return hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest()[:12]
