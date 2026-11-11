"""AT12 to AT19 and AY3: the results page's weakest trait, public gap, marks, spread, flags, dry runs, file names and cells.

See docs/specs/analysis/tests.md#tables.
"""

import re
from datetime import date

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from inspect_ai.log import read_eval_log

from paranoid.analysis import (
    load_recognition,
    load_runs,
    mean_over_epochs,
    public_gap,
    result_key,
    scenario_scores,
    spread,
    write_results,
)
from paranoid.analysis.names import markdown_table
from paranoid.engine import SCENARIOS

HEADER = ["Model", "No change", "One shock", "Down switch", "Up switch", "Shock then switch", "Slow drift"]
HEADER += ["Switch then shock", "Up switch then down switch", "Headline", "Weakest trait", "Tools"]


def tables(text: str, heading: str | None = None) -> list[list[dict[str, str]]]:
    """Every markdown table on the page, or under one heading until the next of its level, as rows of dicts."""
    if heading is not None:
        level = heading.split(" ")[0]
        start = text.index(heading + "\n")
        rest = text[start + len(heading) :]
        stop = re.search(rf"^{level} ", rest, re.M)
        text = rest[: stop.start()] if stop else rest
    found, block = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            block.append([cell.strip() for cell in line.strip("|").split("|")])
        elif block:
            found.append([dict(zip(block[0], row)) for row in block[2:]])
            block = []
    return found


def page(runs, out, name="t", **kwargs) -> str:
    write_results(runs, out, name, **kwargs)
    return (out / f"{name}.md").read_text()


CROSS = ("Sensitivity", "Public gap", "Skin sensitivity", "Noise threshold, ")


def headings(text: str) -> list[str]:
    """The setting sections' headings, without the cross setting tables after them."""
    return [h for h in re.findall(r"^## (.+)$", text, re.M) if not h.startswith(CROSS)]


def key_of(path):
    return result_key(read_eval_log(str(path)))


def number(text: str) -> float:
    return float(text.replace("−", "-"))


def cell(text: str) -> tuple[float, float, float]:
    """`0.76 [0.71, 0.80] †` as its three numbers."""
    score, lo, hi = re.match(r"(\S+) \[(\S+), (\S+)\]", text).groups()
    return number(score), number(lo), number(hi)


def test_at12_the_weakest_trait(logs, tmp_path):
    text = page(load_runs([logs.folder]), tmp_path / "out")
    for row in tables(text, "## example, public, rounds 20, tools none")[0]:
        scores = {column: cell(row[column]) for column in HEADER[1:9]}
        lowest = min(scores, key=lambda c: round(scores[c][0], 2))
        trait = row["Weakest trait"].split(" ")[0]
        assert row["Weakest trait"] == f"{trait} {row[lowest].split(' †')[0]}"
        assert scores[lowest][0] == min(s[0] for s in scores.values())


def held_out_copy(log):
    for sample in log.samples:
        sample.metadata["seed_set"] = "held-out"
        sample.metadata.pop("seed", None)


def test_at13_the_public_gap_table(logs, tmp_path, helpers):
    held = helpers.edit(logs.complacent, tmp_path / "held.eval", held_out_copy)
    runs = load_runs([logs.complacent, held])
    (row,) = tables(page(runs, tmp_path / "out"), "## Public gap")[0]
    gap = public_gap(mean_over_epochs(runs), key_of(logs.complacent)).set_index("pair")
    for scenario, column in zip([*SCENARIOS, "headline"], HEADER[1:10]):
        assert cell(row[column]) == pytest.approx(tuple(gap.loc[scenario, ["diff", "lo", "hi"]]), abs=0.005)
    assert "## Public gap" not in page(load_runs([logs.complacent]), tmp_path / "alone")


def test_at14_marks_and_spread(logs, epochs_log, tmp_path):
    runs = load_runs([logs.folder])
    text = page(runs, tmp_path / "out")
    title = "## example, public, rounds 20, tools none"
    marks = tables(text, title)[1]
    scores = scenario_scores(mean_over_epochs(runs))
    mark = scores[scores["model"] == "baseline/complacent"].set_index("scenario")["complacent"]
    for row, scenario in zip(marks, SCENARIOS):
        assert number(row["Complacent"]) == pytest.approx(mark[scenario], abs=0.005)
    spreads = tables(text, title)[2]
    expected = spread(mean_over_epochs(runs))
    expected["label"] = expected["model"] + expected["reasoning"].map(lambda r: "" if r == "n/a" else f" ({r})")
    sd = {(row.label, row.scenario): row.sd for row in expected.itertuples()}
    names = {name: scenario for scenario, name in zip(SCENARIOS, HEADER[1:9])}
    assert len(spreads) == len(expected) and "Sampling share" not in spreads[0]
    for row in spreads:
        assert row["SD"] == f"{sd[(row['Model'], names[row['Scenario']])]:.2f}".replace("-", "−")
    two = page(load_runs([epochs_log]), tmp_path / "two")
    assert "Sampling share" in tables(two, "## example, public, rounds 20, tools none")[2][0]


def test_at15_one_flag_at_a_time(logs, tmp_path, helpers):
    retried = helpers.edit(logs.mockllm, tmp_path / "retried.eval", lambda log: helpers.set_score(log, retry_rounds=4))
    legends = {"‡": page(load_runs([retried]), tmp_path / "a")}
    for flag, row in (("§", ("round_1", 1, None)), ("¶", ("canary", 0, 1))):
        csv = tmp_path / f"{flag}.csv"
        rows = [("mockllm/model", "example", *row[:1], "reply", *row[1:])]
        pd.DataFrame(rows, columns=["model", "skin", "probe", "reply", "lint_hits", "canary_finished"]).to_csv(csv, index=False)
        legends[flag] = page(load_runs([logs.mockllm]), tmp_path / flag, recognition=load_recognition(csv))
    words = {"‡": "‡ Retry share over 0.1.", "§": "§ Recognised the prompt", "¶": "¶ Finished the canary"}
    for flag, text in legends.items():
        legend = [line for line in text.splitlines() if line.startswith(("†", "‡", "§", "¶"))]
        assert len(legend) == 1 and legend[0].startswith(words[flag]), flag
        assert all(other not in legend[0] for other in words if other != flag)


def test_at16_dry_runs_and_the_eci_date(logs, tmp_path, models_file):
    runs = load_runs([logs.folder])
    would = write_results(runs, tmp_path / "dry", "t", plots=True, dry_run=True)
    assert not (tmp_path / "dry").exists()
    assert write_results(runs, tmp_path / "dry", "t", plots=True) == would and all(path.exists() for path in would)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    eci = models_file(tmp_path / "a", {"id": "mockllm/model", "kind": "llm", "reasoning": "off", "eci": 120.5})
    with pytest.raises(ValueError, match="eci-read-on"):
        write_results(runs, tmp_path / "eci", "t", plots=True, models=eci)
    assert not (tmp_path / "eci").exists()
    plain = models_file(tmp_path / "b", {"id": "mockllm/model", "kind": "llm", "reasoning": "off"})
    paths = write_results(runs, tmp_path / "no-eci", "t", plots=True, models=plain)
    assert not any(path.name.endswith("-trend-eci.svg") for path in paths)
    paths = write_results(runs, tmp_path / "with-eci", "t", plots=True, models=eci, eci_read_on=date(2026, 11, 1))
    assert any(path.name.endswith("-trend-eci.svg") for path in paths)


def test_at17_rows_that_differ_in_harness_version_alone(logs, tmp_path, helpers):
    other = helpers.edit(
        logs.mockllm, tmp_path / "a" / "other.eval", lambda log: helpers.set_metadata(log, harness_version="9.9.9")
    )
    version = read_eval_log(str(logs.mockllm)).samples[0].metadata["harness_version"]
    text = page(load_runs([logs.mockllm, other]), tmp_path / "out")
    (title,) = headings(text)
    models = sorted(r["Model"] for r in tables(text, f"## {title}")[0])
    assert models == sorted([f"mockllm/model (off) at {version}", "mockllm/model (off) at 9.9.9"])
    assert f"harness version {', '.join(sorted([version, '9.9.9']))}." in text

    def high(log):
        log.eval.metadata = {"reasoning": "high", "kind": "llm"}

    raised = helpers.edit(logs.mockllm, tmp_path / "b" / "high.eval", high)
    paths = write_results(load_runs([logs.mockllm, raised]), tmp_path / "plots", "t", plots=True)
    strips = sorted(path.name for path in paths if "-strip-" in path.name)
    assert len(strips) == 2 and strips[0] != strips[1]


@pytest.fixture(scope="module")
def mock_runs(logs):
    return load_runs([logs.mockllm])


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    model=st.from_regex(r"[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,20}", fullmatch=True).filter(lambda m: ".." not in m),
    skin=st.from_regex(r"[a-z][a-z0-9_]{0,10}", fullmatch=True),
)
def test_ay3_every_file_name_stays_under_out(mock_runs, tmp_path_factory, model, skin):
    runs = mock_runs.copy()
    runs["model"] = pd.array([model] * len(runs), dtype="str")
    runs["skin"] = pd.array([skin] * len(runs), dtype="str")
    out = tmp_path_factory.mktemp("ay3") / "out"
    for path in write_results(runs, out, "t", plots=True, dry_run=True):
        assert path.resolve().is_relative_to(out.resolve())


def lopsided(errored: int | None = None):
    """Down switch's Complacent mark held by seed 0 alone, so a lost seed moves it, and seed `errored` errored."""

    def change(log):
        for sample in log.samples:
            if sample.metadata["scenario"] == "down_switch":
                value, index = sample.scores["gain"].value, sample.metadata["seed_index"]
                value["complacent"] = value["discerning"] if index == 0 else value["uniform"]
                sample.scores = None if index == errored else sample.scores

    return change


def test_at18_an_errored_seed_keeps_its_mark(logs, tmp_path, helpers):
    helpers.edit(logs.complacent, tmp_path / "logs" / "a.eval", lopsided(errored=0))
    helpers.edit(logs.uniform, tmp_path / "logs" / "b.eval", lopsided(errored=1))
    marks = tables(page(load_runs([tmp_path / "logs"]), tmp_path / "out"), "## example, public, rounds 20, tools none")[1]
    whole = helpers.edit(logs.complacent, tmp_path / "whole.eval", lopsided())
    mark = scenario_scores(mean_over_epochs(load_runs([whole]))).set_index("scenario")["complacent"]
    assert 0.1 < mark["down_switch"] < 0.4
    for row, scenario in zip(marks, SCENARIOS):
        assert number(row["Complacent"]) == pytest.approx(mark[scenario], abs=0.005), scenario


def test_at19_a_cell_never_breaks_its_table():
    lines = markdown_table(["a", "b"], [["x|y", "one\ntwo"], ["plain", "cell"]])
    assert lines[2] == "| x\\|y | one two |"
    assert len({len(re.findall(r"(?<!\\)\|", line)) for line in lines}) == 1
