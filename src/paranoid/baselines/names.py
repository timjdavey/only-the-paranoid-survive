"""POLICIES, the seven baseline/<name> names the harness plays. See docs/specs/baselines/policies.md#policies."""

from collections.abc import Callable, Mapping
from types import MappingProxyType

from paranoid.engine import Policy

from .bayesian import Bayesian
from .policies import Complacent, Discerning, Perfect, Uniform
from .rules import HedgeRule, ScoutRule

POLICIES: Mapping[str, Callable[..., Policy]] = MappingProxyType(
    {
        "uniform": Uniform,
        "discerning": Discerning,
        "complacent": Complacent,
        "perfect": Perfect,
        "hedge_rule": HedgeRule,
        "scout_rule": ScoutRule,
        "bayesian": Bayesian,
    }
)
