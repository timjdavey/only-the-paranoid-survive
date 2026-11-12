"""The two worlds the shapes are drawn and scored in. See shapes/README.md#today-and-new.

TODAY is the engine's eight scenarios as they ship. NEW is the same eight with the shape knobs on and rougher
small bets. This file is the one place the on values live until a pilot moves them into the scenarios.
"""

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from paranoid.engine import SCENARIOS, ScenarioConfig, ShockSpec, SwitchSpec

KNOBS = dict(recovery=(0.5, 1.5), leader_last_share=0.5, pop_share=0.5, leader_stays_ahead=True)
READ_NOISE_K = 12.0  # small bets get rougher. Today's is 8
FALLS = ("fall", "fall_and_rise", "draw")  # the kinds that carry a storm. A rise and an undo stay quiet


def turn_on(spec):
    """Every shock gets the knobs. Every switch that falls arrives in the scenario's shock, knobs on."""
    if isinstance(spec, ShockSpec):
        return replace(spec, **KNOBS)
    if isinstance(spec, SwitchSpec) and spec.kind in FALLS:
        return replace(spec, storm=ShockSpec(**KNOBS))
    return spec


def new_world(config: ScenarioConfig) -> ScenarioConfig:
    return replace(config, read_noise_k=READ_NOISE_K, events=tuple(turn_on(spec) for spec in config.events))


TODAY: Mapping[str, ScenarioConfig] = SCENARIOS
NEW: Mapping[str, ScenarioConfig] = MappingProxyType({name: new_world(config) for name, config in SCENARIOS.items()})
WORLDS = {"today": TODAY, "new": NEW}
CHANGED = tuple(name for name in SCENARIOS if NEW[name].events != TODAY[name].events)  # the four the knobs change
