"""The one command: draw every image and write criteria.md. See shapes/README.md#redraw-everything.

    uv run python shapes/src/make.py
"""

import argparse
import math
from pathlib import Path

import criteria
import draw

from paranoid.engine import SCENARIOS, make_timeline

SHAPES = Path(__file__).resolve().parents[1]
PUBLIC = SHAPES.parent / "configs" / "seeds" / "public.txt"
TWINS = ("no_change", "one_shock", "down_switch")


def public_seeds() -> list[int]:
    lines = PUBLIC.read_text().splitlines()
    return [int(line) for line in lines if line.strip() and not line.startswith("#")]


def level_axis(timelines) -> draw.Levels:
    """One axis for every image, rounded out to tens."""
    low = min(float(t.levels.min()) for t in timelines)
    high = max(float(t.levels.max()) for t in timelines)
    return (math.floor(low / 10) * 10, math.ceil(high / 10) * 10)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4], help="seeds to draw")
    parser.add_argument("--criteria-seeds", type=int, default=1000, help="how many public seeds the criteria read")
    args = parser.parse_args()

    timelines = {(name, s): make_timeline(config, s) for name, config in SCENARIOS.items() for s in args.seeds}
    levels = level_axis(timelines.values())
    images = SHAPES / "images"
    for (name, s), timeline in timelines.items():
        draw.timeline_figure(timeline, levels, images / name / f"seed-{s}.png")
    for s in args.seeds:
        draw.twins_figure([timelines[(name, s)] for name in TWINS], levels, images / "twins" / f"seed-{s}.png")
    print(f"drew {len(timelines) + len(args.seeds)} images on a level axis of {levels[0]} to {levels[1]}")

    seeds = public_seeds()[: args.criteria_seeds]
    sections = criteria.criteria(seeds)
    (SHAPES / "criteria.md").write_text(criteria.markdown(sections, seeds))
    print(f"wrote criteria.md from {len(seeds)} public seeds")


if __name__ == "__main__":
    main()
