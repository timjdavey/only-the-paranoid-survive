"""The game with no story. See docs/specs/engine/README.md."""

from .config import GENERATOR_VERSION, ScenarioConfig, engine_hash
from .scenarios import SCENARIOS
from .specs import DriftSpec, ShockSpec, SwitchSpec

__all__ = [
    "ScenarioConfig",
    "ShockSpec",
    "SwitchSpec",
    "DriftSpec",
    "SCENARIOS",
    "engine_hash",
    "GENERATOR_VERSION",
]
