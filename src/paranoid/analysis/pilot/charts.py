"""The pilot sections' plots: one line chart and one histogram, drawn as the results plots are.

See docs/specs/analysis/pilot.md#sections. Every plot here reads a section's own table, so it adds nothing to it.
"""

from collections.abc import Sequence
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

from ..plots import PALETTE, RC, figure, save


def lines(
    frame: pd.DataFrame, x: str, y: str, group: str | None, title: str, out: Path, *,
    panels: str | None = None, logx: bool = False, marks: Sequence[float] = (),
) -> Path:  # fmt: skip
    """One line per `group` value of y against x, one panel per `panels` value, horizontal lines at `marks`."""
    names = list(dict.fromkeys(frame[panels])) if panels else [None]
    with matplotlib.rc_context(RC):
        made = figure(6 if len(names) < 3 else 12, 4, bottom=0.15, top=0.85)
        axes = np.atleast_1d(made.subplots(1, len(names), sharey=True))
        for axis, name in zip(axes, names):
            here = frame if name is None else frame[frame[panels] == name]
            groups = list(dict.fromkeys(here[group])) if group else [None]
            for i, value in enumerate(groups):
                line = here if value is None else here[here[group] == value]
                line = line.sort_values(x)
                axis.plot(line[x], line[y], marker="o", markersize=3, color=PALETTE[i % len(PALETTE)], label=str(value))
            for mark in marks:
                axis.axhline(mark, color="#7f7f7f", linewidth=0.8, linestyle=":")
            if logx:
                axis.set_xscale("log")
            axis.set_xlabel(x)
            if name is not None:
                axis.set_title(str(name), fontsize=8)
            if group:
                axis.legend(fontsize=6, frameon=False)
        axes[0].set_ylabel(y)
        made.suptitle(title, fontsize=9)
        return save(made, out)


def histogram(frame: pd.DataFrame, column: str, group: str, title: str, out: Path) -> Path:
    """One histogram of whole numbers per `group` value, side by side."""
    with matplotlib.rc_context(RC):
        made = figure(6, 4)
        axis = made.subplots()
        values = frame[column].dropna().astype(int)
        bins = np.arange(values.min(), values.max() + 2) - 0.5 if len(values) else 1
        for i, value in enumerate(dict.fromkeys(frame[group])):
            mine = frame[frame[group] == value][column].dropna().astype(int)
            axis.hist(mine, bins=bins, histtype="step", color=PALETTE[i % len(PALETTE)], label=str(value))
        axis.set_xlabel(column)
        axis.set_ylabel("seeds")
        axis.legend(fontsize=6, frameon=False)
        made.suptitle(title, fontsize=9)
        return save(made, out)
