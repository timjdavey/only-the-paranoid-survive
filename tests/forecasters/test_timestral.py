"""FT1 to FT7, see docs/specs/forecasters/tests.md#timestral.

FT4 to FT7 load the real model: `uv sync --extra timestral`, then `uv run pytest -m timestral`.
"""

import subprocess
import sys

import numpy as np
import pytest

from paranoid.baselines import QUANTILE_LEVELS, uniform
from paranoid.engine import SCENARIOS, make_timeline, play
from paranoid.forecasters import (
    TIMESTRAL_MODEL,
    TIMESTRAL_POLICIES,
    TIMESTRAL_REVISION,
    Timestral,
    require_timestral,
    timestral,
)

SHAPES = (Timestral(), Timestral(joint=False))


@pytest.fixture(scope="module")
def ten() -> np.ndarray:
    """Ten rounds of readings on every channel, (10, channels)."""
    record = play(uniform, make_timeline(SCENARIOS["one_shock"], 0), max_rounds=10)
    return np.array([row.readings for row in record.rows], dtype=float)


def spread(quantiles: np.ndarray) -> np.ndarray:
    return quantiles[:, -1] - quantiles[:, 0]


def test_ft1_importing_the_layer_imports_no_model():
    code = "import sys, paranoid.forecasters; print(int('torch' in sys.modules or 'timestral' in sys.modules))"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "0"


def test_ft2_a_missing_extra_names_itself(monkeypatch, ten):
    for name in ("torch", "timestral"):
        monkeypatch.setitem(sys.modules, name, None)
    with pytest.raises(ImportError, match="uv sync --extra timestral"):
        require_timestral()
    with pytest.raises(ImportError, match="uv sync --extra timestral"):
        Timestral()(ten, None)


def test_ft3_shapes_and_keys(ten):
    with pytest.raises(ValueError, match="joint"):
        Timestral(joint=True)(ten, np.full(ten.shape, 10.0))
    assert timestral == Timestral()
    assert timestral.key == f"{TIMESTRAL_MODEL}@{TIMESTRAL_REVISION}/joint"
    keys = {
        timestral.key,
        Timestral(joint=False).key,
        Timestral(model="mistralai/Timestral-5M").key,
        Timestral(revision="main").key,
    }
    assert len(keys) == 4


@pytest.mark.timestral
@pytest.mark.parametrize("forecaster", SHAPES, ids=("joint", "separate"))
def test_ft4_the_real_forecast(forecaster, ten):
    quantiles = forecaster(ten, None)
    assert quantiles.shape == (ten.shape[1], len(QUANTILE_LEVELS)) and quantiles.dtype == np.float64
    assert np.isfinite(quantiles).all() and (np.diff(quantiles, axis=1) >= 0).all()
    assert np.array_equal(quantiles, forecaster(ten, None))


@pytest.mark.timestral
@pytest.mark.parametrize("forecaster", SHAPES, ids=("joint", "separate"))
def test_ft5_the_gap_test(forecaster, ten):
    blanks = np.full((30, ten.shape[1]), np.nan)
    after_one = spread(forecaster(np.vstack([ten, blanks[:1]]), None))
    after_thirty = spread(forecaster(np.vstack([ten, blanks]), None))
    assert (after_thirty > after_one).all()


@pytest.mark.timestral
def test_ft6_bets_move_a_forecast_of_each_channel_alone(ten):
    bets = np.full(ten.shape, 5.0)
    bets[:, 0] = 55.0
    separate = Timestral(joint=False)
    assert not np.allclose(separate(ten, bets), separate(ten, None))


@pytest.mark.timestral
def test_ft7_a_whole_run(check_split):
    timeline = make_timeline(SCENARIOS["one_shock"], 0)
    record = play(TIMESTRAL_POLICIES["top-pick"], timeline)
    assert len(record) == timeline.config.rounds
    for row in record.rows:
        check_split(row.bets)
    assert play(TIMESTRAL_POLICIES["top-pick"], timeline) == record
