"""Every fixed baseline as a pure policy. See docs/specs/baselines/README.md."""

from .policies import complacent, discerning, perfect, uniform

__all__ = [
    "uniform",
    "discerning",
    "complacent",
    "perfect",
]
