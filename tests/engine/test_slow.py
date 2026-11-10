"""ET6, ET7, ET17 and ET30, which run a thousand seeds or more. Run with `-m slow`.

See docs/specs/engine/tests.md#timeline. The tolerances are first guesses.
"""

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, make_timeline

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def calm():
    config = SCENARIOS["no_change"]
    timelines = [make_timeline(config, seed) for seed in range(2000)]
    weather = np.stack([t.weather for t in timelines])  # (seeds, rounds, channels)
    factor = np.stack([t.factor for t in timelines])  # (seeds, rounds)
    return config, weather, factor


@pytest.mark.parametrize("round", [1, 10, 40])
def test_et6_weather_sd(calm, round):
    config, weather, factor = calm
    assert weather[:, round - 1, :].std() == pytest.approx(config.own_scale, rel=0.05)
    assert factor[:, round - 1].std() == pytest.approx(config.factor_scale, rel=0.10)


@pytest.mark.parametrize("round", [1, 10, 39])
def test_et7_persistence(calm, round):
    config, weather, _ = calm
    now, next_ = weather[:, round - 1, :].ravel(), weather[:, round, :].ravel()
    assert np.corrcoef(now, next_)[0, 1] == pytest.approx(config.persistence, abs=0.05)


def test_et17_riser_share():
    config = SCENARIOS["down_switch"]
    risen = [make_timeline(config, seed).sleeper is not None for seed in range(1000)]
    assert np.mean(risen) == pytest.approx(config.events[0].riser_share, abs=0.05)


def test_et30_short_share():
    config = SCENARIOS["up_switch"]
    shorts = [make_timeline(config, seed).events[0].numbers["short"] for seed in range(1000)]
    assert np.mean(shorts) == pytest.approx(config.events[0].short_share, abs=0.05)
    for name in ("up_switch_then_down_switch", "down_switch"):
        for seed in range(1000):
            for event in make_timeline(SCENARIOS[name], seed).events:
                assert event.numbers["short"] == 0
