"""The baseline-order cell. See docs/specs/harness/pilot.md#baseline-order.

The reachable gain check reads this file too, so there is no reachable-gain cell.
"""

from pathlib import Path

from paranoid.engine import SCENARIOS, make_timeline, play

from .common import CellArgs, defaults, engine_seeds, move_round, output, stayer, switch_kind, write_csv
from .sweeps import BOTH_WAYS


def baseline_order(args: CellArgs) -> list[Path]:
    columns = ("scenario", "kind", "baseline", "seed", "output", "move_round")

    def rows():
        for name, config in SCENARIOS.items():
            players = defaults() + ([("stayer", stayer)] if name == BOTH_WAYS else [])
            for seed in engine_seeds(args):
                t = make_timeline(config, seed)
                for baseline, policy in players:
                    record = play(policy, t)
                    yield name, switch_kind(t), baseline, seed, output(record), move_round(record, t.leader)

    return write_csv(args, "baseline-order", columns, rows)
