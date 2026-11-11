"""The eight scenarios, by code name. See docs/specs/engine/config.md#scenarios."""

from collections.abc import Mapping
from types import MappingProxyType

from .config import ScenarioConfig
from .specs import DriftSpec, EventSpec, ShockSpec, SwitchSpec

_EVENTS: dict[str, tuple[EventSpec, ...]] = {
    "no_change": (),
    "one_shock": (ShockSpec(),),
    "down_switch": (SwitchSpec(kind="draw"),),
    "up_switch": (SwitchSpec(kind="rise", short_share=0.25),),
    "shock_then_switch": (ShockSpec(), SwitchSpec(kind="draw")),
    "slow_drift": (DriftSpec(),),
    "switch_then_shock": (SwitchSpec(kind="draw"), ShockSpec()),
    "up_switch_then_down_switch": (SwitchSpec(kind="rise"), SwitchSpec(kind="undo")),
}

# Read only, in the order of the spec's table, which the harness and analysis rely on.
SCENARIOS: Mapping[str, ScenarioConfig] = MappingProxyType(
    {name: ScenarioConfig(name=name, events=events) for name, events in _EVENTS.items()}
)
