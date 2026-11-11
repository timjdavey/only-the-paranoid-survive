"""Seed files, the `seeds` arg and the noise grid. See docs/specs/harness/task.md#seeds and #release.

`configs/` is read from the working directory, as `--models` is. No message here holds a seed's value,
so a bad held-out file is safe to report.
"""

import math
import os
import re
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from paranoid.engine import SCENARIOS

from .config import joined, scenario_config

PUBLIC_SEEDS = Path("configs/seeds/public.txt")
GRID = Path("configs/grid.toml")
HELD_OUT_VARIABLE = "PARANOID_SEEDS"
HELD_OUT_FILE = "held-out.txt"
SEED_SETS = ("public", "held-out")
RELEASE = re.compile(r"[a-z0-9-]+")

SeedSet = Literal["public", "held-out"]

# path -> ((mtime, size), seeds). store.seed() runs every round, so a file is read again only when it changes.
_seed_files: dict[Path, tuple[tuple[int, int], list[int]]] = {}


def read_seed_file(path: Path) -> list[int]:
    """One whole number a line. Blank lines and `#` lines are skipped. A repeat raises."""
    path = path.resolve()
    stat = path.stat()
    stamp = (stat.st_mtime_ns, stat.st_size)
    cached = _seed_files.get(path)
    if cached is not None and cached[0] == stamp:
        return list(cached[1])
    seeds: list[int] = []
    seen: set[int] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        try:
            seed = int(text)
        except ValueError:
            raise ValueError(f"{path.name} line {number} is not a whole number") from None
        if seed in seen:
            raise ValueError(f"{path.name} line {number} repeats a seed")
        seen.add(seed)
        seeds.append(seed)
    _seed_files[path] = (stamp, seeds)
    return list(seeds)


def load_seeds(seed_set: SeedSet) -> list[int]:
    """The public list from `configs/seeds/public.txt`, or the held-out list from `$PARANOID_SEEDS/held-out.txt`."""
    if seed_set == "public":
        return read_seed_file(PUBLIC_SEEDS)
    if seed_set == "held-out":
        folder = os.environ.get(HELD_OUT_VARIABLE)
        if not folder:
            raise ValueError(f"held-out seeds need {HELD_OUT_VARIABLE} set to the folder holding {HELD_OUT_FILE}")
        return read_seed_file(Path(folder) / HELD_OUT_FILE)
    raise ValueError(f"seed_set must be public or held-out, got {seed_set!r}")


def seed_set_of(arg: str | Sequence[str]) -> SeedSet:
    """`held-out` for the held-out list, `public` for the public list or positions in it."""
    return "held-out" if joined(arg) == "held-out" else "public"


def parse_seeds(arg: str | Sequence[str]) -> list[tuple[int, int]]:
    """(position, seed) pairs in position order. Positions index the public list."""
    text = joined(arg)
    if text in SEED_SETS:
        return list(enumerate(load_seeds(text)))  # type: ignore[arg-type]
    seeds = load_seeds("public")
    positions: list[int] = []
    for part in text.split(","):
        low, dash, high = part.strip().partition("-")
        try:
            a, b = int(low), int(high if dash else low)
        except ValueError:
            raise ValueError(f"seeds must be public, held-out or positions such as 0-4,7, got {text!r}") from None
        if a < 0 or b < a:
            raise ValueError(f"seed range {part.strip()!r} must run from a low position to a higher one")
        positions.extend(range(a, b + 1))
    if len(set(positions)) < len(positions):
        raise ValueError(f"seeds {text!r} names a position twice")
    if max(positions) >= len(seeds):
        raise ValueError(f"seed position {max(positions)} is past the end of the public list of {len(seeds)}")
    return [(position, seeds[position]) for position in sorted(positions)]


@dataclass(frozen=True)
class Grid:
    release: str  # the release these settings belong to
    own_scale: tuple[float, ...]  # the noise grid


def load_grid() -> Grid:
    """`configs/grid.toml`. Every setting is built for every scenario, so a bad one fails here."""
    with GRID.open("rb") as file:
        data = tomllib.load(file)
    release = data.get("release")
    if not isinstance(release, str) or not RELEASE.fullmatch(release):
        raise ValueError(f"{GRID}: release must match [a-z0-9-]+, got {release!r}")
    settings = data.get("own_scale")
    if not isinstance(settings, list) or not settings:
        raise ValueError(f"{GRID}: own_scale must be a list of numbers")
    for value in settings:
        if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{GRID}: every own_scale setting must be a positive number, got {value!r}")
    grid = Grid(release=release, own_scale=tuple(float(value) for value in settings))
    for name in SCENARIOS:
        for setting in grid.own_scale:
            scenario_config(name, own_scale=setting)
    return grid
