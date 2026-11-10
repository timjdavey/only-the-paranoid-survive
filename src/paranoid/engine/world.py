"""The arrays events edit, on a horizon longer than the run.

See docs/specs/engine/timeline.md#events. Every rule reads its rows as written,
wherever the onset lands, and the arrays are cut to `rounds` at the end.
"""

from dataclasses import dataclass

import numpy as np

from .config import ScenarioConfig
from .ladder import Ladder
from .specs import DriftSpec, ShockSpec, SwitchSpec


def horizon(config: ScenarioConfig) -> int:
    """Enough rows for the latest onset the config can draw, plus its longest ramp."""
    latest_onset = config.onset[1] + sum(spec.gap[1] for spec in config.events)
    longest = 1
    for spec in config.events:
        if isinstance(spec, SwitchSpec):
            longest = max(longest, spec.ramp[1])
        elif isinstance(spec, DriftSpec):
            longest = max(longest, spec.length[1])
        elif isinstance(spec, ShockSpec):
            longest = max(longest, spec.half_life[1] + 1)
    return max(config.rounds, latest_onset + longest + 1)


@dataclass
class World:
    config: ScenarioConfig
    ladder: Ladder
    base: np.ndarray  # (rows, channels)
    loadings: np.ndarray  # (rows, channels)
    impulse: np.ndarray  # (rows, channels), a one-channel shock
    shock: np.ndarray  # (rows,), shock impulses into the shared factor

    @classmethod
    def start(cls, config: ScenarioConfig, ladder: Ladder, loadings: np.ndarray) -> "World":
        rows = horizon(config)
        shape = (rows, config.channels)
        return cls(
            config=config,
            ladder=ladder,
            base=np.tile(ladder.base, (rows, 1)),
            loadings=np.tile(loadings, (rows, 1)),
            impulse=np.zeros(shape),
            shock=np.zeros(rows),
        )

    @property
    def rows(self) -> int:
        return self.base.shape[0]

    def leader_at(self, row: int) -> int:
        """The climate leader: argmax of base in that row, lowest index on a tie."""
        return int(np.argmax(self.base[row]))

    def highest_at(self, row: int, excluding: set[int]) -> int:
        """The channel with the highest base in that row, other than those excluded."""
        values = self.base[row].copy()
        values[sorted(excluding)] = -np.inf
        return int(np.argmax(values))
