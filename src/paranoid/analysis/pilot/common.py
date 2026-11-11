"""What every pilot section shares: reading a cell's CSV or logs, pooling an engine CSV, and a section's parts.

See docs/specs/analysis/pilot.md#reading-the-inputs.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from paranoid.harness import pooled_score

from ..runs import load_runs, mean_over_epochs

# Each cell's columns, as its Writes line in docs/specs/harness/pilot.md names them. AI23 holds these to the page.
CELL_COLUMNS: dict[str, tuple[str, ...]] = {
    "streaks": ("setting", "scenario", "seed", "onset", "leader_below_streak", "rounds_to_separate", "field_beats_leader_streak"),
    "tell": ("factor_scale", "loading_low", "window", "fall_points", "tell_points", "scenario", "seed", "onset",
             "depth_capped", "hedge_rise", "held", "move_round", "fall_rounds", "tell_rounds", "field_together_rounds"),
    "luck": ("setting", "seed", "perfect", "discerning", "uniform"),
    "timeline-sanity": ("setting", "scenario", "seed", "below_zero_rounds", "below_zero_readings", "discerning", "complacent"),
    "timeline-sanity-sparklines": ("scenario", "round", "median", "p10", "p90"),
    "noise-grid": ("setting", "scenario", "baseline", "seed", "size", "output"),
    "game-length": ("rounds", "onset_low", "onset_high", "gap_low", "gap_high", "scenario", "seed", "onset_1", "onset_2",
                    "last_end", "baseline", "output", "output_window_1", "output_window_2", "clear_round_1",
                    "clear_round_2", "move_round"),
    "reading-roughness": ("setting", "scenario", "baseline", "parameter", "scout_rounds", "seed", "output", "move_round"),
    "up-and-down": ("setting", "scenario", "kind", "baseline", "parameter", "seed", "onset", "output", "move_round"),
    "bayesian-frontier": ("scenario", "baseline", "hazard", "rule", "seed", "output"),
    "baseline-order": ("scenario", "kind", "baseline", "seed", "output", "move_round"),
    "seeds-tokens": ("model", "rolling", "scenario", "seed_index", "round", "input_tokens", "cache_read_tokens",
                     "cache_write_tokens"),
    "rolling-tokens": ("model", "rolling", "scenario", "seed_index", "round", "input_tokens", "cache_read_tokens",
                       "cache_write_tokens"),
    "recognition": ("model", "skin", "probe", "reply", "lint_hits", "canary_finished"),
    "channel-order": ("model", "skin", "shape", "probe", "called", "valid", "matched", "slipped", "wanted", "sent"),
    "jev": ("model", "scenario", "seed_index", "round", "rounded_out"),
    "timestral": ("probe", "joint", "gap", "channel", "spread", "equal"),
    "timestral-grid": ("setting", "scenario", "model", "seed", "output"),
    "timestral-rounding": ("setting", "model", "scenario", "seed_index", "round", "rounded_out"),
}  # fmt: skip
SWITCH_OR_DRIFT = ("down_switch", "up_switch", "shock_then_switch", "slow_drift", "switch_then_shock", "up_switch_then_down_switch")
BLIND = ("hedge_rule", "scout_rule", "bayesian")
BOTH_WAYS = "up_switch_then_down_switch"  # where the Stayer stands in for the Complacent baseline


@dataclass
class Section:
    """A section's tables and plots, in the order the page shows them, and any line under them."""

    tables: list[tuple[str, pd.DataFrame]] = field(default_factory=list)
    plots: list[tuple[str, Callable[[Path], Path]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def table(self, name: str, frame: pd.DataFrame | None) -> None:
        if frame is not None and len(frame):
            self.tables.append((name, frame.reset_index(drop=True)))

    def plot(self, name: str, draw: Callable[[Path], Path]) -> None:
        self.plots.append((name, draw))

    @property
    def empty(self) -> bool:
        return not self.tables and not self.plots and not self.notes


Builder = Callable[[Path, Path | None], Section | None]  # (logs, main) to a section, or None when no input exists


def read_csv(logs: Path, name: str) -> pd.DataFrame | None:
    """`<logs>/<name>.csv` with exactly its cell's columns, or None when the cell has not run."""
    path = logs / f"{name}.csv"
    if not path.exists():
        return None
    frame = pd.read_csv(path, keep_default_na=True)
    wanted = CELL_COLUMNS[name]
    odd = [c for c in frame.columns if c not in wanted] + [c for c in wanted if c not in frame.columns]
    if odd:
        raise ValueError(f"{path} has columns its cell does not write: {', '.join(map(str, odd))}")
    if name == "recognition":
        frame = frame.drop(columns="reply")  # never held, see load_recognition
    return frame


def read_cell(logs: Path, cell: str, *, per_epoch: bool = False) -> pd.DataFrame | None:
    """The run table of `<logs>/<cell>/`, loaded on its own, or None when it holds no log."""
    folder = logs / cell
    if not folder.is_dir() or not any(folder.rglob("*.eval")):
        return None
    runs = load_runs([folder])
    return runs if per_epoch else mean_over_epochs(runs)


def engine_scores(frame: pd.DataFrame, by: Sequence[str], player: str = "baseline") -> pd.DataFrame:
    """Each player's pooled score per group: output − uniform over discerning − uniform, joined on the seed.

    `by` are the setting columns that, with the seed, name one timeline. An empty one is a group of its own.
    """
    rows = []
    groups = frame.groupby(list(by), dropna=False, sort=True) if by else [((), frame)]
    for group, block in groups:
        wide = block.pivot_table(index="seed", columns=player, values="output", aggfunc="first")
        if "uniform" not in wide or "discerning" not in wide:
            continue
        wide = wide.dropna(subset=["uniform", "discerning"])
        gaps = (wide["discerning"] - wide["uniform"]).to_numpy(dtype=float)
        values = group if isinstance(group, tuple) else (group,)
        for name in wide.columns:
            gains = (wide[name] - wide["uniform"]).to_numpy(dtype=float)
            ok = ~np.isnan(gains)
            if ok.any() and gaps[ok].sum() != 0:
                score = pooled_score(gains[ok], gaps[ok])
                rows.append(dict(zip(by, values)) | {player: name, "seeds": int(ok.sum()), "score": score})
    return pd.DataFrame(rows, columns=[*by, player, "seeds", "score"])


def share(values: pd.Series) -> float | None:
    """The share of true values, None with none at all."""
    values = values.dropna()
    return float(values.astype(bool).mean()) if len(values) else None


def median(values: pd.Series) -> float | None:
    values = values.dropna()
    return float(values.median()) if len(values) else None


def holds(text: str, ok: bool) -> str:
    """A pass line, in bold when it breaks."""
    return f"{text}, holds" if ok else f"**{text}, breaks**"
