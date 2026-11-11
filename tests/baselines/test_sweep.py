"""BP7, BP8 and BP14, which play a thousand seeds. Run with `uv run pytest -m sweep`.

See docs/specs/baselines/tests.md#three-sizes. The default run and CI skip them.
"""

import dataclasses

import numpy as np
import pytest

from paranoid.baselines import POLICIES, complacent, discerning, uniform
from paranoid.engine import SCENARIOS, make_timeline, play

pytestmark = pytest.mark.sweep

SEEDS = range(1000)


def pooled(policy, config) -> float:
    """Mean output per round over every seed."""
    return float(np.mean([r.output for seed in SEEDS for r in play(policy, make_timeline(config, seed)).rows]))


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_bp7_baseline_order(name):
    config = SCENARIOS[name]
    output = {key: pooled(POLICIES[key](), config) for key in POLICIES if key != "bayesian"}
    assert output["perfect"] >= output["discerning"] >= output["complacent"]
    if name == "down_switch":
        assert output["discerning"] > output["complacent"]
    assert all(output["uniform"] < value for key, value in output.items() if key != "uniform")


def test_bp8_uniform_is_the_mean_level():
    config = SCENARIOS["no_change"]
    mean_level = np.mean([make_timeline(config, seed).levels for seed in SEEDS])
    assert pooled(uniform, config) == pytest.approx(mean_level, rel=1e-3)


def test_bp14_pinning_keeps_the_switch_gap():
    gaps = []
    for own_scale in (2.0, 4.0, 8.0):
        config = dataclasses.replace(SCENARIOS["down_switch"], own_scale=own_scale, pin_in_level_points=True)
        gaps.append(pooled(discerning, config) - pooled(complacent, config))
    assert max(gaps) - min(gaps) <= 0.05 * np.mean(gaps), gaps
