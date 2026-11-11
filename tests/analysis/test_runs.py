"""AR1 to AR7 and AR9: the run table. See docs/specs/analysis/tests.md#runs."""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import RUN_COLUMNS, load_runs, mean_over_epochs, result_key, scenario_scores
from paranoid.harness import BUDGETS

DTYPES = {
    "str": [
        "log",
        "model",
        "reasoning",
        "skin",
        "seed_set",
        "tools",
        "warm_up",
        "tool_choice",
        "prompt_hash",
        "harness_version",
        "release",
        "kind",
        "scenario",
        "engine_hash",
        "numpy_version",
    ],
    "Int64": [
        "game_rounds",
        "inertia",
        "generator_version",
        "seed_index",
        "seed",
        "epoch",
        "epochs",
        "input_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "output_tokens",
        "reasoning_tokens",
        "total_tokens",
        "rounds",
        "warm_up_rounds",
        "retries",
        "retry_rounds",
        "bad_calls",
        "no_calls",
        "cut_offs",
        "notes_rounds",
        "compute_rounds",
        "unchanged_rounds",
        "sleeper_round",
    ],
    "float64": [
        "own_scale",
        "output",
        "uniform",
        "discerning",
        "complacent",
        "perfect",
        "hedge_rule",
        "scout_rule",
        "gain",
        "gap",
        "run_score",
        "explore_points",
        "warm_up_kept",
    ],
    "boolean": ["rolling", "gave_up", "errored"],
}
SCORES = ["output", "gain", "gap", "run_score", "rounds", "input_tokens"]


def keep(ids):
    def change(log):
        log.samples = [s for s in log.samples if s.id in ids]

    return change


def started(minutes: int):
    def change(log):
        log.eval.created = (datetime(2026, 11, 11, 12) + timedelta(minutes=minutes)).isoformat() + "+00:00"

    return change


def both(*changes):
    def change(log):
        for one in changes:
            one(log)

    return change


def ids_of(path) -> list[str]:
    return [s.id for s in read_eval_log(str(path)).samples]


def test_ar1_the_run_table(logs):
    runs = load_runs([logs.folder])
    assert tuple(runs.columns) == RUN_COLUMNS and len(RUN_COLUMNS) == len(set(RUN_COLUMNS))
    for dtype, columns in DTYPES.items():
        for column in columns:
            assert str(runs[column].dtype) == dtype, column
    assert str(runs["started"].dtype).startswith("datetime64") and str(runs["started"].dt.tz) == "UTC"
    assert len(runs) == 4 * 40 and (runs["epoch"] == 1).all()
    assert (runs["run_score"] - runs["gain"] / runs["gap"]).abs().max() < 1e-12
    averaged = mean_over_epochs(runs)
    assert tuple(averaged.columns) == tuple(c for c in RUN_COLUMNS if c != "epoch")
    pd.testing.assert_frame_equal(averaged, runs.drop(columns="epoch"))


def test_ar2_held_out_seeds_never_load(held_out, tmp_path, helpers):
    runs = load_runs([held_out])
    assert runs["seed"].isna().all() and (runs["seed_set"] == "held-out").all()
    text = runs.to_string() + runs.to_csv()
    for seed in (731904516, 482019377, 905177263):
        assert str(seed) not in text

    def plant(log):
        log.samples[1].metadata["seed"] = 1

    planted = helpers.edit(held_out, tmp_path / "planted.eval", plant)
    with pytest.raises(ValueError, match=rf"planted.eval.*{read_eval_log(str(planted)).samples[1].id}"):
        load_runs([planted])


def test_ar3_duplicates(logs, tmp_path, helpers):
    ids = ids_of(logs.complacent)
    folder = tmp_path / "cover"
    helpers.edit(logs.complacent, folder / "a.eval", both(keep(ids[:5]), started(0)))
    helpers.edit(logs.complacent, folder / "b.eval", both(keep(ids[:6]), started(1)))
    runs = load_runs([folder])
    assert set(runs["log"]) == {"b.eval"} and len(runs) == 6
    assert runs.attrs["report"]["dropped"] == [("a.eval", "b.eval")]
    clash = tmp_path / "clash"
    helpers.edit(logs.complacent, clash / "a.eval", both(keep(ids[:5]), started(0)))
    helpers.edit(logs.complacent, clash / "b.eval", both(keep(ids[3:8]), started(1)))
    with pytest.raises(ValueError, match="a.eval.*b.eval"):
        load_runs([clash])
    apart = tmp_path / "apart"
    helpers.edit(logs.complacent, apart / "a.eval", both(keep(ids[:5]), started(0)))
    helpers.edit(logs.complacent, apart / "b.eval", both(keep(ids[5:10]), started(1)))
    assert len(load_runs([apart])) == 10
    tie = tmp_path / "tie"
    helpers.edit(logs.complacent, tie / "a.eval", both(keep(ids[:5]), started(0)))
    helpers.edit(logs.complacent, tie / "b.eval", both(keep(ids[:5]), started(0)))
    assert set(load_runs([tie])["log"]) == {"b.eval"}


def test_ar4_reasoning(logs):
    mock, uniform = read_eval_log(str(logs.mockllm)), read_eval_log(str(logs.uniform))
    assert result_key(mock).reasoning == "off"

    def reasoning(metadata=None, **config):
        log = mock.model_copy(deep=True)
        log.eval.metadata = metadata
        log.eval.model_generate_config = log.eval.model_generate_config.model_copy(update=config)
        return result_key(log).reasoning

    assert reasoning({"reasoning": "low"}) == "low"
    assert reasoning(reasoning_effort="high") == "high"
    assert reasoning(reasoning_tokens=BUDGETS["medium"]) == "medium"
    assert reasoning(reasoning_effort="none") == "off"
    for config in ({"reasoning_tokens": 0}, {"reasoning_tokens": 5}, {}):
        assert reasoning(**config) == "unknown"
    uniform.eval.metadata = None
    assert result_key(uniform).reasoning == "n/a"


def test_ar5_an_errored_sample(logs, tmp_path, helpers):
    def error_one(log):
        log.samples[0].scores = None

    path = helpers.edit(logs.mockllm, tmp_path / "errored.eval", error_one)
    runs = load_runs([path])
    errored = runs[runs["errored"]]
    assert len(errored) == 1 and errored[SCORES].isna().all().all()
    assert runs.attrs["report"]["errored"] == [("errored.eval", 1)]
    scores = scenario_scores(mean_over_epochs(runs))
    scenario = errored["scenario"].iloc[0]
    assert scores.set_index("scenario").loc[scenario, "n"] == 4


def test_ar6_epochs(epochs_log, tmp_path, helpers):
    runs = load_runs([epochs_log])
    assert sorted(runs.groupby(["scenario", "seed_index"]).size().unique()) == [2]
    assert set(runs["epoch"]) == {1, 2}

    def vary(log):
        first = {}
        for sample in log.samples:
            value = sample.scores["gain"].value
            if sample.epoch == 2:
                value["run_score"] = value["run_score"] / 2
                value["gave_up"] = 1 if sample.id == log.samples[0].id else 0
            sleeper = {"one_shock": (0, 0), "up_switch": (0, 7)}[sample.metadata["scenario"]]
            value["sleeper_round"] = sleeper[sample.epoch - 1]
            value["explore_points"] = 2.0 if sample.epoch == 1 else None
            first.setdefault(sample.id, value)

    path = helpers.edit(epochs_log, tmp_path / "varied.eval", vary)
    varied = load_runs([path])
    averaged = mean_over_epochs(varied)
    assert len(averaged) == 10 and (averaged["epochs"] == 2).all() and "epoch" not in averaged
    for (_, sample), row in zip(varied.groupby(["scenario", "seed_index"], sort=False), averaged.itertuples()):
        assert row.run_score == pytest.approx(sample["run_score"].mean())
        assert row.rounds == sample["rounds"].sum()
        assert row.gave_up == sample["gave_up"].any()
        assert row.sleeper_round == (7 if row.scenario == "up_switch" else 0)
        assert row.explore_points == 2.0
    assert averaged["gave_up"].sum() == 1


def test_ar7_what_is_not_a_paranoid_log(logs, tmp_path, helpers):
    def other(log):
        log.eval.task = "other/task"

    helpers.edit(logs.uniform, tmp_path / "mixed" / "other.eval", other)
    helpers.edit(logs.uniform, tmp_path / "mixed" / "mine.eval")
    runs = load_runs([tmp_path / "mixed"])
    assert set(runs["log"]) == {"mine.eval"} and runs.attrs["report"]["skipped"] == ["other.eval"]
    (tmp_path / "junk").mkdir()
    (tmp_path / "junk" / "junk.eval").write_text("not a log")
    with pytest.raises(ValueError, match="junk.eval"):
        load_runs([tmp_path / "junk"])


def test_ar9_mixed_numpy(logs, tmp_path, helpers):
    ids = ids_of(logs.uniform)

    def newer(log):
        keep(ids[20:])(log)
        for sample in log.samples:
            sample.metadata["numpy_version"] = "9.9.9"

    helpers.edit(logs.uniform, tmp_path / "a.eval", keep(ids[:20]))
    helpers.edit(logs.uniform, tmp_path / "b.eval", newer)
    runs = load_runs([tmp_path])
    ((row, versions),) = runs.attrs["report"]["numpy"]
    assert "baseline/uniform" in row and versions == sorted([np.__version__, "9.9.9"])
