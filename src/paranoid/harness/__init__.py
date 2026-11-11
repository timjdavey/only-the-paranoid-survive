"""The inspect_ai layer. See docs/specs/harness/README.md#exports."""

from .cli import main
from .config import scenario_config
from .metrics import (
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED,
    TRAITS,
    bootstrap,
    draws_of,
    headline,
    pooled_score,
    retry_share,
    scenario_score,
    tool_use_share,
    weakest_trait,
)
from .pilot import ALL_BETS, CELLS, CHANNEL_ORDER_REQUEST, RECOGNITION_QUESTION, CellArgs, run_cell
from .providers import StoreAPI
from .providers.baseline import BaselineAPI
from .providers.jev import JevAnswer, JevAPI, JevClient
from .providers.timestral import TimestralAPI
from .models import BUDGETS, EFFORT_PREFIXES, REASONING, SKIN_READERS, ModelRow, generate_config, load_models
from .scorer import gain
from .seeds import Grid, load_grid, load_seeds, parse_seeds
from .solver import BLOCK_CACHE_APIS, record_blocks, round_loop, tool_choice_for
from .store import RunStore, StoredRow
from .task import paranoid
from .tools import compute, notes, submit

__all__ = [
    "paranoid",
    "RunStore",
    "StoredRow",
    "load_seeds",
    "parse_seeds",
    "scenario_config",
    "load_grid",
    "Grid",
    "round_loop",
    "tool_choice_for",
    "record_blocks",
    "BLOCK_CACHE_APIS",
    "submit",
    "notes",
    "compute",
    "gain",
    "scenario_score",
    "headline",
    "weakest_trait",
    "retry_share",
    "tool_use_share",
    "pooled_score",
    "bootstrap",
    "draws_of",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_SEED",
    "TRAITS",
    "load_models",
    "ModelRow",
    "generate_config",
    "REASONING",
    "EFFORT_PREFIXES",
    "BUDGETS",
    "SKIN_READERS",
    "StoreAPI",
    "BaselineAPI",
    "JevAPI",
    "TimestralAPI",
    "JevAnswer",
    "JevClient",
    "main",
    "CellArgs",
    "CELLS",
    "run_cell",
    "RECOGNITION_QUESTION",
    "CHANNEL_ORDER_REQUEST",
    "ALL_BETS",
]
