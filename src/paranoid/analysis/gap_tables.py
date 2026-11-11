"""The cross setting tables and the noise threshold table. See docs/specs/analysis/tables.md#the-cross-setting-tables.

Each compares two result rows of one model and reasoning setting. A model with two candidates for one side, as they
differ in harness_version alone, has no row, and a line under the table names it.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from itertools import combinations

import pandas as pd

from paranoid.engine import SCENARIOS
from paranoid.harness import BOOTSTRAP_DRAWS

from .gaps import paired_gap, public_gap
from .keys import ResultKey, Setting, compared, differing, label, rows_of
from .names import DEFAULTS, bar, curve_heading, design_name, knob, markdown_table, number, slug
from .scores import headlines
from .threshold import Threshold, noise_threshold

SENSITIVITY_KNOBS = ("tools", "rolling", "tool_choice")
GAP_HEADER = [design_name(s) for s in SCENARIOS] + ["Headline"]


@dataclass
class Page:
    """What the cross setting tables need from the page: the keys in page order, each section's heading and labels."""

    keys: list[ResultKey]
    heading_of: Callable[[Setting], str]
    label_of: Callable[[ResultKey], str]
    lines: list[str] = field(default_factory=list)

    def twins(self, key: ResultKey) -> list[ResultKey]:
        """Every key that differs from this one in harness_version alone, itself included."""
        return [k for k in self.keys if (k.model, k.reasoning, compared(k.setting)) == (key.model, key.reasoning, compared(key.setting))]


def gap_cells(gap: pd.DataFrame) -> list[str]:
    by_pair = gap.set_index("pair")
    return [bar(*by_pair.loc[p, ["diff", "lo", "hi"]]) if p in by_pair.index else "" for p in [*SCENARIOS, "headline"]]


def unique_or_line(page: Page, key: ResultKey, notes: list[str]) -> bool:
    twins = page.twins(key)
    if len(twins) == 1:
        return True
    line = f"{label(key)} has rows at harness versions {' and '.join(sorted(k.setting.harness_version for k in twins))}, so no row here."
    if line not in notes:
        notes.append(line)
    return False


def section(title: str, columns: Sequence[str], rows: list[list[str]], notes: list[str]) -> list[str]:
    if not rows and not notes:
        return []
    lines = [f"## {title}", ""]
    if rows:
        lines += markdown_table(columns, rows) + [""]
    return lines + [f"- {note}" for note in notes] + ([""] if notes else [])


def sensitivity(runs: pd.DataFrame, page: Page) -> list[str]:
    """A row wherever two rows of one model differ in one of tools, rolling and tool_choice alone, the first at its default."""
    rows, notes = [], []
    for first in page.keys:
        for second in page.keys:
            if (first.model, first.reasoning) != (second.model, second.reasoning):
                continue
            changed = differing(first.setting, second.setting)
            if len(changed) != 1 or changed[0] not in SENSITIVITY_KNOBS:
                continue
            name = changed[0]
            if getattr(first.setting, name) != DEFAULTS[name]:
                continue
            if not (unique_or_line(page, first, notes) and unique_or_line(page, second, notes)):
                continue
            head = headline_of(runs, second)
            gap = paired_gap(runs, first, second).set_index("pair").loc["headline"]
            rows.append([
                page.label_of(first), page.heading_of(first.setting), knob(name, getattr(second.setting, name)),
                bar(head["headline"], head["lo"], head["hi"]), bar(gap["diff"], gap["lo"], gap["hi"]),
            ])  # fmt: skip
    return section("Sensitivity", ["Model", "Setting", "Knob", "Headline", "Gap"], rows, notes)


def headline_of(runs: pd.DataFrame, key: ResultKey) -> pd.Series:
    return headlines(rows_of(runs, key)).iloc[0]


def public_gaps(runs: pd.DataFrame, page: Page) -> list[str]:
    """A row wherever public_gap finds a public row its held-out partner."""
    rows, notes = [], []
    for key in page.keys:
        if key.setting.seed_set != "public":
            continue
        partners = [k for k in page.keys if (k.model, k.reasoning) == (key.model, key.reasoning)
                    and differing(key.setting, k.setting) == ["seed_set"]]  # fmt: skip
        if not partners:
            continue
        if not (unique_or_line(page, key, notes) and all(unique_or_line(page, k, notes) for k in partners)):
            continue
        rows.append([page.label_of(key), page.heading_of(key.setting), *gap_cells(public_gap(runs, key))])
    return section("Public gap", ["Model", "Setting", *GAP_HEADER], rows, notes)


def skin_sensitivity(runs: pd.DataFrame, page: Page) -> list[str]:
    """A row wherever two rows of one model differ in skin and nothing else but prompt_hash, pairs in name order."""
    rows, notes = [], []
    for a, b in combinations(page.keys, 2):
        if (a.model, a.reasoning) != (b.model, b.reasoning) or set(differing(a.setting, b.setting)) - {"prompt_hash"} != {"skin"}:
            continue
        a, b = sorted((a, b), key=lambda k: k.setting.skin)
        if not (unique_or_line(page, a, notes) and unique_or_line(page, b, notes)):
            continue
        skins = f"{a.setting.skin} − {b.setting.skin}"
        rows.append([page.label_of(a), page.heading_of(a.setting), skins, *gap_cells(paired_gap(runs, a, b))])
    return section("Skin sensitivity", ["Model", "Setting", "Skins", *GAP_HEADER], rows, notes)


def curves(page: Page) -> dict[Setting, list[ResultKey]]:
    """Result rows with own_scale set, by their setting without own_scale and harness_version."""
    found: dict[Setting, list[ResultKey]] = {}
    for key in page.keys:
        if key.setting.own_scale is not None:
            plain = compared(Setting(**{**key.setting.__dict__, "own_scale": None}))
            found.setdefault(plain, []).append(key)
    return found


def threshold_cell(found: Threshold) -> str:
    if found.snr is None:
        return found.status
    text = bar(found.snr, found.lo, found.hi, places=1)
    if found.uncrossed_draws:
        text += f", {found.uncrossed_draws} of {BOOTSTRAP_DRAWS} draws off the grid"
    return text


def noise_tables(
    runs: pd.DataFrame, page: Page, link: Callable[[str], str] | None
) -> tuple[list[str], list[tuple[str, list[Threshold]]]]:
    """One section per curve that any model has three settings on, and the noise plot file each asks for.

    `link` turns a plot's file name into the line that links it, or is None when plots are off.
    """
    lines: list[str] = []
    plots: list[tuple[str, list[Threshold]]] = []
    every = [k.setting for k in page.keys]
    for plain, keys in curves(page).items():
        models = list(dict.fromkeys((k.model, k.reasoning) for k in keys))
        counts = {m: len({k.setting.own_scale for k in keys if (k.model, k.reasoning) == m}) for m in models}
        if max(counts.values()) < 3:
            continue
        rows, notes, found = [], [], []
        for model in models:
            first = next(k for k in keys if (k.model, k.reasoning) == model)
            if counts[model] < 3:
                notes.append(f"{label(first)} has {counts[model]} noise settings, and a curve needs three.")
                continue
            try:
                threshold = noise_threshold(runs, first)
            except ValueError as error:
                notes.append(f"{label(first)}: {error}.")
                continue
            found.append(threshold)
            rows.append([
                label(first), threshold_cell(threshold), number(threshold.snr_80, 1), number(threshold.own_scale, 1),
                f"{number(threshold.complacent)} (±{number(threshold.complacent_drift)})", str(threshold.settings),
            ])  # fmt: skip
        title = curve_heading(keys[0].setting, every)
        columns = ["Model", "Threshold", "At 80%", "Own-weather scale", "Complacent", "Settings"]
        lines += section(f"Noise threshold, {title}", columns, rows, notes)
        if found and link is not None:
            name = f"{slug(title)}-noise.svg"
            plots.append((name, found))
            lines += [link(name), ""]
    return lines, plots
