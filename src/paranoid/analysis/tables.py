"""write_results: the results page, its CSV and its plots. See docs/specs/analysis/tables.md#the-results-page.

The page is built in memory from the logs alone, every file name is checked before anything is written, and the
page is never read first, so the same logs give the same bytes.
"""

from collections.abc import Callable
from datetime import date
from pathlib import Path

import pandas as pd

from paranoid.engine import SCENARIOS
from paranoid.harness import ModelRow, load_models

from .gap_tables import Page, noise_tables, public_gaps, sensitivity, skin_sensitivity
from .keys import ResultKey, Setting, compared, keys_in, label, rows_of
from .names import DEFAULTS, bar, design_name, heading, markdown_table, number, row_label, slug
from .plots import noise_plot, profile_plot, strip_plot, trend_plot
from .pool import by_scenario, pooled, scored, share
from .run_csv import run_csv_text
from .runs import mean_over_epochs
from .scores import RETRY_FLAG, headlines, scenario_scores
from .spread import sampling_share, spread

HEADER = [
    "Written by `paranoid analyse` from the logs, and never edited by hand.",
    "",
    "- One table per setting, and a skin is its name only.",
    "- Scores run from the Uniform baseline at 0 to the Discerning baseline at 1, and the headline is their plain mean.",
    "- `Tools` is how often each tool was used, as a share of rounds played.",
]
SCORE_COLUMNS = ["Model", *(design_name(s) for s in SCENARIOS), "Headline", "Weakest trait", "Tools"]
MARK_COLUMNS = {"complacent": "Complacent", "hedge_rule": "Hedge rule", "scout_rule": "Scout rule", "perfect": "Perfect"}
Plot = tuple[str, str, Callable[[Path], Path]]  # file name, the row it is for, and how to draw it


def write_results(
    runs: pd.DataFrame,
    out: Path,
    name: str,
    *,
    models: Path | None = None,
    recognition: pd.DataFrame | None = None,
    plots: bool = False,
    eci_read_on: date | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """out/<name>.md, out/<name>.csv and with plots out/<name>/*.svg. Returns what it wrote, or would write."""
    if not name or "/" in name or "\\" in name or ".." in name:
        raise ValueError(f"--name must be a bare file stem, got {name!r}")
    rows = load_models(models) if models is not None else None
    if plots and rows and any(row.eci is not None for row in rows) and eci_read_on is None:
        raise ValueError("the models file has eci values, so the ECI plot needs --eci-read-on for Epoch AI's credit")
    averaged = mean_over_epochs(runs)
    text, jobs = page_text(runs, averaged, name, rows, recognition, plots, eci_read_on)
    files = check_names(out, name, jobs)
    paths = [out / f"{name}.md", out / f"{name}.csv", *files]
    if dry_run:
        return paths
    out.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(text, encoding="utf-8")
    paths[1].write_text(run_csv_text(averaged), encoding="utf-8")
    for path, (_, _, draw) in zip(files, jobs):
        draw(path)
    return paths


def check_names(out: Path, name: str, jobs: list[Plot]) -> list[Path]:
    """Each plot's path, after checking no two share one."""
    seen: dict[str, str] = {}
    for file, row, _ in jobs:
        if file in seen:
            raise ValueError(f"two plots would share the name {file}: {seen[file]} and {row}")
        seen[file] = row
    return [out / name / file for file, _, _ in jobs]


LATER = ("game_rounds", "tools", "warm_up", "rolling", "tool_choice", "inertia", "prompt_hash", "generator_version", "release")


def section_order(setting: Setting) -> tuple:
    """Skin, public first, own_scale unset first then rising, then each later field, a default before any other.

    A field with no default, such as release, sorts by its value, so two settings never tie.
    """
    later = []
    for field in LATER:
        value = getattr(setting, field)
        if value is None or (field in DEFAULTS and value == DEFAULTS[field]):
            later.append((0, ""))
        else:
            later.append((1, str(value) if isinstance(value, str) else value))
    scale = setting.own_scale
    return (setting.skin, setting.seed_set != "public", scale is not None, scale or 0.0, *later)


def row_order(keys: list[ResultKey], heads: pd.DataFrame, models: list[ModelRow] | None) -> list[ResultKey]:
    """The models file's order, provider rows first, else by headline descending. A tie goes to the label."""
    headline = {key: float(rows_of(heads, key)["headline"].iloc[0]) for key in keys}
    place: dict[str, tuple[int, int, int]] = {}
    for index, row in enumerate(models or []):
        place.setdefault(row.id, (0, 0 if row.kind != "llm" else 1, index))
    reasoning = {row.id: row.reasoning for row in models or []}

    def order(key: ResultKey) -> tuple:
        if key.model in place:
            settings = reasoning[key.model]
            step = settings.index(key.reasoning) if key.reasoning in settings else len(settings)
            return (*place[key.model], step, 0.0, label(key), key.setting.harness_version)
        return (1, 0, 0, 0, -headline[key], label(key), key.setting.harness_version)

    return sorted(keys, key=order)


def page_text(runs, averaged, name, models, recognition, plots, eci_read_on) -> tuple[str, list[Plot]]:
    scores = scenario_scores(averaged, recognition=recognition)
    heads = headlines(averaged, recognition=recognition)
    keys = keys_in(scored(averaged))
    settings = sorted({compared(k.setting) for k in keys}, key=section_order)
    every = [k.setting for k in keys]
    heading_of = {s: heading(next(k.setting for k in keys if compared(k.setting) == s), every) for s in settings}
    ordered = [k for s in settings for k in row_order([k for k in keys if compared(k.setting) == s], heads, models)]
    twins = {
        k
        for k in keys
        if sum(compared(o.setting) == compared(k.setting) and o.model == k.model and o.reasoning == k.reasoning for o in keys) > 1
    }
    label_of = lambda key: row_label(key, key in twins)  # noqa: E731
    lines = [f"# Results: {name}", "", *HEADER, "", stamp(runs, averaged, name), ""]
    jobs: list[Plot] = []
    link = (lambda file: f"Plot: [{file}]({name}/{file})") if plots else None
    for setting in settings:
        section_keys = [k for k in ordered if compared(k.setting) == setting]
        lines += setting_section(heading_of[setting], section_keys, averaged, runs, scores, heads, label_of)
        if plots:
            lines += plot_section(
                heading_of[setting], section_keys, averaged, scores, heads, models, eci_read_on, label_of, jobs, name
            )
    page = Page(ordered, lambda s: heading_of[compared(s)], label_of)
    lines += sensitivity(averaged, page) + public_gaps(averaged, page) + skin_sensitivity(averaged, page)
    noise, curves = noise_tables(averaged, page, link)
    lines += noise
    for file, thresholds in curves:
        jobs.append((file, file, lambda path, t=thresholds: noise_plot(averaged, t, path)))
    return "\n".join(lines).rstrip() + "\n", jobs


def stamp(runs: pd.DataFrame, averaged: pd.DataFrame, name: str) -> str:
    versions = ", ".join(sorted(set(runs["harness_version"].dropna())))
    when = runs["started"].max().date().isoformat() if len(runs) else "no date"
    count = len(runs.attrs.get("report", {}).get("read", [])) or runs["log"].nunique()
    text = f"Written by paranoid analyse from {count} logs at harness version {versions} on {when}, see {name}.csv."
    errored = int(averaged["errored"].sum())
    return text + (f" {errored} samples errored and are in no score." if errored else "")


def setting_section(title, keys, averaged, runs, scores, heads, label_of) -> list[str]:
    """The heading, the versions line, the scores table and its legend, then Marks and Spread."""
    mine = pd.concat([rows_of(averaged, k) for k in keys])
    first = keys[0].setting
    versions = sorted({k.setting.harness_version for k in keys})
    lines = [f"## {title}", ""]
    lines += [
        f"Prompt hash {first.prompt_hash}, generator version {first.generator_version}, release {first.release}, "
        f"harness version {', '.join(versions)}.",
        "",
    ]
    rows = [score_row(k, rows_of(scores, k), rows_of(heads, k).iloc[0], rows_of(averaged, k), label_of) for k in keys]
    lines += markdown_table(SCORE_COLUMNS, rows) + [""]
    legend = legend_of(pd.concat([rows_of(scores, k) for k in keys]))
    lines += ([legend, ""] if legend else []) + ["### Marks", ""] + marks_table(mine) + [""]
    lines += ["### Spread", ""] + spread_table(keys, mine, runs, label_of) + [""]
    return lines


def score_row(key, scores, head, rows, label_of) -> list[str]:
    by = scores.set_index("scenario")
    cells = [
        (bar(r["score"], r["lo"], r["hi"]) + (f" {r['flags']}" if r["flags"] else "")) if s in by.index else ""
        for s in SCENARIOS
        for r in [by.loc[s] if s in by.index else None]
    ]
    headline = bar(head["headline"], head["lo"], head["hi"])
    headline += f" of {head['scenarios']}" if head["scenarios"] < len(SCENARIOS) else ""
    headline += f" {head['flags']}" if head["flags"] else ""
    weak = by.loc[head["weakest_scenario"]]
    weakest = f"{head['weakest_trait'].capitalize()} {bar(weak['score'], weak['lo'], weak['hi'])}"
    played = scored(rows)
    provider = (played["kind"] != "llm").all()
    tools = (
        ""
        if provider or key.setting.tools == "none"
        else (f"notes {number(share(played, 'notes_rounds'))}, compute {number(share(played, 'compute_rounds'))}")
    )
    return [label_of(key), *cells, headline, weakest, tools]


def legend_of(scores: pd.DataFrame) -> str:
    used = "".join(scores["flags"])
    parts = []
    if "†" in used:
        failed = int(scores["failed"].sum())
        parts.append(f"† {failed} {'run' if failed == 1 else 'runs'} gave up and scored as the Uniform baseline.")
    if "‡" in used:
        parts.append(f"‡ Retry share over {RETRY_FLAG}.")
    if "§" in used:
        parts.append("§ Recognised the prompt on over a quarter of probes.")
    if "¶" in used:
        parts.append("¶ Finished the canary, see recognition.")
    return " ".join(parts)


def marks_table(rows: pd.DataFrame) -> list[str]:
    """The fixed baselines' pooled scores per scenario, on the seeds the table scored."""
    # A mark is the world's, whoever played it, so each seed counts once, from a row that scored it.
    groups = by_scenario(scored(rows).drop_duplicates(["scenario", "seed_index"]))
    body = [[design_name(s), *(number(pooled(group, mark)) for mark in MARK_COLUMNS)] for s, group in groups.items()]
    return markdown_table(["Scenario", *MARK_COLUMNS.values()], body)


def spread_table(keys, rows, runs, label_of) -> list[str]:
    spreads = spread(rows)
    sampled = (runs["epochs"] > 1).any() if len(runs) else False
    shares = sampling_share(pd.concat([rows_of(runs, k) for k in keys])) if sampled else None
    body = []
    for key in keys:
        for row in rows_of(spreads, key).itertuples():
            cells = [label_of(key), design_name(row.scenario), number(row.sd), number(row.p10), str(row.n)]
            if shares is not None:
                mine = rows_of(shares, key).set_index("scenario")
                cells.append(number(mine.loc[row.scenario, "share"]) if row.scenario in mine.index else "")
            body.append(cells)
    columns = ["Model", "Scenario", "SD", "10th percentile", "Seeds"] + (["Sampling share"] if shares is not None else [])
    return markdown_table(columns, body)


def plot_section(title, keys, averaged, scores, heads, models, eci_read_on, label_of, jobs, name) -> list[str]:
    """Queue this setting's plots and return the lines that link them."""
    base = slug(title)
    files = []
    for key in keys:
        file = f"{base}-strip-{slug(label_of(key))}.svg"
        jobs.append((file, label_of(key), lambda path, k=key: strip_plot(averaged, k, path)))
        files.append(file)
    mine = pd.concat([rows_of(scores, k) for k in keys])
    jobs.append((f"{base}-profile.svg", title, lambda path: profile_plot(mine, path)))
    files.append(f"{base}-profile.svg")
    if models is not None:
        heads_here = pd.concat([rows_of(heads, k) for k in keys])
        for x in ("released", "eci"):
            if any(getattr(row, x) is not None for row in models if row.id in {k.model for k in keys}):
                file = f"{base}-trend-{x}.svg"
                draw = lambda path, x=x: trend_plot(heads_here, models, x, path, eci_read_on=eci_read_on)  # noqa: E731
                jobs.append((file, title, draw))
                files.append(file)
    return ["Plots: " + ", ".join(f"[{f}]({name}/{f})" for f in files), ""]
