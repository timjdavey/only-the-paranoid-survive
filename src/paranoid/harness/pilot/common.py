"""What every pilot cell shares: the args, the seeds, the CSV writer and the words the columns use.

See docs/specs/harness/pilot.md#shared-rules and #words-the-columns-use.
"""

import csv
import math
import os
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from paranoid.baselines import POLICIES
from paranoid.engine import Bets, Policy, Record, Timeline, View

from ..seeds import load_seeds

PILOT_SEEDS_VARIABLE = "PARANOID_PILOT_SEEDS"  # the harness's one test hook


@dataclass(frozen=True)
class CellArgs:
    out: Path = Path("logs/pilot")  # where every cell writes
    models: Path = Path("configs/models/poc.toml")
    only: str | None = None  # a model id, for cells that need a model
    seeds: int = 1000  # seeds an engine cell plays, capped by PARANOID_PILOT_SEEDS
    dry_run: bool = False


Cell = Callable[[CellArgs], list[Path]]  # returns the paths it wrote


def seed_cap(seeds: int) -> int:
    """`seeds`, capped by PARANOID_PILOT_SEEDS when it is set."""
    cap = os.environ.get(PILOT_SEEDS_VARIABLE)
    return min(seeds, int(cap)) if cap else seeds


def engine_seeds(args: CellArgs) -> list[int]:
    """Public positions 0 to seeds − 1, as seed values."""
    count = seed_cap(args.seeds)
    seeds = load_seeds("public")
    if len(seeds) < count:
        raise ValueError(f"the public list has {len(seeds)} seeds, fewer than {count}. Lower --seeds or {PILOT_SEEDS_VARIABLE}")
    return seeds[:count]


def write_csv(args: CellArgs, name: str, columns: Sequence[str], rows: Callable[[], Iterable[Sequence[Any]]]) -> list[Path]:
    """`<out>/<name>.csv` with exactly these columns. A dry run prints the path and columns and builds no row."""
    path = args.out / f"{name}.csv"
    if args.dry_run:
        print(f"{path}: {', '.join(columns)}")
        return []
    args.out.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for row in rows():
            if len(row) != len(columns):
                raise RuntimeError(f"{name}: a row of {len(row)} values for {len(columns)} columns")
            writer.writerow(["" if value is None else value for value in row])
    return [path]


def defaults() -> list[tuple[str, Policy]]:
    """Every entry in POLICIES, built at its defaults."""
    return [(name, build()) for name, build in POLICIES.items()]


def output(record: Record, rows: slice = slice(None)) -> float:
    return sum((row.output for row in record.rows[rows]), 0.0)


def onset(timeline: Timeline) -> int | None:
    return timeline.events[0].onset if timeline.events else None


def first_switch(timeline: Timeline):
    return next((event for event in timeline.events if event.shape == "switch"), None)


def switch_kind(timeline: Timeline) -> str:
    """The first switch's kind, rise_short when it stops short, none with no switch."""
    switch = first_switch(timeline)
    if switch is None:
        return "none"
    kind = str(switch.numbers["kind"])
    return "rise_short" if switch.numbers.get("short") == 1 else kind


def largest(bets: Bets) -> int:
    """The channel of the largest bet, lowest index on a tie."""
    return max(range(len(bets)), key=lambda c: (bets[c], -c))


def move_round(record: Record, leader: int) -> int:
    """The first round whose largest bet is not on the leader. 0 when it never happens."""
    return next((row.round for row in record.rows if largest(row.bets) != leader), 0)


def last_end(timeline: Timeline) -> int | None:
    """The round the last event ends, see the Words table."""
    if not timeline.events:
        return None
    event = timeline.events[-1]
    numbers = event.numbers
    if event.shape == "switch":
        return event.onset + int(numbers["ramp"]) - 1
    if event.shape == "drift":
        return event.onset + int(numbers["length"]) - 1
    half_life = int(numbers["half_life"])
    if numbers["profile"] == "sharp":
        return event.onset + math.ceil(3 * half_life)
    return event.onset + half_life + 3 * math.ceil(half_life / 2)


@dataclass(frozen=True)
class Stayer:
    """A pilot reference, never in POLICIES: plays as discerning until the last event begins, then holds."""

    peeks: ClassVar[bool] = True

    def __call__(self, view: View) -> Bets:
        timeline = view.timeline
        assert timeline is not None and timeline.events
        held = timeline.climate_leader(min(view.round, timeline.events[-1].onset - 1))
        return tuple(view.budget if c == held else 0 for c in range(view.channels))


stayer = Stayer()
