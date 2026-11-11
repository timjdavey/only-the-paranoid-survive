"""AT1, AT3 to AT5 and AT7 to AT17, and AY3: the results page. See docs/specs/analysis/tests.md#tables.

AT2 and AT6, on the CSV and cost alone, are in test_csv_cost.py.
"""

import re
import tomllib
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from inspect_ai.log import read_eval_log

from paranoid.analysis import CSV_COLUMNS, load_recognition, load_runs, mean_over_epochs, noise_threshold, paired_gap
from paranoid.analysis import public_gap, result_key, scenario_scores, spread, write_results
from paranoid.engine import SCENARIOS
from paranoid.harness import pooled_score

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = tomllib.loads((ROOT / "src" / "paranoid" / "skins" / "example.toml").read_text())
HEADER = ["Model", "No change", "One shock", "Down switch", "Up switch", "Shock then switch", "Slow drift"]
HEADER += ["Switch then shock", "Up switch then down switch", "Headline", "Weakest trait", "Tools"]
BASELINE = {"reasoning": "n/a", "kind": "baseline"}


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


def test_at1_the_scores_table(logs, tmp_path, helpers, models_file):
    models = models_file(tmp_path, {"id": "mockllm/model", "kind": "llm", "reasoning": "off"},
                         *({"id": f"baseline/{n}", "kind": "baseline", "reasoning": "n/a"} for n in ("uniform", "discerning", "complacent")))  # fmt: skip
    text = page(load_runs([logs.folder]), tmp_path / "out", models=models)
    assert text.startswith("# Results: t\n")
    version = read_eval_log(str(logs.uniform)).samples[0].metadata["harness_version"]
    assert f"from 4 logs at harness version {version} on " in text
    (rows,) = tables(text, "## example, public, rounds 20, tools none")[:1]
    assert list(rows[0]) == HEADER
    assert [r["Model"] for r in rows] == ["baseline/uniform", "baseline/discerning", "baseline/complacent", "mockllm/model (off)"]
    first = read_eval_log(str(logs.mockllm)).samples[0]
    gave_up = helpers.edit(logs.mockllm, tmp_path / "gave-up.eval", lambda log: helpers.set_score(
        log, lambda s: s.id == first.id, gave_up=1, gain=0.0, run_score=0.0))  # fmt: skip
    text = page(load_runs([gave_up]), tmp_path / "two")
    assert "† 1 run gave up and scored as the Uniform baseline." in text and "‡" not in text


def test_at3_the_same_bytes(logs, tmp_path):
    runs = load_runs([logs.folder])
    out = tmp_path / "out"
    page(runs, out)
    first = (out / "t.md").read_bytes(), (out / "t.csv").read_bytes()
    with (out / "t.md").open("a") as file:
        file.write("a line by hand\n")
    page(runs, out)
    assert ((out / "t.md").read_bytes(), (out / "t.csv").read_bytes()) == first


def test_at4_nothing_secret_is_written(held_out, tmp_path):
    reply = "THE PLANTED REPLY about Merridew"
    csv = tmp_path / "recognition.csv"
    pd.DataFrame([("baseline/complacent", "example", "round_1", reply, 1, None)],
                 columns=["model", "skin", "probe", "reply", "lint_hits", "canary_finished"]).to_csv(csv, index=False)  # fmt: skip
    out = tmp_path / "out"
    write_results(load_runs([held_out]), out, "t", recognition=load_recognition(csv), plots=True)
    words = EXAMPLE["intro"].split()
    runs_of_five = [" ".join(words[i : i + 5]) for i in range(len(words) - 4)]
    written = [path for path in out.rglob("*") if path.is_file()]
    assert len(written) > 2
    for path in written:
        text = path.read_text()
        for seed in (731904516, 482019377, 905177263):
            assert str(seed) not in text, path
        assert reply not in text and "PLANTED" not in text
        assert not any(channel in text for channel in EXAMPLE["channels"]), path
        assert not any(run in text for run in runs_of_five), path


def with_tools(log):
    for sample in log.samples:
        sample.metadata["tools"] = "notes,compute"
        sample.scores["gain"].value |= {"notes_rounds": 4, "compute_rounds": 0}


def test_at5_the_page_pools_from_the_csv(logs, tmp_path, helpers):
    tooled = helpers.edit(logs.mockllm, tmp_path / "tooled.eval", with_tools)
    out = tmp_path / "out"
    text = page(load_runs([logs.folder, tooled]), out)
    csv = pd.read_csv(out / "t.csv", keep_default_na=False)
    for title in headings(text):
        rows = tables(text, f"## {title}")[0]
        tools = "none" if title.endswith("tools none") else "notes,compute"
        for row in rows:
            model = row["Model"].split(" ")[0]
            mine = csv[(csv["model"] == model) & (csv["tools"] == tools)]
            for scenario, column in zip(SCENARIOS, HEADER[1:9]):
                one = mine[mine["scenario"] == scenario]
                assert f"{pooled_score(one['gain'], one['gap']):.2f}".replace("-", "−") == row[column].split(" ")[0]
            if tools == "notes,compute":
                notes = mine["notes_rounds"].sum() / mine["rounds"].sum()
                assert row["Tools"] == f"notes {notes:.2f}, compute 0.00"


def test_at7_headings(logs, tmp_path, helpers):
    tooled = helpers.edit(logs.mockllm, tmp_path / "a" / "tooled.eval", with_tools)
    text = page(load_runs([logs.mockllm, tooled]), tmp_path / "one")
    assert headings(text) == ["example, public, rounds 20", "example, public, rounds 20, tools none"]
    released = helpers.edit(logs.mockllm, tmp_path / "b" / "r1.eval", lambda log: helpers.set_metadata(log, release="r1"))
    text = page(load_runs([logs.mockllm, released]), tmp_path / "two")
    assert headings(text) == ["example, public, rounds 20, tools none, release dev", "example, public, rounds 20, tools none, release r1"]
    with pytest.raises(ValueError, match="bare file stem"):
        write_results(load_runs([logs.mockllm]), tmp_path / "three", "../x")
    assert not (tmp_path / "three").exists() and not (tmp_path / "x.md").exists()


def test_at8_the_sensitivity_table(logs, tmp_path, helpers):
    tooled = helpers.edit(logs.mockllm, tmp_path / "tooled.eval", lambda log: helpers.set_metadata(log, tools="notes,compute"))
    runs = load_runs([logs.mockllm, tooled])
    text = page(runs, tmp_path / "out")
    (rows,) = tables(text, "## Sensitivity")
    (row,) = rows
    assert row["Knob"] == "tools none" and row["Setting"] == "example, public, rounds 20"
    plain, copy = key_of(logs.mockllm), key_of(tooled)
    head = tables(text, "## example, public, rounds 20, tools none")[0][0]["Headline"]
    assert row["Headline"] == head
    gap = paired_gap(mean_over_epochs(runs), copy, plain).set_index("pair").loc["headline"]
    assert cell(row["Gap"]) == pytest.approx((gap["diff"], gap["lo"], gap["hi"]), abs=0.005)
    assert "## Sensitivity" not in page(load_runs([logs.mockllm]), tmp_path / "alone")


def test_at9_the_skin_sensitivity_table(logs, tmp_path, helpers, monkeypatch):
    skins = tmp_path / "skins"
    skins.mkdir()
    (skins / "b.toml").write_text((ROOT / "src" / "paranoid" / "skins" / "example.toml").read_text())
    monkeypatch.setenv("PARANOID_SKINS", str(skins))
    b = helpers.run("baseline/complacent", tmp_path / "b-logs", metadata=BASELINE, skin="b")
    runs = load_runs([logs.complacent, b])
    text = page(runs, tmp_path / "out")
    assert len([h for h in headings(text) if h.startswith(("example,", "b,"))]) == 2
    (rows,) = tables(text, "## Skin sensitivity")
    (row,) = rows
    assert row["Skins"] == "b − example"
    assert all(cell(row[c])[0] == 0 for c in HEADER[1:10])
    moved = helpers.edit(b, tmp_path / "moved" / "b.eval", lambda log: helpers.set_score(
        log, lambda s: s.metadata["seed_index"] == 0, gain=0.0, run_score=0.0))  # fmt: skip
    runs = load_runs([logs.complacent, moved])
    (row,) = tables(page(runs, tmp_path / "moved-out"), "## Skin sensitivity")[0]
    gap = paired_gap(mean_over_epochs(runs), key_of(moved), key_of(logs.complacent)).set_index("pair")
    for scenario, column in zip([*SCENARIOS, "headline"], HEADER[1:10]):
        assert cell(row[column]) == pytest.approx(tuple(gap.loc[scenario, ["diff", "lo", "hi"]]), abs=0.005)
    assert "## Skin sensitivity" not in page(load_runs([logs.complacent]), tmp_path / "alone")


CURVE = {1.0: 0.95, 2.0: 0.9, 4.0: 0.7, 8.0: 0.6}


def curve_logs(source, folder, helpers, scales=CURVE, prefix=""):
    for scale in scales:
        helpers.edit(source, folder / f"{prefix}{scale}.eval", helpers.on_curve(CURVE[scale], 0.55, scale, 0.1))
    return folder


def test_at10_the_noise_threshold_table(logs, tmp_path, helpers):
    folder = curve_logs(logs.complacent, tmp_path / "curve", helpers)
    runs = load_runs([folder])
    text = page(runs, tmp_path / "out", plots=True)
    (title,) = [h for h in re.findall(r"^## (.+)$", text, re.M) if h.startswith("Noise threshold, ")]
    (row,) = tables(text, f"## {title}")[0]
    found = noise_threshold(mean_over_epochs(runs), key_of(folder / "1.0.eval"))
    assert cell(row["Threshold"]) == pytest.approx((found.snr, found.lo, found.hi), abs=0.05)
    assert row["Settings"] == "4"
    assert (tmp_path / "out" / "t" / "example-public-rounds-20-tools-none-noise.svg").exists()
    curve_logs(logs.mockllm, folder, helpers, scales=[1.0, 2.0], prefix="mock-")  # a second model with two settings beside the first's four
    text = page(load_runs([folder]), tmp_path / "two")
    rows = tables(text, f"## {title}")[0]
    assert [r["Model"] for r in rows] == ["baseline/complacent"]
    assert "mockllm/model (off) has 2 noise settings" in text


def test_at11_the_csv_groups_to_the_sections(logs, tmp_path, helpers):
    tooled = helpers.edit(logs.mockllm, tmp_path / "a" / "tooled.eval", with_tools)
    out = tmp_path / "out"
    text = page(load_runs([logs.mockllm, tooled]), out)
    csv = pd.read_csv(out / "t.csv", keep_default_na=False, dtype=str)
    setting = ["model", "reasoning", "skin", "seed_set", "own_scale", "game_rounds", "tools", "warm_up", "rolling",
               "tool_choice", "inertia", "prompt_hash", "generator_version", "harness_version", "release"]  # fmt: skip
    assert set(setting) <= set(CSV_COLUMNS)
    groups = csv.groupby(setting)
    assert len(groups) == 2 == len(headings(text))
    for (_, group), title in zip(sorted(groups, key=lambda g: g[0][6] == "none"), headings(text)):
        assert len(group) == 40 and (group["tools"].iloc[0] == "none") == title.endswith("tools none")
    released = helpers.edit(logs.mockllm, tmp_path / "b" / "r1.eval", lambda log: helpers.set_metadata(log, release="r1"))
    assert len(headings(page(load_runs([logs.mockllm, released]), tmp_path / "two"))) == 2


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
    other = helpers.edit(logs.mockllm, tmp_path / "a" / "other.eval", lambda log: helpers.set_metadata(log, harness_version="9.9.9"))
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
