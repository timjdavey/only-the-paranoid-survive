"""Off draws today: ET39. See docs/specs/engine/tests.md#timeline."""

import hashlib

import numpy as np

from paranoid.engine import SCENARIOS, make_timeline

# Pinned before the shape knobs existed. Changing it is a reviewed change, see ET39.
LEVELS_HASH = "aa7ad96e2061b38a"


def levels_hash() -> str:
    """SHA-256 of `levels` on seeds 0 to 9 of every scenario, rounded to 9 places so a last-bit wobble across CPUs passes."""
    digest = hashlib.sha256()
    for config in SCENARIOS.values():
        for seed in range(10):
            digest.update(np.round(make_timeline(config, seed).levels, 9).tobytes())
    return digest.hexdigest()[:16]


def test_et39_off_draws_today():
    assert levels_hash() == LEVELS_HASH
