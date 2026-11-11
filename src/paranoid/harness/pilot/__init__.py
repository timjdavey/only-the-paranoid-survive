"""The pilot cells, one function per cell. See docs/specs/harness/pilot.md.

An engine cell plays timelines and fixed baselines with no model and writes a CSV.
A provider cell plays a model through the task and leaves eval logs.
"""

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from .common import Cell, CellArgs, seed_cap
from .evals import bare, jev, rolling, seeds, tool_choice, up_against_down, warm_up
from .order import baseline_order
from .probes import ALL_BETS, CHANNEL_ORDER_REQUEST, RECOGNITION_QUESTION, channel_order, recognition
from .repeats import repeats
from .sweeps import bayesian_frontier, game_length, reading_roughness, up_and_down
from .timestral_cell import timestral
from .weather import luck, noise_grid, streaks, tell, timeline_sanity

# Read only, the twenty-one names in page order.
CELLS: Mapping[str, Cell] = MappingProxyType(
    {
        "streaks": streaks,
        "tell": tell,
        "luck": luck,
        "timeline-sanity": timeline_sanity,
        "noise-grid": noise_grid,
        "game-length": game_length,
        "reading-roughness": reading_roughness,
        "up-and-down": up_and_down,
        "bayesian-frontier": bayesian_frontier,
        "baseline-order": baseline_order,
        "seeds": seeds,
        "repeats": repeats,
        "recognition": recognition,
        "channel-order": channel_order,
        "up-against-down": up_against_down,
        "jev": jev,
        "timestral": timestral,
        "bare": bare,
        "tool-choice": tool_choice,
        "rolling": rolling,
        "warm-up": warm_up,
    }
)


def run_cell(name: str, args: CellArgs) -> list[Path]:
    """Runs one cell and returns the paths it wrote."""
    if name not in CELLS:
        raise ValueError(f"unknown pilot check {name!r}, the checks are {', '.join(CELLS)}")
    return CELLS[name](args)


__all__ = ["CellArgs", "CELLS", "run_cell", "seed_cap", "RECOGNITION_QUESTION", "CHANNEL_ORDER_REQUEST", "ALL_BETS"]
