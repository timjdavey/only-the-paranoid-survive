"""AT2, AT6 and AY1: the run CSV and the cost table. See docs/specs/analysis/tests.md#tables.

AT5 and AT11, which hold the CSV against the page, are in test_tables.py.
"""

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from inspect_ai.log import read_eval_log
from inspect_ai.model import ModelUsage

from paranoid.analysis import CSV_COLUMNS, RUN_COLUMNS, load_runs, mean_over_epochs, paired_gap, result_key
from paranoid.analysis import scenario_scores, write_cost, write_run_csv
from paranoid.harness import pooled_score

COST = ["model", "reasoning", "kind", "skin", "runs", "input", "cache_read", "cache_write", "output", "reasoning_tokens"]
COST += ["cached_share", "cut_off_share", "projected"]


def test_at2_the_run_csv(logs, held_out, tmp_path):
    runs = mean_over_epochs(load_runs([logs.folder, held_out]))
    path = tmp_path / "t.csv"
    write_run_csv(runs, path)
    csv = pd.read_csv(path, keep_default_na=False, dtype=str)
    assert tuple(csv.columns) == CSV_COLUMNS and set(CSV_COLUMNS) <= set(RUN_COLUMNS) and "output" not in csv
    assert len(csv) == len(runs)
    assert (csv[csv["seed_set"] == "public"]["seed"] != "").all() and (csv[csv["seed_set"] == "held-out"]["seed"] == "").all()
    for seed in (731904516, 482019377, 905177263):
        assert str(seed) not in path.read_text()


def usage(input_tokens, read, write):
    def change(log):
        for sample in log.samples:
            sample.model_usage = {"m": ModelUsage(input_tokens=input_tokens, input_tokens_cache_read=read,
                                                  input_tokens_cache_write=write, output_tokens=10)}  # fmt: skip

    return change


def test_at6_cost(logs, epochs_log, tmp_path, helpers, models_file, capsys):
    runs = load_runs([logs.folder])
    table = write_cost(runs)
    assert list(table.columns) == COST and "cost" not in table
    baseline = table[table["model"] == "baseline/uniform"].iloc[0]
    assert baseline["input"] == baseline["output"] == 0 and baseline["skin"] == "example"
    models = models_file(tmp_path, {"id": "mockllm/model", "kind": "llm", "reasoning": ["off", "low"]})
    projected = write_cost(runs, models=models, seeds=10).set_index("model")
    assert projected.loc["mockllm/model", "projected"] == pytest.approx(
        sum(projected.loc["mockllm/model", k] for k in ("input", "cache_read", "cache_write", "output")) * 10 * 8 * 2)
    assert projected["projected"].isna().sum() == 3
    cached = load_runs([helpers.edit(logs.mockllm, tmp_path / "a" / "cached.eval", usage(100, 300, 0))])
    prices = tmp_path / "prices.toml"
    prices.write_text('read_on = "2026-11-01"\n[[price]]\nid = "mockllm/model"\ninput = 3.0\noutput = 15.0\ncache_read = 0.3\n')
    full = tmp_path / "full.toml"
    full.write_text('[[price]]\nid = "mockllm/model"\ninput = 3.0\noutput = 15.0\n')
    with_read = write_cost(cached, models=models, seeds=10, prices=prices).iloc[0]
    without = write_cost(cached, models=models, seeds=10, prices=full).iloc[0]
    assert with_read["cached_share"] == 0.75 and with_read["cost"] < without["cost"]
    assert write_cost(cached, models=models, seeds=10, prices=prices).attrs["read_on"] == "2026-11-01"
    two = load_runs([helpers.edit(epochs_log, tmp_path / "b" / "two.eval", usage(100, 0, 0))])
    (row,) = write_cost(two).itertuples()
    assert row.runs == 20 and row.input == 100
    assert capsys.readouterr().out == ""


@pytest.fixture(scope="module")
def base(logs):
    return mean_over_epochs(load_runs([logs.mockllm])), result_key(read_eval_log(str(logs.mockllm)))


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data())
def test_ay1_the_csv_pools_to_the_page(base, tmp_path_factory, data):
    runs, key = base
    two = runs[runs["scenario"].isin(["one_shock", "down_switch"])].copy()
    n = len(two)
    gaps = data.draw(st.lists(st.floats(1.0, 1000.0), min_size=n, max_size=n))
    gains = data.draw(st.lists(st.floats(-1000.0, 1000.0), min_size=n, max_size=n))
    two["gap"], two["gain"] = gaps, gains
    two["run_score"] = two["gain"] / two["gap"]
    path = tmp_path_factory.mktemp("ay1") / "t.csv"
    write_run_csv(two, path)
    csv = pd.read_csv(path)
    scores = scenario_scores(two).set_index("scenario")
    for scenario, rows in csv.groupby("scenario"):
        assert pooled_score(rows["gain"], rows["gap"]) == pytest.approx(scores.loc[scenario, "score"], rel=1e-12)
    assert (paired_gap(two, key, key)[["diff", "lo", "hi"]] == 0).all().all()
