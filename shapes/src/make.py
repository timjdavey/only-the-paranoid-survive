"""The one command: draw every image and write criteria.md. See shapes/README.md#redraw-everything.

    uv run python shapes/src/make.py
    uv run python shapes/src/make.py --readers   # also plays two readers, a few minutes
"""

import argparse
import math
from pathlib import Path

import criteria
import draw
import readers
from worlds import CHANGED, NEW, TODAY, WORLDS

from paranoid.engine import make_timeline

SHAPES = Path(__file__).resolve().parents[1]
PUBLIC = SHAPES.parent / "configs" / "seeds" / "public.txt"
TWINS = ("no_change", "one_shock", "down_switch")
READER_SEEDS = 100


def public_seeds() -> list[int]:
    lines = PUBLIC.read_text().splitlines()
    return [int(line) for line in lines if line.strip() and not line.startswith("#")]


def level_axis(timelines) -> draw.Levels:
    """One axis for every image, rounded out to tens."""
    low = min(float(t.levels.min()) for t in timelines)
    high = max(float(t.levels.max()) for t in timelines)
    return (math.floor(low / 10) * 10, math.ceil(high / 10) * 10)


def draw_all(seeds: list[int]) -> int:
    """The new world for all eight in images/, and today's for the four the knobs change in images/today/."""
    new = {(name, s): make_timeline(config, s) for name, config in NEW.items() for s in seeds}
    today = {(name, s): make_timeline(TODAY[name], s) for name in (*CHANGED, "no_change") for s in seeds}
    levels = level_axis([*new.values(), *today.values()])
    images = SHAPES / "images"
    for (name, s), timeline in new.items():
        draw.timeline_figure(timeline, levels, images / name / f"seed-{s}.png")
    for (name, s), timeline in today.items():
        if name in CHANGED:
            draw.timeline_figure(timeline, levels, images / "today" / name / f"seed-{s}.png")
    for s in seeds:
        draw.twins_figure([new[(n, s)] for n in TWINS], levels, images / "twins" / f"seed-{s}.png", "through the trough")
        draw.twins_figure([today[(n, s)] for n in TWINS], levels, images / "today" / "twins" / f"seed-{s}.png", "until onset")
    count = len(new) + len(CHANGED) * len(seeds) + 2 * len(seeds)
    print(f"drew {count} images on a level axis of {levels[0]} to {levels[1]}")
    return count


def markdown(sections: dict, seeds: list[int]) -> str:
    config = TODAY["no_change"]
    lines = [
        "# Shape criteria",
        "",
        "Written by `shapes/src/make.py`. Do not edit by hand. What each measure is for is in [the README](README.md#the-test).",
        "",
        f"- **Seeds.** The first {len(seeds)} public seeds, {seeds[0]} to {seeds[-1]}.",
        "- **Today** is the eight scenarios as the engine ships them. **New** has the shape knobs on and a k of "
        f"{NEW['no_change'].read_noise_k:g}, see [worlds](src/worlds.py).",
        f"- **Levels, not readings**, unless a row says readings or looks. One sigma is {config.own_scale:g} points.",
        "- **An event's effect** is its timeline minus the No change twin on the same seed.",
        "- **A size** in points is the median, then the 10th to 90th percentile in brackets.",
        "- **A count** of rounds or channels, and the points a holder gives up, is the mean, then the 10th to 90th percentile.",
        "- **A switch kind row** gives three shares, then how many seeds drew that kind. The kinds fall on different "
        "seeds in the two worlds, as a storm switch draws its storm first.",
        "",
    ]
    for purpose, rows in sections.items():
        lines += [f"## {purpose}", "", "| Measure | Today | New |", "|---|---|---|"]
        lines += [f"| {measure} | {today} | {new} |" for measure, today, new in rows]
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4], help="seeds to draw")
    parser.add_argument("--criteria-seeds", type=int, default=1000, help="how many public seeds the criteria read")
    parser.add_argument("--readers", action="store_true", help="also play two readers in both worlds")
    args = parser.parse_args()

    draw_all(args.seeds)
    seeds = public_seeds()[: args.criteria_seeds]
    (SHAPES / "criteria.md").write_text(markdown(criteria.criteria(WORLDS, seeds), seeds))
    print(f"wrote criteria.md from {len(seeds)} public seeds")
    if args.readers:
        few = public_seeds()[:READER_SEEDS]
        (SHAPES / "readers.md").write_text(readers.readers(WORLDS, few))
        print(f"wrote readers.md from {len(few)} public seeds")


if __name__ == "__main__":
    main()
