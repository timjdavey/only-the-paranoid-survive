"""AT1, AT3 to AT5 and AT7 to AT11: the results page. See docs/specs/analysis/tests.md#tables.

AT2 and AT6, on the CSV and cost alone, are in test_csv_cost.py. AT12 to AT17 and AY3 are in test_tables_marks.py.
"""

import re
import tomllib
from pathlib import Path

import pandas as pd
import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import (
    CSV_COLUMNS,
    load_recognition,
    load_runs,
    mean_over_epochs,
    noise_threshold,
    paired_gap,
    result_key,
    write_results,
)
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
    models = models_file(
        tmp_path,
        {"id": "mockllm/model", "kind": "llm", "reasoning": "off"},
        *({"id": f"baseline/{n}", "kind": "baseline", "reasoning": "n/a"} for n in ("uniform", "discerning", "complacent")),
    )
    text = page(load_runs([logs.folder]), tmp_path / "out", models=models)
    assert text.startswith("# Results: t\n")
    version = read_eval_log(str(logs.uniform)).samples[0].metadata["harness_version"]
    assert f"from 4 logs at harness version {version} on " in text
    (rows,) = tables(text, "## example, public, rounds 20, tools none")[:1]
    assert list(rows[0]) == HEADER
    assert [r["Model"] for r in rows] == ["baseline/uniform", "baseline/discerning", "baseline/complacent", "mockllm/model (off)"]
    first = read_eval_log(str(logs.mockllm)).samples[0]
    gave_up = helpers.edit(
        logs.mockllm,
        tmp_path / "gave-up.eval",
        lambda log: helpers.set_score(log, lambda s: s.id == first.id, gave_up=1, gain=0.0, run_score=0.0),
    )
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
    pd.DataFrame(
        [("baseline/complacent", "example", "round_1", reply, 1, None)],
        columns=["model", "skin", "probe", "reply", "lint_hits", "canary_finished"],
    ).to_csv(csv, index=False)
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
    assert headings(text) == [
        "example, public, rounds 20, tools none, release dev",
        "example, public, rounds 20, tools none, release r1",
    ]
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
    moved = helpers.edit(
        b,
        tmp_path / "moved" / "b.eval",
        lambda log: helpers.set_score(log, lambda s: s.metadata["seed_index"] == 0, gain=0.0, run_score=0.0),
    )
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
    curve_logs(
        logs.mockllm, folder, helpers, scales=[1.0, 2.0], prefix="mock-"
    )  # a second model with two settings beside the first's four
    text = page(load_runs([folder]), tmp_path / "two")
    rows = tables(text, f"## {title}")[0]
    assert [r["Model"] for r in rows] == ["baseline/complacent"]
    assert "mockllm/model (off) has 2 noise settings" in text


def test_at11_the_csv_groups_to_the_sections(logs, tmp_path, helpers):
    tooled = helpers.edit(logs.mockllm, tmp_path / "a" / "tooled.eval", with_tools)
    out = tmp_path / "out"
    text = page(load_runs([logs.mockllm, tooled]), out)
    csv = pd.read_csv(out / "t.csv", keep_default_na=False, dtype=str)
    setting = [
        "model",
        "reasoning",
        "skin",
        "seed_set",
        "own_scale",
        "game_rounds",
        "tools",
        "warm_up",
        "rolling",
        "tool_choice",
        "inertia",
        "prompt_hash",
        "generator_version",
        "harness_version",
        "release",
    ]
    assert set(setting) <= set(CSV_COLUMNS)
    groups = csv.groupby(setting)
    assert len(groups) == 2 == len(headings(text))
    for (_, group), title in zip(sorted(groups, key=lambda g: g[0][6] == "none"), headings(text)):
        assert len(group) == 40 and (group["tools"].iloc[0] == "none") == title.endswith("tools none")
    released = helpers.edit(logs.mockllm, tmp_path / "b" / "r1.eval", lambda log: helpers.set_metadata(log, release="r1"))
    assert len(headings(page(load_runs([logs.mockllm, released]), tmp_path / "two"))) == 2
