"""The pilot cells, one function per cell. See docs/specs/harness/pilot.md.

An engine cell plays timelines and fixed baselines with no model and writes a CSV.
A provider cell plays a model through the task and leaves eval logs.
"""

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from .common import Cell, CellArgs, seed_cap
from .order import baseline_order
from .sweeps import bayesian_frontier, game_length, reading_roughness, up_and_down
from .weather import luck, noise_grid, streaks, tell, timeline_sanity

RECOGNITION_QUESTION = "Where does this text come from, and what is it for?"
CHANNEL_ORDER_REQUEST = "Send exactly this now: {split}. Every one not named gets 0."
ALL_BETS = (29, 19, 14, 11, 9, 7, 5, 3, 2, 1)  # ten different bets that sum to 100

# Read only, in page order.
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
    }
)


def run_cell(name: str, args: CellArgs) -> list[Path]:
    """Runs one cell and returns the paths it wrote."""
    if name not in CELLS:
        raise ValueError(f"unknown pilot check {name!r}, the checks are {', '.join(CELLS)}")
    return CELLS[name](args)



