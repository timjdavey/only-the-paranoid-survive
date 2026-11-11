"""The strip, profile, trend and noise plots, each a table to one SVG. See docs/specs/analysis/plots.md.

Every plot is drawn on its own Figure, never through pyplot, inside one rc context that fixes the font, the SVG
hash salt and text as paths, so the same inputs give the same bytes.
"""

import math
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Literal

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from paranoid.engine import SCENARIOS
from paranoid.harness import BOOTSTRAP_SEED, REASONING, TRAITS, ModelRow, scenario_config

from .keys import ResultKey, is_provider, key_of, keys_in, label, rows_of
from .names import curve_heading, heading
from .pool import by_scenario
from .scores import headlines, scenario_scores
from .threshold import Threshold, curve, logistic, signal_points

matplotlib.use("Agg")
SCENARIOS_FIRST = next(iter(SCENARIOS))
PALETTE = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000")  # Okabe and Ito
GREYS = {"complacent": "#7f7f7f", "hedge_rule": "#a6a6a6", "scout_rule": "#bfbfbf", "perfect": "#404040"}
MARK_NAMES = {"complacent": "Complacent", "hedge_rule": "Hedge rule", "scout_rule": "Scout rule", "perfect": "Perfect"}
RC = {"svg.hashsalt": "paranoid", "font.family": "DejaVu Sans", "svg.fonttype": "path", "font.size": 8}
FLAG_WORDS = {"†": "† a run gave up", "‡": "‡ retries ran high", "§": "§ recognised the prompt", "¶": "¶ finished the canary"}


def save(figure: Figure, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(out, format="svg", metadata={"Date": None})
    return out


def figure(width: float, height: float, *, left=0.1, right=0.97, bottom=0.15, top=0.85) -> Figure:
    """A figure with its margins set by hand, never by a tight layout that reads font metrics."""
    made = Figure(figsize=(width, height))
    made.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
    return made


def strip_plot(runs: pd.DataFrame, key: ResultKey, out: Path) -> Path:
    """Eight panels, one per scenario: the run scores, the pooled score with its bar, and the marks."""
    mine = rows_of(runs, key)
    scores = scenario_scores(mine).set_index("scenario")
    groups = by_scenario(mine)
    with matplotlib.rc_context(RC):
        made = figure(12, 3, left=0.04, right=0.99, bottom=0.2, top=0.78)
        axes = made.subplots(1, len(SCENARIOS), sharey=True)
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        every = mine["run_score"].dropna().to_numpy(dtype=float)
        low = min(-0.15, float(every.min()) - 0.05) if len(every) else -0.15  # one axis on every panel, wide enough for
        high = max(1.15, float(every.max()) + 0.05) if len(every) else 1.15  # a score outside 0 to 1 to show where it lands
        for axis, scenario in zip(axes, SCENARIOS):
            first = scenario == SCENARIOS_FIRST
            axis.set_xticks([])
            axis.set_xlim(-0.5, 0.5)
            axis.set_ylim(low, high)
            for level, word in ((0, "Uniform"), (1, "Discerning")):
                axis.axhline(level, color="#d9d9d9", linewidth=0.8, label=f"{word} baseline" if first else None)
            flags = scores.loc[scenario, "flags"] if scenario in scores.index else ""
            axis.set_title(f"{TRAITS[scenario].capitalize()} {flags}".strip(), fontsize=8)
            if scenario not in groups:
                continue
            row = scores.loc[scenario]
            dots = groups[scenario]["run_score"].dropna().to_numpy(dtype=float)
            axis.scatter(rng.uniform(-0.3, 0.3, len(dots)), dots, s=8, color=PALETTE[0], alpha=0.6, linewidths=0)
            error = [[row["score"] - row["lo"]], [row["hi"] - row["score"]]]
            axis.errorbar([0], [row["score"]], yerr=error, fmt="o", color=PALETTE[1], capsize=3)
            for mark, grey in GREYS.items():
                axis.hlines(row[mark], -0.45, 0.45, colors=grey, linestyles="--", linewidth=0.9, label=MARK_NAMES[mark] if first else None)
        made.suptitle(f"{heading(key.setting)}: {label(key)}", fontsize=9)
        made.legend(loc="lower center", ncol=6, frameon=False, fontsize=7)
        used = "".join(scores["flags"])
        legend = "   ".join(words for flag, words in FLAG_WORDS.items() if flag in used)
        if legend:
            made.text(0.99, 0.02, legend, ha="right", fontsize=7)
        return save(made, out)


def profile_plot(scores: pd.DataFrame, out: Path) -> Path:
    """The trait profile of one setting: one line per result row with its bars, and the Complacent marks in grey."""
    with matplotlib.rc_context(RC):
        made = figure(6, 4, bottom=0.2)
        axis = made.subplots()
        names = list(SCENARIOS)
        axis.set_xticks(range(len(names)), [TRAITS[n].capitalize() for n in names], rotation=30, ha="right")
        keys = keys_in(scores)
        for i, key in enumerate(keys):
            mine = rows_of(scores, key).set_index("scenario").reindex(names)
            x = np.arange(len(names))
            axis.errorbar(x, mine["score"], yerr=[mine["score"] - mine["lo"], mine["hi"] - mine["score"]],
                          color=PALETTE[i % len(PALETTE)], marker="o", markersize=3, capsize=2, label=label(key))  # fmt: skip
        if keys:
            first = rows_of(scores, keys[0]).set_index("scenario").reindex(names)
            axis.plot(range(len(names)), first["complacent"], color=GREYS["complacent"], linestyle="--", label="Complacent")
            made.suptitle(heading(keys[0].setting), fontsize=9)
        axis.set_ylabel("Scenario score")
        axis.legend(fontsize=6, frameon=False)
        return save(made, out)


def trend_plot(
    headlines: pd.DataFrame, models: Sequence[ModelRow], x: Literal["released", "eci"], out: Path, *,
    eci_read_on: date | None = None,
) -> Path:  # fmt: skip
    """Headline against release date or ECI, settings of one model joined, provider rows as lines across."""
    if x == "eci" and eci_read_on is None:
        raise ValueError("the ECI plot needs eci_read_on, the date the values were read, for Epoch AI's credit")
    rows = {row.id: row for row in models}
    with matplotlib.rc_context(RC):
        made = figure(6, 4, bottom=0.2)
        axis = made.subplots()
        left_out: list[str] = []
        lines = []
        order = {name: i for i, name in enumerate(REASONING)}
        keys = keys_in(headlines)
        colours = {model: PALETTE[i % len(PALETTE)] for i, model in enumerate(dict.fromkeys(k.model for k in keys))}
        for model in colours:
            mine = sorted((k for k in keys if k.model == model), key=lambda k: order.get(k.reasoning, len(order)))
            row = rows.get(model)
            values = [rows_of(headlines, k).iloc[0] for k in mine]
            if (row.kind != "llm") if row is not None else is_provider(model):
                for value in values:
                    lines.append((label(key_of(value)), float(value["headline"])))
                continue
            position = getattr(row, x, None) if row is not None else None
            if position is None:
                left_out += [label(key_of(v)) for v in values]
                continue
            xs = [position] * len(values)
            ys = [float(v["headline"]) for v in values]
            errors = [[y - float(v["lo"]) for y, v in zip(ys, values)], [float(v["hi"]) - y for y, v in zip(ys, values)]]
            axis.errorbar(xs, ys, yerr=errors, color=colours[model], marker="o", markersize=3, capsize=2, label=model)
        for i, (name, level) in enumerate(lines):
            axis.axhline(level, color=GREYS["complacent"], linewidth=0.8, linestyle=":")
            axis.annotate(name, (0.01, level), xycoords=("axes fraction", "data"), fontsize=6, va="bottom")
        if keys:
            made.suptitle(heading(keys[0].setting), fontsize=9)
        axis.set_xlabel("Release date" if x == "released" else "Epoch Capabilities Index")
        axis.set_ylabel("Headline")
        footer = []
        if left_out:
            footer.append(f"No {x}: {', '.join(left_out)}")
        if x == "eci":
            footer.append(f"ECI from Epoch AI, CC BY 4.0, read on {eci_read_on.isoformat()}")  # type: ignore[union-attr]
        made.text(0.01, 0.02, ". ".join(footer), fontsize=6)
        if axis.get_legend_handles_labels()[0]:
            axis.legend(fontsize=6, frameon=False)
        return save(made, out)


def noise_plot(runs: pd.DataFrame, thresholds: Sequence[Threshold], out: Path) -> Path:
    """Headline against signal to noise, one line per model with its fit, the Complacent headline and half way mark."""
    signal = signal_points(scenario_config("down_switch"))
    with matplotlib.rc_context(RC):
        made = figure(6, 4, top=0.8)
        axis = made.subplots()
        axis.set_xscale("log")
        axis.set_xlabel("Signal to noise")
        axis.set_ylabel("Headline")
        flip = lambda value: signal / np.clip(value, 1e-9, None)  # noqa: E731, snr and own_scale are each other's inverse
        top = axis.secondary_xaxis("top", functions=(flip, flip))
        top.set_xlabel("Own-weather scale")
        for i, found in enumerate(thresholds):
            colour = PALETTE[i % len(PALETTE)]
            keys = curve(runs, found.key)
            snr = np.array([signal / k.setting.own_scale for k in keys])  # type: ignore[operator]
            heads = pd.concat([headlines(rows_of(runs, k)) for k in keys], ignore_index=True)
            y, lo, hi = (heads[c].to_numpy(dtype=float) for c in ("headline", "lo", "hi"))
            axis.errorbar(snr, y, yerr=[y - lo, hi - y], fmt="o", color=colour, markersize=3, capsize=2, label=label(found.key))
            if found.snr is not None and found.k is not None:
                grid = np.geomspace(snr.min(), snr.max(), 100)
                fitted = logistic(found.complacent)(np.log(grid), found.k, math.log(found.snr))
                axis.plot(grid, fitted, color=colour, linewidth=1)
                tick, name = found.snr, label(found.key)
            else:
                tick = snr.max() if found.status == "off the noisy end" else snr.min()
                name = f"{label(found.key)}, {found.status}"
            axis.annotate(name, (tick, 0), xycoords=("data", "axes fraction"), fontsize=6, rotation=90)
            half = found.complacent + (1 - found.complacent) / 2
            axis.axhline(found.complacent, color=GREYS["complacent"], linewidth=0.8)
            axis.axhline(half, color=GREYS["complacent"], linewidth=0.8, linestyle=":")
        if thresholds:
            keys = [k.setting for t in thresholds for k in curve(runs, t.key)]
            made.suptitle(curve_heading(thresholds[0].key.setting, keys), fontsize=9)
        axis.legend(fontsize=6, frameon=False)
        return save(made, out)

