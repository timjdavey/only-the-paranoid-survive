"""AR8 and AR10 to AR15: the guards on a log and the fields read from it.

See docs/specs/analysis/tests.md#runs.
"""

import pytest
from inspect_ai.log import read_eval_log
from inspect_ai.model import ModelUsage

from paranoid.analysis import headlines, load_runs, mean_over_epochs, result_key, scenario_scores


def first_sample(**values):
    def change(log):
        log.samples[0].metadata |= values

    return change


def every_sample(**values):
    def change(log):
        for sample in log.samples:
            sample.metadata |= values

    return change


def model(name):
    def change(log):
        log.eval.model = name

    return change


@pytest.mark.parametrize(
    "change, field",
    [
        (first_sample(scenario="nope"), "scenario"),
        (every_sample(skin="Rome"), "skin"),
        (model("a/../b"), "model"),
        (model("a/b c"), "model"),
        (every_sample(seed_set="private"), "seed_set"),
        (first_sample(seed_index=-1), "seed_index"),
        (first_sample(tools="notes"), "tools"),
        (every_sample(tool_choice="maybe"), "tool_choice"),
    ],
)
def test_ar8_guards(logs, tmp_path, helpers, change, field):
    path = helpers.edit(logs.uniform, tmp_path / "guarded.eval", change)
    with pytest.raises(ValueError, match=rf"guarded.eval.*{field}"):
        load_runs([path])


def usage(read, write):
    def change(log):
        for sample in log.samples:
            sample.model_usage = {"m": ModelUsage(input_tokens=100, input_tokens_cache_read=read, input_tokens_cache_write=write)}

    return change


def test_ar10_cached_tokens(logs, tmp_path, helpers):
    runs = load_runs([helpers.edit(logs.mockllm, tmp_path / "a" / "cached.eval", usage(300, 50))])
    assert (runs["cache_read_tokens"] == 300).all() and (runs["cache_write_tokens"] == 50).all()
    runs = load_runs([helpers.edit(logs.mockllm, tmp_path / "b" / "none.eval", usage(None, None))])
    assert (runs["cache_read_tokens"] == 0).all() and (runs["cache_write_tokens"] == 0).all()


def test_ar11_game_rounds_and_rounds(logs, tmp_path, helpers):
    path = helpers.edit(
        logs.mockllm,
        tmp_path / "gave-up.eval",
        lambda log: helpers.set_score(log, lambda s: s.id == log.samples[0].id, gave_up=1, rounds=3, gain=0.0, run_score=0.0),
    )
    runs = load_runs([path])
    row = runs[runs["gave_up"]].iloc[0]
    assert row["game_rounds"] == 20 and row["rounds"] == 3
    log = read_eval_log(str(logs.mockllm))
    released = log.model_copy(deep=True)
    every_sample(release="r1")(released)
    assert result_key(released) != result_key(log)


def test_ar12_the_metric_check(logs, tmp_path, helpers):
    def tamper(log):
        log.samples[0].scores["gain"].value["gain"] += 50

    scenario = read_eval_log(str(logs.mockllm)).samples[0].metadata["scenario"]
    path = helpers.edit(logs.mockllm, tmp_path / "a" / "tampered.eval", tamper, results=True)
    with pytest.raises(ValueError, match=rf"tampered.eval.*{scenario}"):
        load_runs([path])
    assert len(load_runs([helpers.edit(logs.mockllm, tmp_path / "b" / "tampered.eval", tamper)])) == 40
    assert load_runs([logs.folder]).attrs["report"]["checked"] == 4


def test_ar13_tool_choice_from_the_samples_that_hold_it(logs, tmp_path, helpers):
    def drop_one(log):
        del log.samples[0].metadata["tool_choice"]
        log.samples[0].scores = None

    runs = load_runs([helpers.edit(logs.mockllm, tmp_path / "a" / "one.eval", drop_one)])
    assert (runs["tool_choice"] == "any").all()

    def drop_all(log):
        for sample in log.samples:
            del sample.metadata["tool_choice"]

    log = read_eval_log(str(logs.mockllm))
    drop_all(log)
    assert result_key(log).setting.tool_choice is None

    def drop_skin(log):
        del log.samples[0].metadata["skin"]

    with pytest.raises(ValueError, match="skin"):
        load_runs([helpers.edit(logs.mockllm, tmp_path / "c" / "skinless.eval", drop_skin)])


def test_ar14_na_keys_lose_no_row(logs):
    runs = mean_over_epochs(load_runs([logs.folder]))
    assert runs["own_scale"].isna().all() and runs["warm_up"].isna().all() and runs["inertia"].isna().all()
    assert len(runs) == 160
    assert len(scenario_scores(runs)) == 4 * 8 and len(headlines(runs)) == 4


def test_ar15_harness_version_splits_rows(logs, tmp_path, helpers):
    helpers.edit(logs.complacent, tmp_path / "a.eval")
    helpers.edit(logs.complacent, tmp_path / "b.eval", every_sample(harness_version="0.2.0"))
    runs = load_runs([tmp_path])
    assert len(runs) == 80 and runs["harness_version"].nunique() == 2
    assert len(headlines(mean_over_epochs(runs))) == 2
