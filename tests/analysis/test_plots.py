"""AP1 to AP3: the four plots. See docs/specs/analysis/tests.md#plots."""

import xml.etree.ElementTree as ElementTree
from datetime import date

import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import headlines, load_runs, mean_over_epochs, noise_plot, noise_threshold, profile_plot
from paranoid.analysis import result_key, scenario_scores, strip_plot, trend_plot
from paranoid.harness import load_models

SCALES = (1.0, 2.0, 4.0, 8.0)


@pytest.fixture(scope="module")
def runs(logs):
    return mean_over_epochs(load_runs([logs.folder]))


@pytest.fixture(scope="module")
def mock(logs):
    return result_key(read_eval_log(str(logs.mockllm)))


def models(tmp_path, models_file, eci=True):
    rows = [
        {"id": "baseline/uniform", "kind": "baseline", "reasoning": "n/a"},
        {"id": "mockllm/model", "kind": "llm", "reasoning": "off", "released": "2026-01-01"} | ({"eci": 120.5} if eci else {}),
    ]
    path = models_file(tmp_path, *rows)
    path.write_text(path.read_text().replace('"2026-01-01"', "2026-01-01"))  # a TOML date, not a string
    return load_models(path)


def curve(logs, tmp_path, helpers):
    folder = tmp_path / "curve"
    for scale, headline in zip(SCALES, (0.95, 0.9, 0.7, 0.6)):
        helpers.edit(logs.complacent, folder / f"{scale}.eval", helpers.on_curve(headline, 0.55, scale, 0.1))
    runs = mean_over_epochs(load_runs([folder]))
    key = result_key(read_eval_log(str(folder / "1.0.eval")))
    return runs, noise_threshold(runs, key)


def draw_all(runs, mock, logs, tmp_path, helpers, models_file, out):
    curve_runs, threshold = curve(logs, tmp_path, helpers)
    return [
        strip_plot(runs, mock, out / "strip.svg"),
        profile_plot(scenario_scores(runs), out / "profile.svg"),
        trend_plot(headlines(runs), models(tmp_path, models_file), "eci", out / "eci.svg", eci_read_on=date(2026, 11, 1)),
        noise_plot(curve_runs, [threshold], out / "noise.svg"),
    ]


def test_ap1_every_plot_is_svg_and_stable(runs, mock, logs, tmp_path, helpers, models_file):
    first = draw_all(runs, mock, logs, tmp_path / "a", helpers, models_file, tmp_path / "one")
    second = draw_all(runs, mock, logs, tmp_path / "b", helpers, models_file, tmp_path / "two")
    for a, b in zip(first, second):
        ElementTree.parse(a)
        assert a.read_bytes() == b.read_bytes(), a.name


def test_ap2_credit_and_title(runs, mock, tmp_path, models_file):
    path = trend_plot(headlines(runs), models(tmp_path, models_file), "eci", tmp_path / "eci.svg", eci_read_on=date(2026, 11, 1))
    text = path.read_text()
    assert "Epoch AI" in text and "CC BY 4.0" in text and "2026-11-01" in text
    strip = strip_plot(runs, mock, tmp_path / "strip.svg").read_text()
    assert "example, public, rounds 20, tools none" in strip
    seeds = runs[runs["model"] == "mockllm/model"]["seed"].dropna().astype(int)
    assert not any(f"seed {seed}" in strip for seed in seeds)


def test_ap3_eci_needs_a_date_and_names_who_has_none(runs, tmp_path, models_file):
    rows = models(tmp_path, models_file, eci=False)
    with pytest.raises(ValueError, match="eci_read_on"):
        trend_plot(headlines(runs), rows, "eci", tmp_path / "eci.svg")
    text = trend_plot(headlines(runs), rows, "eci", tmp_path / "eci.svg", eci_read_on=date(2026, 11, 1)).read_text()
    assert "No eci: mockllm/model (off)" in text
