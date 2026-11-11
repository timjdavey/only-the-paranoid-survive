"""switch_kinds: which kind of switch each seed drew. See docs/specs/analysis/scores.md#switch-kinds.

The one place in the layer that builds a timeline. Each is dropped as soon as its word is read, and nothing is
cached to disk, as a cache would be a timeline on disk.
"""

import pandas as pd

from paranoid.engine import make_timeline
from paranoid.harness import load_seeds, scenario_config

from .keys import cell
from .pool import scored

WORLD = ("scenario", "seed_set", "seed_index", "engine_hash", "game_rounds", "inertia", "own_scale")


def switch_kind(timeline) -> str:
    """The first switch's kind, rise_short when it stops short, none with no switch."""
    switch = next((event for event in timeline.events if event.shape == "switch"), None)
    if switch is None:
        return "none"
    return "rise_short" if switch.numbers.get("short") == 1 else str(switch.numbers["kind"])


def switch_kinds(runs: pd.DataFrame) -> pd.DataFrame:
    """One row per distinct world in the table, with its switch_kind. A held-out seed is read from its seed file."""
    worlds = scored(runs)[list(WORLD)].drop_duplicates()
    rows = []
    seeds: dict[str, list[int]] = {}
    for world in worlds.itertuples(index=False):
        values = {name: cell(value) for name, value in zip(WORLD, world)}
        listed = seeds.setdefault(values["seed_set"], load_seeds(values["seed_set"]))
        config = scenario_config(
            values["scenario"], rounds=values["game_rounds"], inertia=values["inertia"], own_scale=values["own_scale"]
        )
        timeline = make_timeline(config, listed[values["seed_index"]])
        if timeline.engine_hash != values["engine_hash"]:
            raise ValueError(
                f"{values['scenario']} at position {values['seed_index']}: the row's engine hash {values['engine_hash']} "
                f"is not {timeline.engine_hash}, the hash of the config rebuilt from its knobs"
            )
        rows.append(values | {"switch_kind": switch_kind(timeline)})
    return pd.DataFrame(rows, columns=[*WORLD, "switch_kind"]).astype({c: runs[c].dtype for c in WORLD} | {"switch_kind": "str"})
