"""The timestral cell: the gap test, determinism, and the policies on the noise grid. Not an eval.

See docs/specs/harness/pilot.md#timestral. It plays the forecasters layer's policies with the engine,
as an engine cell plays a baseline, so it needs no task and no Docker.
"""

from pathlib import Path

import numpy as np

from paranoid.baselines import uniform
from paranoid.engine import SCENARIOS, Game, make_timeline, play
from paranoid.forecasters import TIMESTRAL_POLICIES, Forecaster, ForecastPolicy, Timestral, require_timestral
from paranoid.forecasters import timestral as joint_timestral

from ..config import scenario_config
from ..seeds import load_grid, load_seeds
from .common import CellArgs, output, seed_cap, write_csv
from .evals import rows_of

GAPS = 30
GRID_SCENARIOS = ("one_shock", "down_switch", "up_switch")


def shapes() -> list[tuple[int, Forecaster]]:
    """The two input shapes the probes run on, as (joint, forecaster)."""
    return [(1, joint_timestral), (0, Timestral(joint=False))]


def policy_for(model_id: str) -> ForecastPolicy:
    return TIMESTRAL_POLICIES[model_id.split("/", 1)[1]]


def extra_missing() -> bool:
    try:
        require_timestral()
    except ImportError:
        return True
    return False


def probes():
    """The gap test and determinism, on the first ten rounds of uniform on One shock."""
    record = play(uniform, make_timeline(SCENARIOS["one_shock"], load_seeds("public")[0]), max_rounds=10)
    ten = np.array([[np.nan if r is None else r for r in row.readings] for row in record.rows], dtype=float)
    readings = np.vstack([ten, np.full((GAPS, ten.shape[1]), np.nan)])
    for joint, forecaster in shapes():
        for gap in range(1, GAPS + 1):
            quantiles = np.asarray(forecaster(readings[: 10 + gap], None))
            for channel, spread in enumerate(quantiles[:, -1] - quantiles[:, 0]):
                yield "gap", joint, gap, channel, float(spread), None
        equal = np.array_equal(np.asarray(forecaster(ten, None)), np.asarray(forecaster(ten, None)))
        yield "determinism", joint, None, None, None, int(equal)


def timestral(args: CellArgs) -> list[Path]:
    rows = rows_of(args, "timestral")
    if extra_missing():
        print("timestral: the timestral extra is not installed, run `uv sync --extra timestral`. Nothing written")
        return []
    seeds = list(enumerate(load_seeds("public")[: seed_cap(20)]))
    grid_runs: list[tuple] = []
    rounding: list[tuple] = []

    def play_grid() -> None:
        for row in rows:
            policy = policy_for(row.id)
            for setting in load_grid().own_scale:
                for name in GRID_SCENARIOS:
                    config = scenario_config(name, own_scale=setting)
                    for position, seed in seeds:
                        game = Game(make_timeline(config, seed))
                        while not game.done:
                            view = game.view(False)
                            rounding.append((setting, row.id, name, position, game.round, policy.rounded_out(view)))
                            game.play(policy(view))
                        grid_runs.append((setting, name, row.id, seed, output(game.record)))

    def grid():
        play_grid()
        return grid_runs

    paths = write_csv(args, "timestral", ("probe", "joint", "gap", "channel", "spread", "equal"), probes)
    paths += write_csv(args, "timestral-grid", ("setting", "scenario", "model", "seed", "output"), grid)
    columns = ("setting", "model", "scenario", "seed_index", "round", "rounded_out")
    return paths + write_csv(args, "timestral-rounding", columns, lambda: rounding)
