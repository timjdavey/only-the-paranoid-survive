"""write_pilot, SECTIONS and the reachable gain floors: pilot results from the pilot cells. See docs/specs/analysis/pilot.md.

Each section reads its own inputs and builds its tables, or says `_Not run yet._`. The engine sections are in
engine.py and order.py, the provider sections in provider.py and knobs.py.
"""

import csv
import io
import re
from pathlib import Path

import pandas as pd

from ..names import markdown_table, slug
from ..run_csv import text
from .common import Builder, Section
from .engine import game_length, noise, reading_roughness, up_and_down, weather
from .knobs import bare_harness, cost_per_run, rolling, tool_choice, warm_up
from .order import BAYESIAN_GAIN_PERCENTAGE_FLOOR, BAYESIAN_MOVE_SHARE_FLOOR, REACHABLE_GAIN_FLOOR
from .order import baseline_order, bayesian_frontier, reachable_gain, timestral_checks
from .provider import channel_order, jev_checks, recognition, seeds_and_repeats, up_against_down

BUILDERS: dict[str, Builder] = {
    "Weather": weather,
    "Seeds and repeats": seeds_and_repeats,
    "Recognition": recognition,
    "Channel order": channel_order,
    "Up against down": up_against_down,
    "Noise": noise,
    "Game length and switch round": game_length,
    "Reading roughness": reading_roughness,
    "Up and down": up_and_down,
    "Bayesian frontier": bayesian_frontier,
    "Baseline order": baseline_order,
    "Reachable gain": reachable_gain,
    "Jev checks": jev_checks,
    "Timestral checks": timestral_checks,
    "Bare harness": bare_harness,
    "Tool choice": tool_choice,
    "Rolling conversation": rolling,
    "Warm up": warm_up,
    "Cost per run": cost_per_run,
}
SECTIONS: tuple[str, ...] = tuple(BUILDERS)
INTRO = (
    "Written by `uv run paranoid analyse` from the pilot logs. Do not edit by hand. "
    "The decisions taken from these tables are in [decisions](decisions.md)."
)
NOT_RUN = "_Not run yet._"


def write_pilot(logs: Path, out: Path, *, main: Path | None = None, dry_run: bool = False) -> list[Path]:
    """Rewrites out/results.md, and writes each table's CSV and each plot under out/results/."""
    page = out / "results.md"
    if page.exists():
        found = re.findall(r"^## (.+)$", page.read_text(encoding="utf-8"), re.M)
        for want, have in zip(SECTIONS, found + [""] * len(SECTIONS)):
            if want != have:
                raise ValueError(f"{page} has heading {have!r} where the pilot spec has {want!r}")
        if len(found) > len(SECTIONS):
            raise ValueError(f"{page} has heading {found[len(SECTIONS)]!r}, which the pilot spec does not")
    lines = ["# Pilot results", "", INTRO, ""]
    files: list[tuple[Path, object]] = []
    for heading, build in BUILDERS.items():
        section = build(logs, main) or Section()
        lines += [f"## {heading}", ""] + body(heading, section, files, out / "results") + [""]
    paths = [page, *(path for path, _ in files)]
    if dry_run:
        return paths
    out.mkdir(parents=True, exist_ok=True)
    page.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    for path, content in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            content(path)  # type: ignore[operator]
    return paths


def body(heading: str, section: Section, files: list[tuple[Path, object]], folder: Path) -> list[str]:
    """A section's tables, plot links and notes, queuing each file. `_Not run yet._` when it has none."""
    if section.empty:
        return [NOT_RUN]
    base = slug(heading)
    lines: list[str] = []
    for name, table in section.tables:
        file = f"{base}-{name}.csv"
        files.append((folder / file, csv_text(table)))
        lines += [f"### {name}", "", *markdown_table(list(map(str, table.columns)), cells(table)), "", f"[{file}](results/{file})", ""]
    if section.plots:
        links = []
        for name, draw in section.plots:
            file = f"{base}-{name}.svg"
            files.append((folder / file, draw))
            links.append(f"[{name}](results/{file})")
        lines += ["Plots: " + ", ".join(links), ""]
    lines += section.notes
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def cells(table: pd.DataFrame) -> list[list[str]]:
    """Every cell as the page shows it: a whole number plain, any other number to three significant places."""
    return [[shown(value) for value in row] for row in table.itertuples(index=False)]


def shown(value: object) -> str:
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() and abs(value) < 1e15 else f"{value:.3g}" if abs(value) < 1000 else f"{value:.0f}"
    return str(value)


def csv_text(table: pd.DataFrame) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(table.columns)
    for row in table.itertuples(index=False):
        writer.writerow([text(value.item() if hasattr(value, "item") else value) for value in row])
    return out.getvalue()


__all__ = ["write_pilot", "SECTIONS", "REACHABLE_GAIN_FLOOR", "BAYESIAN_GAIN_PERCENTAGE_FLOOR", "BAYESIAN_MOVE_SHARE_FLOOR"]
