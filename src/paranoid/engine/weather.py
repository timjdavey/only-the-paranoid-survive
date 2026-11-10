"""Own weather, the shared factor and read noise.

See docs/specs/engine/timeline.md#weather-and-the-shared-factor and #read-noise.
"""

import math

import numpy as np

from .config import ScenarioConfig


def ar1(eps: np.ndarray, persistence: float) -> np.ndarray:
    """z[0] = eps[0], z[t] = p·z[t−1] + sqrt(1 − p²)·eps[t], so the SD is 1 at every row."""
    innovation = math.sqrt(1.0 - persistence * persistence)
    z = np.empty_like(eps)
    z[0] = eps[0]
    for t in range(1, len(eps)):
        z[t] = persistence * z[t - 1] + innovation * eps[t]
    return z


def draw_weather(rng: np.random.Generator, config: ScenarioConfig) -> np.ndarray:
    eps = rng.standard_normal((config.rounds, config.channels))
    return config.own_scale * ar1(eps, config.persistence)


def draw_factor(rng: np.random.Generator, config: ScenarioConfig) -> np.ndarray:
    """The shared factor before any shock impulse is added."""
    eps = rng.standard_normal(config.rounds)
    return config.factor_scale * ar1(eps, config.persistence)


def draw_read_noise(rng: np.random.Generator, config: ScenarioConfig) -> np.ndarray:
    return rng.standard_normal((config.rounds, config.channels))
