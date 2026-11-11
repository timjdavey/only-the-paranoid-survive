"""The baseline-order cell. See docs/specs/harness/pilot.md#baseline-order.

The reachable gain check reads this file too, so there is no reachable-gain cell.
"""

from pathlib import Path

from paranoid.engine import SCENARIOS, make_timeline, play

from .common import CellArgs, Rows, defaults, move_round, output, seed_rows, stayer, switch_kind, write_csv
from .sweeps import BOTH_WAYS


def baseline_order(args: CellArgs) -> list[Path]:
    columns = ("scenario", "kind", "baseline", "seed", "output", "move_round")
    blocks = [
        (name, config, defaults() + ([("stayer", stayer)] if name == BOTH_WAYS else [])) for name, config in SCENARIOS.items()
    ]
    return write_csv(args, "baseline-order", columns, lambda: seed_rows(args, order_rows, blocks))


def order_rows(block, seed: int) -> Rows:
    name, config, players = block
    t = make_timeline(config, seed)
    records = [(baseline, play(policy, t)) for baseline, policy in players]
    return [(name, switch_kind(t), baseline, seed, output(record), move_round(record, t.leader)) for baseline, record in records]
